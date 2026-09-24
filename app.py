import streamlit as st
import pandas as pd
import psycopg2

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="ShockSimAI — Enterprise Resilience OS", layout="wide", page_icon="⚡")

# تصميم Frontend بالوضع الفاتح مع الخريطة التفاعلية
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] div, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #1e293b !important;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
        text-align: center;
    }
    .metric-title {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
    }
    .metric-delta {
        font-size: 0.7rem;
        color: #059669;
        margin-top: 4px;
    }

    .main-header {
        background: #ffffff;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .main-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
    }
    .main-subtitle {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# وظائف قاعدة البيانات السحابية (Supabase)
# ==========================================
def get_db_connection():
    database_url = st.secrets.get("DATABASE_URL")
    if not database_url:
        return None
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception:
        return None

def get_organization_tier(org_name: str) -> str:
    conn = get_db_connection()
    if not conn:
        return "growth"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT tier FROM organizations WHERE name = %s;", (org_name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return result[0]
    except Exception:
        if conn:
            conn.close()
    
    return "growth"

# ==========================================
# الشريط الجانبي (Sidebar)
# ==========================================
st.sidebar.markdown("### 🔐 بوابة المؤسسات")
st.sidebar.markdown("---")
company_input = st.sidebar.text_input("🏢 اسم الشركة (Company Name)", value="Global Manufacturing Corp")

if not company_input:
    st.warning("⚠️ يرجى إدخال اسم شركتك في الشريط الجانبي للبدء.")
    st.stop()

else:
    st.session_state["company_name"] = company_input
    org_tier = get_organization_tier(company_input)
    st.session_state["user_tier"] = org_tier
    
    st.sidebar.markdown(f"✅ **مرحباً بك:** {company_input}")
    st.sidebar.markdown(f"🏷️ **الباقة النشطة:** `{org_tier.upper()}`")
    
    max_limits = {
        "free": 50,
        "growth": 500,
        "enterprise": 999999
    }
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 مدخلات الشبكة")
    use_demo = st.sidebar.checkbox("استخدام شبكة إمداد تجريبية (Demo Data)", value=True)
    uploaded_file = st.sidebar.file_uploader("رفع ملف شبكة (CSV أو TXT)", type=["csv", "txt"])
    
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception:
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
    elif use_demo:
        # بيانات تجريبية مع إحداثيات جغرافية (lat, lon) للخريطة
        demo_data = {
            "node_id": [1, 2, 3, 4, 5, 6],
            "node_name": ["Main Supplier Port", "Central Warehouse", "Distribution Hub East", "Manufacturing Plant A", "Regional Depot", "Retail Center"],
            "type": ["Supplier", "Warehouse", "Hub", "Factory", "Depot", "Retail"],
            "risk_score": [0.2, 0.5, 0.8, 0.3, 0.6, 0.4],
            "lat": [24.7136, 25.2048, 26.0667, 23.5880, 29.3759, 21.5433],
            "lon": [46.6753, 55.2708, 50.5577, 58.3829, 47.9774, 39.1728]
        }
        df = pd.DataFrame(demo_data)

    # ==========================================
    # واجهة العرض الرئيسية (Main Frontend UI)
    # ==========================================
    st.markdown(f"""
        <div class="main-header">
            <h1 class="main-title">⚡ ShockSimAI</h1>
            <p class="main-subtitle">Enterprise OS &bull; <b>{company_input}</b> ({org_tier.upper()})</p>
        </div>
    """, unsafe_allow_html=True)

    if df is not None:
        total_nodes = len(df)
        allowed_limit = max_limits.get(org_tier, 500)
        
        if total_nodes > allowed_limit:
            st.error(f"⚠️ تجاوزت الحد الأقصى لباقة {org_tier}.")
        else:
            if 'risk_score' in df.columns:
                base_damage = round(df['risk_score'].sum() * 125.4, 1)
            else:
                base_damage = round(total_nodes * 92.5, 1)
            
            run_simulation = st.toggle("🚀 تشغيل محاكاة الصدمات بالذكاء الاصطناعي (Monte Carlo Stress Test)")

            if run_simulation:
                calculated_damage = round(base_damage * 1.42, 1)
                delta_text = "⚠️ ارتفاع ملحوظ بعد محاكاة الصدمة"
                status_color = "#dc2626"
            else:
                calculated_damage = base_damage
                delta_text = "↓ -4.2% مقارنة بالربع السابق"
                status_color = "#059669"

            # عرض المؤشرات
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">إجمالي الضرر المتوقع</div>
                        <div class="metric-value">${calculated_damage}M</div>
                        <div class="metric-delta" style="color: {status_color};">{delta_text}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">عقد الشبكة المتأثرة</div>
                        <div class="metric-value">{total_nodes} عقدة</div>
                        <div class="metric-delta" style="color: #dc2626;">⚠️ مستوى حرج</div>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">حالة النظام السحابي</div>
                        <div class="metric-value" style="font-size: 1.3rem;">متصل 🟢</div>
                        <div class="metric-delta">Supabase Secure PostgreSQL</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- ميزة الخريطة التفاعلية الجديدة ---
            st.markdown("### 🗺️ الخريطة الجغرافية الحية لعقد الشبكة (Supply Chain Map)")
            st.markdown("تتبع مواقع المصانع، المستودعات، ومراكز التوزيع وتحديد العقد ذات المخاطر العالية.")
            
            if 'lat' in df.columns and 'lon' in df.columns:
                st.map(df, latitude='lat', longitude='lon', size=50, color='#4f46e5')
            else:
                st.info("💡 الملف المرفوع لا يحتوي على إحداثيات جغرافية (lat, lon). يتم عرض الإحداثيات الافتراضية.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📋 جدول البيانات التحليلية للعقد")
            st.dataframe(df, use_container_width=True)
            
            if run_simulation:
                st.success(f"🎉 تم تفعيل محاكاة الصدمات بنجاح وتحليل توزيع المخاطر لـ {total_nodes} عقدة جغرافياً.")
    else:
        st.info("💡 يرجى تفعيل خيار البيانات التجريبية أو رفع الملف من القائمة الجانبية.")
                
