import streamlit as st
from supabase import create_client

# إعداد الصفحة
st.set_page_config(page_title="ShockSimAI - بوابة المؤسسات", layout="wide")

# جلب بيانات الاتصال من إعدادات الأمان في Streamlit Secrets أو وضعها مباشرة
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    # قيم احتياطية في حال لم يتم إعدادها في الـ Secrets
    SUPABASE_URL = "YOUR_SUPABASE_URL"
    SUPABASE_KEY = "YOUR_SUPABASE_KEY"

# إنشاء الاتصال بـ Supabase
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")

# تهيئة حالة الجلسة (Session State)
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "company_name" not in st.session_state:
    st.session_state["company_name"] = ""
if "company_id" not in st.session_state:
    st.session_state["company_id"] = None

# الشريط الجانبي للمصادقة وتسجيل الشركات
st.sidebar.title("🔐 بوابة المؤسسات الآمنة")

auth_mode = st.sidebar.radio("اختر الحالة", ["تسجيل دخول شركة", "تسجيل شركة جديدة"])

if auth_mode == "تسجيل شركة جديدة":
    st.sidebar.subheader("تسجيل شركة جديدة")
    new_company_name = st.sidebar.text_input("اسم الشركة الجديد", key="new_comp_input")
    selected_tier = st.sidebar.selectbox("اختر الباقة", ["Enterprise", "Pro", "Standard"], key="tier_input")
    register_btn = st.sidebar.button("إنشاء حساب المؤسسة")
    
    if register_btn:
        if new_company_name.strip():
            try:
                data = {"company_name": new_company_name.strip(), "subscription_tier": selected_tier}
                res = supabase.table("companies").insert(data).execute()
                st.sidebar.success("تم إنشاء الحساب بنجاح! يمكنك الانتقال لتسجيل الدخول الآن.")
            except Exception as e:
                st.sidebar.error(f"فشل التسجيل (تأكد أن الاسم غير مكرر): {e}")
        else:
            st.sidebar.warning("يرجى إدخال اسم الشركة.")

else:  # حالة تسجيل الدخول
    st.sidebar.subheader("تسجيل دخول شركة")
    login_company_name = st.sidebar.text_input("اسم الشركة المسجل", key="login_comp_input")
    login_btn = st.sidebar.button("دخول للوحة المحاكاة")

    if login_btn:
        if login_company_name.strip():
            try:
                res = supabase.table("companies").select("*").eq("company_name", login_company_name.strip()).execute()
                if res.data and len(res.data) > 0:
                    st.session_state["authenticated"] = True
                    st.session_state["company_name"] = res.data[0]["company_name"]
                    st.session_state["company_id"] = res.data[0]["id"]
                    st.sidebar.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.sidebar.error("اسم الشركة غير مسجل، يرجى التحقق أو إنشاء حساب جديد.")
            except Exception as e:
                st.sidebar.error(f"حدث خطأ أثناء الاتصال: {e}")
        else:
            st.sidebar.warning("يرجى إدخال اسم الشركة.")

# الواجهة الرئيسية للتطبيق
st.title("🛡️ منصة ShockSimAI - محاكاة شبكات الإمداد وتحليل المخاطر بالذكاء الاصطناعي")

if st.session_state.get("authenticated", False):
    st.success(مرحباً بك في لوحة تحكم شركة: **{st.session_state['company_name']}** (معرّف الشركة: {st.session_state['company_id']}))
    
    st.divider()
    st.subheader("📁 الخطوة الثانية: رفع بيانات شبكة الإمداد (CSV)")
    
    uploaded_file = st.file_uploader("اختر ملف الـ CSV الخاص بشبكة الموردين", type=["csv"])
    
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
            st.info("تم قراءة الملف بنجاح وإليك المعاينة:")
            st.text(file_content[:500] + "..." if len(file_content) > 500 else file_content)
            
            if st.button("حفظ الشبكة في قاعدة البيانات"):
                net_data = {
                    "company_id": st.session_state["company_id"],
                    "network_data": file_content
                }
                save_res = supabase.table("company_networks").insert(net_data).execute()
                st.success("تم حفظ بيانات شبكة الإمداد بنجاح في قاعدة البيانات وجاهزة للتحليل!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
            
    st.divider()
    st.subheader("⚡ محرك المحاكاة والذكاء الاصطناعي (قريباً في الخطوة الثالثة)")
    st.write("بعد اكتمال رفع البيانات وحفظها، سنقوم بتفعيل محرّك الصدمات وتحليل المخاطر هنا.")

    if st.sidebar.button("تسجيل خروج"):
        st.session_state["authenticated"] = False
        st.session_state["company_name"] = ""
        st.session_state["company_id"] = None
        st.rerun()

else:
    st.warning("⚠️ يرجى تسجيل الدخول عبر القائمة الجانبية (Sidebar) للوصول إلى لوحة التحكم وإدارة شبكات الإمداد الخاصة بشركتك.")
    
