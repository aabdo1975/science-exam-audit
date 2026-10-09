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
    
    # القائمة الجانبية
    st.sidebar.header("⚙️ اختيار المنهج والصف")
    grade = st.sidebar.selectbox("اختر الصف الدراسي:", ["الصف 12", "الصف 11", "الصف 10", "الصف 9", "الصف 8", "الصف 7", "الصف 6", "الصف 5"])
    subject = st.sidebar.selectbox("اختر المادة:", ["الفيزياء", "الكيمياء", "الأحياء", "العلوم العامة"])
    exam_type = st.sidebar.selectbox("نوع أداة التقويم:", ["اختبار قصير 1", "اختبار قصير 2", "اختبار نهاية الفصل الدراسي", "امتحان تجريبي"])

    # رفع الملفات الأساسية والاختيارية
    col1, col2 = st.columns(2)
    with col1:
        uploaded_exam = st.file_uploader("📄 1. إرفاق ورقة أسئلة الاختبار (إجباري - PDF):", type=["pdf"])
    with col2:
        uploaded_answer_key = st.file_uploader("📑 2. إرفاق نموذج الإجابة (اختياري - PDF):", type=["pdf"])

    # تحديد ملف الوثيقة المناسب بناءً على الصف
    if grade in ["الصف 11", "الصف 12"]:
        doc_filename = "وثيقة تقويم تعلم الطلبة في مواد العلوم (11-12) للعام 2026-2027_1 (1) (1).pdf"
    else:
        doc_filename = "وثيقة تقويم تعلم الطلبة في مواد العلوم (5-10) للعام 2026-2027_1 (1) (1).pdf"

    # قراءة نص الوثيقة المرجعية
    reference_text = ""
    if os.path.exists(doc_filename):
        try:
            ref_doc = fitz.open(doc_filename)
            for page in ref_doc:
                reference_text += page.get_text()
        except Exception:
            reference_text = "تعذر قراءة ملف الوثيقة المرجعية."

    if st.button("🚀 بدء فحص وتدقيق الاختبار", type="primary"):
        if uploaded_exam is not None:
            with st.spinner("جاري قراءة الملفات ومطابقتها مع وثيقة التقويم الرسمية..."):
                try:
                    # 1. استخراج نص ورقة الاختبار
                    exam_doc = fitz.open(stream=uploaded_exam.read(), filetype="pdf")
                    exam_text = ""
                    for page in exam_doc:
                        exam_text += page.get_text()

                    # 2. استخراج نص نموذج الإجابة (إن وجد)
                    answer_key_text = ""
                    if uploaded_answer_key is not None:
                        ans_doc = fitz.open(stream=uploaded_answer_key.read(), filetype="pdf")
                        for page in ans_doc:
                            answer_key_text += page.get_text()

                    # صياغة أمر الفحص للذكاء الاصطناعي
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    answer_prompt_part = ""
                    if answer_key_text:
                        answer_prompt_part = f"""
                        ---
                        نص نموذج الإجابة المرفق:
                        {answer_key_text}
                        
                        * ملاحظة إضافية للتدقيق: يرجى مطابقة نموذج الإجابة مع ورقة الأسئلة والتأكد من صحة الإجابات النموذجية وتوزيع الدرجات.
                        """

                    prompt = f"""
                    أنت خبير ومدقق أول لاختبارات العلوم والفيزياء بسلطنة عمان.
                    قم بتدقيق الاختبار المرفق بناءً على معايير وضوابط وثيقة التقويم الرسمية للعام الدراسي 2026/2027م.

                    تفاصيل الاختبار:
                    - الصف الدراسي: {grade}
                    - المادة: {subject}
                    - نوع أداة التقويم: {exam_type}

                    ---
                    نص وثيقة التقويم الرسمية المعتمدة (مرجع الضوابط والجدول):
                    {reference_text[:8000]}

                    ---
                    نص ورقة أسئلة الاختبار المراد تدقيقها:
                    {exam_text}
                    {answer_prompt_part}

                    ---
                    المطلوب تقديم تقرير تدقيق تفصيلي وشامل يحتوي على:
                    1. **البيانات العامة**: وضوح رأس الورقة (الزمن، الدرجة الكلية، المادة، الصف).
                    2. **مطابقة جدول المواصفات**: الأوزان النسبية للدرجات والتوزيع المستهدف للمستويات المعرفية (تذكر، تطبيق، قدرات عليا).
                    3. **التحليل العلمي والصياغة**: دقة المصطلحات، سلامة الصياغة اللغوية، خلو الأسئلة من الغموض.
                    4. **فحص نموذج الإجابة (إن وجد)**: مطابقة الدرجات، وضوح سلم التصحيح، ودقة الإجابات النموذجية.
                    5. **ملاحظات وتوصيات محددة**: مقترحات تعديل تفصيلية لكل سؤال يحتاج تحسيناً.
                    """

                    response = model.generate_content(prompt)
                    st.success("تم تدقيق الاختبار بنجاح بناءً على وثيقة التقويم الرسمية!")
                    st.markdown("### 📋 تقرير التدقيق الفني المعتمد:")
                    st.write(response.text)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء فحص الاختبار: {e}")
        else:
            st.warning("يرجى رفع ملف ورقة الأسئلة أولاً بصيغة PDF.")
