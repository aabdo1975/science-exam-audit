import streamlit as st
import google.generativeai as genai
import os
import fitz  # PyMuPDF

st.set_page_config(page_title="منصة تدقيق الاختبارات", page_icon="🔬", layout="wide")

st.title("🔬 منصة تدقيق اختبارات العلوم والفيزياء والكيمياء والأحياء")
st.caption("تدقيق تلقائي فوري وفقاً لوثائق التقويم الرسمية لوزارة التربية والتعليم (2026/2027م)")

# جلب المفتاح الأمني
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.info("👈 لبدء استخدام المنصة يرجى إدخال مفتاح Gemini API في Secrets المنصة.")
    api_key = st.sidebar.text_input("أدخل مفتاح Gemini API:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    
    # القائمة الجانبية (تم حذف خيار الوحدة لتسهيل الدمج بين الدروس)
    st.sidebar.header("⚙️ اختيار المنهج والصف")
    grade = st.sidebar.selectbox("اختر الصف الدراسي:", ["الصف 11", "الصف 12", "الصف 10", "الصف 9"])
    subject = st.sidebar.selectbox("اختر المادة:", ["الفيزياء", "الكيمياء", "الأحياء", "العلوم العامة"])
    exam_type = st.sidebar.selectbox("نوع أداة التقويم:", ["اختبار قصير 1", "اختبار قصير 2", "اختبار نهاية الفصل الدراسي"])

    uploaded_file = st.file_uploader("📄 إرفاق ورقة الاختبار المراد فحصها (PDF):", type=["pdf"])

    if st.button("🚀 بدء فحص وتدقيق الاختبار", type="primary"):
        if uploaded_file is not None:
            with st.spinner("جاري قراءة الملف وتدقيقه بواسطة الذكاء الاصطناعي..."):
                try:
                    # استخراج النص من ملف PDF المرفوع
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    exam_text = ""
                    for page in doc:
                        exam_text += page.get_text()

                    # إعداد المحرك للتحليل
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    prompt = f"""
                    أنت خبير تدقيق اختبارات علوم في وزارة التربية والتعليم بسلطنة عمان.
                    قم بتدقيق الاختبار المرفق بناءً على معايير التقويم الرسمية لعام 2026/2027م.
                    
                    تفاصيل الاختبار:
                    - الصف: {grade}
                    - المادة: {subject}
                    - نوع الاختبار: {exam_type}
                    
                    نص الاختبار:
                    {exam_text}
                    
                    المطلوب في التقرير:
                    1. تقييم مدى مطابقة الأسئلة لجدول المواصفات والأوزان النسبية.
                    2. مراجعة الصياغة اللغوية والعلمية للأسئلة.
                    3. التحقق من تنوع المستويات المعرفية (تذكر، تطبيق، قدرات عليا).
                    4. ملاحظات تحسين محددة لكل سؤال إن وجدت.
                    """

                    response = model.generate_content(prompt)
                    st.success("تم التدقيق بنجاح!")
                    st.markdown("### 📋 تقرير تدقيق الاختبار:")
                    st.write(response.text)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء الفحص: {e}")
        else:
            st.warning("يرجى رفع ملف الاختبار أولاً بصيغة PDF.")
