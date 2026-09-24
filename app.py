import streamlit as st
import pandas as pd
from database import get_organization_tier, get_db_connection

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="ShockSimAI - Enterprise Resilience OS", layout="wide")

# ==========================================
# بوابة تسجيل الدخول المؤسسي (Onboarding & Login)
# ==========================================
st.sidebar.title("🔐 بوابة المؤسسات")
st.sidebar.markdown("أدخل اسم شركتك للوصول إلى بيئة العمل الخاصة بك.")

company_input = st.sidebar.text_input("اسم شركتك (Company Name)", value="")

if not company_input:
    st.warning("⚠️ يرجى إدخال اسم شركتك في الشريط الجانبي للبدء في استخدام منصة ShockSimAI المؤسسية.")
    
    # عرض واجهة ترحيبية عامة للزوار الجدد
    st.title("🚀 ShockSimAI — Enterprise Resilience OS")
    st.markdown("### المنصة الأولى عالمياً لتقييم صدمات سلاسل الإمداد وإدارة المخاطر بالذكاء الاصطناعي.")
    st.info("👈 يرجى كتابة اسم شركتك في القائمة الجانبية على اليسار لتفعيل الجلسة واستخدام الأدوات.")
    st.stop() # إيقاف التنفيذ لحين إدخال اسم الشركة

else:
    # حفظ اسم الشركة وبقتها في الجلسة (Session State)
    st.session_state["company_name"] = company_input
    
    # جلب باقة الشركة الفعلية من سحابة Supabase
    org_tier = get_organization_tier(company_input)
    st.session_state["user_tier"] = org_tier
    
    st.sidebar.success(f"مرحباً بك، فريق **{company_input}**")
    st.sidebar.info(f"🏷️ باقة المؤسسة الحالية: **{org_tier.upper()}**")
    
    # حدود العقد لكل باقة
    max_limits = {
        "free": 50,
        "growth": 500,
        "enterprise": 999999
    }
    
    # ==========================================
    # الواجهة الرئيسة للمنصة بعد تسجيل الدخول
    # ==========================================
    st.title("🚀 ShockSimAI — Enterprise Resilience OS")
    st.markdown(f"**بيئة عمل مخصصة لشركة:** `{company_input}` | **الباقة النشطة:** `{org_tier.upper()}`")
    
    # مثال على التحقق من الباقة عند رفع ملف الشبكة
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 بيانات الشبكة والسيناريو")
    uploaded_file = st.sidebar.file_uploader("رفع ملف شبكة الإمداد (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        total_nodes = len(df)
        allowed_limit = max_limits.get(org_tier, 50)
        
        # فحص القيود (Feature Gating)
        if total_nodes > allowed_limit:
            st.error(f"⚠️ عذراً، شبكتك تحتوي على {total_nodes} عقدة، بينما الحد الأقصى المسموح به لباقة (**{org_tier}**) هو {allowed_limit} عقدة. يرجى ترقية اشتراكك المؤسسي للمتابعة.")
        else:
            st.success(f"✅ شبكتك مطابقة لحدود الباقة ({total_nodes}/{allowed_limit} عقدة). المحاكاة جاهزة للعمل!")
            # هنا تستكمل باقي كود المحاكاة والتحليلات الخاص بك...
    else:
        st.info("💡 قم برفع ملف الـ CSV الخاص بشبكة الإمداد من القائمة الجانبية لبدء المحاكاة وتحليل المخاطر.")
        
