import os
import fitz  # PyMuPDF
import streamlit as st
from google import genai

st.set_page_config(page_title="منصة تدقيق الاختبارات - إعداد أ. عبد الجابر حسن", page_icon="🔬", layout="wide")

st.title("🔬 منصة تدقيق اختبارات العلوم والفيزياء والكيمياء والأحياء")
st.subheader("👨‍🏫 إعداد وتطوير: المشرف التربوي أ. عبد الجابر حسن علي عبد الرحيم")
st.caption("تدقيق تلقائي فوري وفقاً لوثائق التقويم الرسمية لوزارة التربية والتعليم (2026/2027م)")

# --- حماية المنصة بكلمة سر للمشرفين ---
SUPERVISOR_PASSWORD = "Inspect2026"  # يمكنك تغيير كلمة السر هنا لأي رمز تفضله

st.sidebar.header("🔒 صلاحية الدخول")
access_code = st.sidebar.text_input("🔑 أدخل كلمة سر المشرفين:", type="password")

if access_code != SUPERVISOR_PASSWORD:
    st.warning("🔒 هذه المنصة مغلقة ومخصصة للفريق الإشرافي فقط. يرجى إدخال كلمة سر المشرفين الصحيحة في الشريط الجانبي لبدء الاستخدام.")
else:
    # جلب المفاتيح المتعددة من Secrets
    raw_keys = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

    # إذا أدخل المشرف مفتاحاً خاصاً به إضافياً
    user_key = st.sidebar.text_input("🔑 مفتاح API إضافي (اختياري):", type="password")
    if user_key:
        api_keys = [user_key.strip()] + api_keys

    if not api_keys:
        st.info("👈 يرجى التأكد من ضبط المفاتيح في إعدادات Secrets.")
    else:
        st.success("🔓 تم التحقق من صلاحية المشرف بنجاح. أهلاً بك!")
        
        # القائمة الجانبية لإعدادات الفحص
        st.sidebar.header("⚙️ اختيار المنهج والصف")
        grade = st.sidebar.selectbox("اختر الصف الدراسي:", ["الصف 10", "الصف 11", "الصف 12", "الصف 9", "الصف 8", "الصف 7", "الصف 6", "الصف 5"])
        
        subject = st.sidebar.selectbox("اختر المادة:", ["الفيزياء", "الكيمياء", "الأحياء", "العلوم العامة", "العلوم والبيئة (الصف 11)", "العلوم والبيئة (الصف 12)"])
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
                        # قراءة نص ورقة الاختبار
                        exam_doc = fitz.open(stream=exam_file.read(), filetype="pdf")
                        exam_text = ""
                        for page in exam_doc:
                            exam_text += page.get_text()

                        # قراءة نص نموذج الإجابة
                        answer_text = ""
                        if answer_file:
                            answer_doc = fitz.open(stream=answer_file.read(), filetype="pdf")
                            for page in answer_doc:
                                answer_text += page.get_text()

                        # تجهيز الأوامر
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

                        # التدوير الآلي بين المفاتيح
                        response = None
                        last_error = None
                        
                        for current_key in api_keys:
                            try:
                                client = genai.Client(api_key=current_key)
                                response = client.models.generate_content(
                                    model='gemini-3.8-flash',
                                    contents=prompt,
                                )
                                if response:
                                    break
                            except Exception as err:
                                last_error = err
                                continue

                        if response:
                            st.success("✅ تم الانتهاء من تدقيق ورقة الاختبار بنجاح!")
                            st.markdown("### 📋 تقرير تدقيق الاختبار:")
                            st.markdown(response.text)
                        else:
                            st.error(f"حدث خطأ أثناء فحص الاختبار: {last_error}")

                    except Exception as e:
                        st.error(f"حدث خطأ أثناء المعالجة: {e}")
