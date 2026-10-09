import os
import fitz  # PyMuPDF
import streamlit as st
from google import genai

st.set_page_config(page_title="منصة تدقيق الاختبارات", page_icon="🔬", layout="wide")

st.title("🔬 منصة تدقيق اختبارات العلوم والفيزياء والكيمياء والأحياء")
st.caption("تدقيق تلقائي فوري وفقاً لوثائق التقويم الرسمية لوزارة التربية والتعليم (2026/2027م)")

# جلب المفتاح الأمني
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.info("👈 لبدء استخدام المنصة يرجى إدخال مفتاح Gemini API في Secrets")
    api_key = st.sidebar.text_input("أدخل مفتاح Gemini API:", type="password")

if api_key:
    # تهيئة العميل بالحزمة الحديثة
    client = genai.Client(api_key=api_key)

    # القائمة الجانبية
    st.sidebar.header("⚙️ اختيار المنهج والصف")
    grade = st.sidebar.selectbox("اختر الصف الدراسي:", ["الصف 10", "الصف 11", "الصف 12", "الصف 9", "الصف 8", "الصف 7", "الصف 6", "الصف 5"])
    subject = st.sidebar.selectbox("اختر المادة:", ["الفيزياء", "الكيمياء", "الأحياء", "العلوم العامة"])
    exam_type = st.sidebar.selectbox("نوع أداة التقويم:", ["اختبار قصير 1", "اختبار قصير 2", "اختبار منتصف الفصل", "اختبار نهائي"])

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        exam_file = st.file_uploader("📄 1. إرفاق ورقة أسئلة الاختبار (PDF - إجباري):", type=["pdf"])
    with col2:
        answer_file = st.file_uploader("📝 2. إرفاق نموذج الإجابة (PDF - اختياري):", type=["pdf"])

    if st.button("🚀 بدء فحص وتدقيق الاختبار", type="primary"):
        if not exam_file:
            st.warning("⚠️ يرجى رفع ملف ورقة أسئلة الاختبار أولاً.")
        else:
            with st.spinner("جاري استخراج النصوص وفحص الورقة الامتحانية بالذكاء الاصطناعي..."):
                try:
                    # قراءة محتوى ورقة الأسئلة
                    exam_doc = fitz.open(stream=exam_file.read(), filetype="pdf")
                    exam_text = ""
                    for page in exam_doc:
                        exam_text += page.get_text()

                    # قراءة محتوى نموذج الإجابة إذا تم رفعه
                    answer_text = ""
                    if answer_file:
                        answer_doc = fitz.open(stream=answer_file.read(), filetype="pdf")
                        for page in answer_doc:
                            answer_text += page.get_text()

                    # تجهيز الأوامر للنموذج
                    prompt = f"""
 أنت خبير وتدقيق امتحانات ومكلف بمراجعة اختبار لمادة {subject} للـ {grade} ({exam_type}) المرفق نصه أدناه وفقاً لمعايير وثائق التقويم الرسمية الصادرة عن وزارة التربية والتعليم للعام الدراسي 2026/2027م.

 نص ورقة الاختبار:
 '''
 {exam_text}
 '''

 {'نص نموذج الإجابة:' + answer_text if answer_text else 'ملاحظة: لم يتم إرفاق نموذج إجابة.'}

 يرجى تقديم تقرير تدقيق فني شامل ومفصل يحتوي على:
 1. 📊 **مدى مطابقة هيكل الاختبار والزمن والدرجات مع وثيقة التقويم الرسمية**.
 2. 🎯 **تحليل مستويات الصعوبة والقدرات العقلية (معرفة، تطبيق، استدلال)**.
 3. ✍️ **السلامة اللغوية والعلمية ووضوح صياغة الأسئلة والتعليمات**.
 4. 📐 **ملاحظات حول توزيع الأسئلة الموضوعية والمقالية**.
 5. 💡 **توصيات ومقترحات لتحسين جودة ورقة الاختبار**.
                    """

                    # طلب توليد النص باستعمال العميل الحديث ونموذج gemini-2.5-flash
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )

                    st.success("✅ تم الانتهاء من تدقيق ورقة الاختبار بنجاح!")
                    st.markdown("### 📋 تقرير تدقيق الاختبار:")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء فحص الاختبار: {e}")
