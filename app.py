import streamlit as st
import fitz  # PyMuPDF
import json
import os
from google import genai
from google.genai import types

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="منصة التدقيق الذكي للاختبارات | سلطنة عمان",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 منصة تدقيق اختبارات العلوم والفيزياء والكيمياء والأحياء")
st.caption("تدقيق تلقائي فوري وفقاً لوثائق التقويم الرسمية لوزارة التربية والتعليم (2026/2027م)")

# 2. إعداد مفتاح API من إعدادات Streamlit Secrets أو الشريط الجانبي
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = st.sidebar.text_input("أدخل مفتاح Gemini API:", type="password")

if not api_key:
    st.info("👈 يرجى إدخال مفتاح Gemini API في الشريط الجانبي أو ضبطه في Secrets لبدء استخدام المنصة.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. قاعدة البيانات المدمجة المأخوذة من المناهج
CURRICULUM_DATABASE = {
    "الصف 12": {
        "الفيزياء": {
            "الوحدة الأولى: مجالات الجاذبية": "قانون الجذب العام لنيوتن، شدة مجال الجاذبية g=GM/r^2، جهد الجاذبية السالب، طاقة الوضع، السرعة المدارية v=sqrt(GM/r)، والزمن الدوري T^2 proportional to r^3.",
            "الوحدة الثانية: المجالات الكهربائية": "قانون كولوم، شدة المجال الكهربائي المنتظم والشعاعي، الجهد الكهربائي، حركة الجسيمات المشحونة.",
            "الوحدة الثالثة: المكثفات": "السعة الكهربائية، الشحنة، طاقة المكثف، وتوصيل المكثفات على التوالي والتوازي."
        },
        "الكيمياء": {
            "الوحدة الأولى: الاتزان الكيميائي": "ثابت الاتزان Kc و Kp، مبدأ لوشاتيليه، والتغير في الضغط والحرارة والتركيز.",
            "الوحدة الثانية: الأحماض والقواعد": "تعريف برونستد-لوري، الرقم الهيدروجيني pH، المحاليل المنظمة، ومعايرة الأحماض والقواعد."
        },
        "الأحياء": {
            "الوحدة الأولى: التحكم والتنسيق": "الجهاز العصبي، جهد الراحة وجهد الفعل، التشابك العصبي، والهرمونات النباتية والحيوانية."
        }
    },
    "الصف 11": {
        "الفيزياء": {
            "الوحدة الأولى: الحركة الدائرية": "السرعة الزاوية، التسارع المركزي، والقوة الجاذبة المركزية.",
            "الوحدة الثانية: التذبذبات": "الحركة التوافقية البسيطة، البندول البسيط، الكتلة والنابض، والتردد والزمن الدوري."
        }
    },
    "الصف 5": {
        "العلوم": {
            "الوحدة الأولى: أجهزة جسم الإنسان": "أعضاء الجهاز الهضمي، وظائف المعدة والأمعاء، الجهاز التنفسي والتبادل الغازي."
        }
    }
}

# 4. واجهة الاختيارات الذكية
st.sidebar.header("⚙️ اختيار المنهج والوحدة")
selected_grade = st.sidebar.selectbox("اختر الصف الدراسي:", list(CURRICULUM_DATABASE.keys()))

available_subjects = list(CURRICULUM_DATABASE[selected_grade].keys())
selected_subject = st.sidebar.selectbox("اختر المادة:", available_subjects)

available_units = list(CURRICULUM_DATABASE[selected_grade][selected_subject].keys())
selected_unit = st.sidebar.selectbox("اختر الوحدة الدراسية:", available_units)

exam_type = st.sidebar.selectbox("نوع أداة التقويم:", ["اختبار قصير", "امتحان نهاية الفصل الدراسي", "واجب منزلي", "اختبار الاستقصاء العلمي"])

st.sidebar.markdown("---")
uploaded_exam = st.file_uploader("📄 ارفع ورقة الاختبار المراد فحصها (PDF):", type=["pdf"])

# دالة قراءة الـ PDF
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# 5. محرك الفحص والتدقيق
if st.button("🚀 بدء فحص وتدقيق الاختبار", type="primary"):
    if not uploaded_exam:
        st.warning("⚠️ يرجى رفع ملف الاختبار أولاً.")
    else:
        with st.spinner("جاري قراءة الورقة ومطابقتها مع أهداف المنهج وضوابط وثيقة التقويم الرسمية..."):
            exam_text = extract_text_from_pdf(uploaded_exam)
            unit_context = CURRICULUM_DATABASE[selected_grade][selected_subject][selected_unit]

            system_instruction = """
            أنت خبير تقويم تربوي لمواد العلوم بوزارة التربية والتعليم بسلطنة عمان.
            قم بفحص ورقة الاختبار ومطابقتها مع الضوابط الرسمية لوثائق التقويم (2026/2027):
            1. التنسيق والخط: خط Adobe Arabic بحجم 16 للمفردة، يمنع البراويز للأسئلة، كتابة الدرجات بين قوسين مربعين مثل [1].
            2. اللغة والصياغة: خلو الورقة من الأخطاء النحوية والإملائية العلمية، تجنب صيغ النفي وإبراز كلمات النفي (مثل: ليس، لا) بخط عريض إن وجدت.
            3. الاختيار من متعدد: 4 بدائل فقط، يمنع خيارات (جميع ما سبق/لا شيء مما سبق)، وجود عبارة (ظلل الشكل المقترن بالإجابة الصحيحة).
            4. أهداف التقويم ومستويات الصعوبة: مطابقة النسب المعتمدة (منخفض 40%، متوسط 40%، مرتفع 20%).
            """

            prompt = f"""
            الرجاء تدقيق ورقة الاختبار المرفوعة:
            - الصف: {selected_grade} | المادة: {selected_subject}
            - الوحدة المستهدفة: {selected_unit}
            - المرجع العلمي المستهدف من المنهج: {unit_context}
            - نوع أداة التقويم: {exam_type}

            --- نص ورقة الاختبار المرفوعة ---
            {exam_text}

            المطلوب توليد تقرير شامل يتضمن:
            1. **سلامة اللغة والصياغة العلمية.**
            2. **مدى مطابقة الأسئلة لمحتوى وأهداف الوحدة.**
            3. **توزيع المستويات المعرفية ونسب الصعوبة.**
            4. **الالتزام بالشروط الشكلية وضوابط التنسيق.**
            5. **جدول الأخطاء والتعديلات المقترحة.**
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2
                )
            )

            st.success("✅ تم الفحص بنجاح!")
            st.markdown("---")
            st.markdown(response.text)
