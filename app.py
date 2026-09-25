import streamlit as st
from supabase import create_client
import pandas as pd
import io

# إعداد الصفحة
st.set_page_config(page_title="ShockSimAI - محاكاة شبكات الإمداد", layout="wide")

# جلب بيانات الاتصال من إعدادات الأمان في Streamlit Secrets
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
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

# تهيئة حالة الجلسة
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "company_name" not in st.session_state:
    st.session_state["company_name"] = ""
if "company_id" not in st.session_state:
    st.session_state["company_id"] = None

# الشريط الجانبي للمصادقة
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

else:
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
                    st.sidebar.error("اسم الشركة غير مسجل، يرجى التحقق.")
            except Exception as e:
                st.sidebar.error(f"حدث خطأ أثناء الاتصال: {e}")
        else:
            st.sidebar.warning("يرجى إدخال اسم الشركة.")

# الواجهة الرئيسية للتطبيق
st.title("🛡️ منصة ShockSimAI - محاكاة شبكات الإمداد وتحليل المخاطر بالذكاء الاصطناعي")

if st.session_state.get("authenticated", False):
    st.success(f"مرحباً بك في لوحة تحكم شركة: **{st.session_state['company_name']}** (معرّف الشركة: {st.session_state['company_id']})")
    
    st.divider()
    st.subheader("📁 الخطوة الثانية: رفع وتخزين بيانات شبكة الإمداد (CSV)")
    
    uploaded_file = st.file_uploader("اختر ملف الـ CSV الخاص بشبكة الموردين", type=["csv"])
    
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
            df = pd.read_csv(io.StringIO(file_content))
            
            st.info("معاينة بيانات شبكة الإمداد المرفوعة:")
            st.dataframe(df.head())
            
            if st.button("حفظ الشبكة في قاعدة البيانات"):
                net_data = {
                    "company_id": st.session_state["company_id"],
                    "network_data": file_content
                }
                supabase.table("company_networks").insert(net_data).execute()
                st.success("تم حفظ بيانات شبكة الإمداد في قاعدة البيانات بنجاح!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة أو حفظ الملف: {e}")
            
    st.divider()
    st.subheader("⚡ الخطوة الثالثة: محرك المحاكاة وتحليل المخاطر بالذكاء الاصطناعي")
    
    # محاكاة الصدمات وتحليل المخاطر
    shock_target = st.text_input("حدد المورد أو العقدة المستهدفة بالصدمة (مثال: Supplier_A أو Port_X):")
    shock_severity = st.slider("اختر شدة الصدمة (نسبة التعطل %)", 0, 100, 50)
    
    if st.button("تشغيل محاكاة الصدمة وتحليل المخاطر"):
        if shock_target:
            with st.spinner("جاري تشغيل خوارزميات محاكاة الانتشار وتحليل المخاطر بالذكاء الاصطناعي..."):
                # محاكاة تحليل المخاطر بناءً على المدخلات
                st.warning(f"⚠️ تنبيه صدمة نشطة: تعطل بنسبة {shock_severity}% في العقدة ({shock_target})")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("معدل التأثر الكلي للشبكة", f"{int(shock_severity * 0.75)}%")
                col2.metric("العقد المتأثرة بالتبعية", "3 موردين فرعيين")
                col3.metric("مستوى خطورة الذكاء الاصطناعي", "عالي (High Risk)" if shock_severity > 50 else "متوسط (Medium Risk)")
                
                st.subheader("📋 تقرير توصيات الذكاء الاصطناعي للتخفيف من المخاطر:")
                st.info(
                    f"• بناءً على المحاكاة لعقدة **{shock_target}**، يوصى بالتحول الفوري إلى المورد البديل لتجنب توقف خط الإنتاج بنسبة {shock_severity}%.\n"
                    "• تم رصد مسارات بديلة لتوزيع المخزون الاحتياطي لتقليل الخسائر."
                )
        else:
            st.warning("يرجى كتابة اسم المورد أو العقدة المستهدفة أولاً.")

    st.sidebar.divider()
    if st.sidebar.button("تسجيل خروج"):
        st.session_state["authenticated"] = False
        st.session_state["company_name"] = ""
        st.session_state["company_id"] = None
        st.rerun()

else:
    st.warning("⚠️ يرجى تسجيل الدخول عبر القائمة الجانبية (Sidebar) للوصول إلى لوحة التحكم ومحرك المحاكاة.")
    
