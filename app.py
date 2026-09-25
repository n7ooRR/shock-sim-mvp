import streamlit as st
from supabase import create_client, Client

# إعدادات الاتصال بقاعدة بيانات Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_company_auth():
    st.sidebar.title("🔐 بوابة المؤسسات الآمنة")
    
    # خيار تسجيل الدخول أو التسجيل الجديد
    auth_mode = st.sidebar.radio("اختر الحالة", ["تسجيل دخول شركة", "تسجيل شركة جديدة"])
    
    if auth_mode == "تسجيل دخول شركة":
        company_name_input = st.sidebar.text_input("اسم الشركة (Company Name)")
        login_btn = st.sidebar.button("دخول للوحة المحاكاة")
        
        if login_btn:
            if company_name_input:
                # البحث عن الشركة في قاعدة بيانات Supabase
                response = supabase.table("companies").select("*").eq("company_name", company_name_input).execute()
                
                if response.data and len(response.data) > 0:
                    st.session_state["authenticated"] = True
                    st.session_state["company_data"] = response.data[0]
                    st.sidebar.success(f"مرحباً بك، {company_name_input}!")
                    st.rerun()
                else:
                    st.sidebar.error("اسم الشركة غير مسجل. يرجى التسجيل أولاً.")
            else:
                st.sidebar.warning("يرجى إدخال اسم الشركة.")
                
    else: # تسجيل شركة جديدة
        new_company_name = st.sidebar.text_input("اسم الشركة الجديد")
        selected_tier = st.sidebar.selectbox("اختر الباقة", ["Free", "Growth", "Enterprise"])
        register_btn = st.sidebar.button("إنشاء حساب المؤسسة")
        
        if register_btn:
            if new_company_name:
                # إدخال الشركة الجديدة في Supabase
                data = {"company_name": new_company_name, "subscription_tier": selected_tier}
                res = supabase.table("companies").insert(data).execute()
                
                if res.data:
                    st.sidebar.success("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
                else:
                    st.sidebar.error("حدث خطأ أثناء التسجيل.")
            else:
                st.sidebar.warning("يرجى إدخال اسم الشركة.")

# التحقق مما إذا كانت الشركة مسجلة الدخول أم لا
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    check_company_auth()
    st.stop() # إيقاف عرض باقي المنصة لحين تسجيل الدخول
