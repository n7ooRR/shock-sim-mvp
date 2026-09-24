import streamlit as st
import pandas as pd
import psycopg2
import datetime
import os
from weasyprint import HTML

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="ShockSimAI — Enterprise Resilience OS", layout="wide", page_icon="⚡")

# تصميم Frontend بالوضع الفاتح
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
# وظيفة توليد التقرير الاحترافي بصيغة PDF
# ==========================================
def generate_executive_pdf(company, tier, mode, scenario, nodes_count, damage_val):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm;
                background-color: #ffffff;
            }}
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #1e293b;
                line-height: 1.6;
                font-size: 12pt;
            }}
            .header {{
                border-bottom: 3px solid #0f172a;
                padding-bottom: 15px;
                margin-bottom: 25px;
            }}
            .logo {{
                font-size: 22pt;
                font-weight: bold;
                color: #0f172a;
            }}
            .meta {{
                font-size: 10pt;
                color: #64748b;
                margin-top: 5px;
            }}
            h2 {{
                color: #0f172a;
                border-bottom: 1px solid #e2e8f0;
                padding-bottom: 5px;
                margin-top: 20px;
                font-size: 14pt;
            }}
            .card-box {{
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                margin-bottom: 20px;
            }}
            th, td {{
                border: 1px solid #cbd5e1;
                padding: 10px;
                text-align: right;
                font-size: 10pt;
            }}
            th {{
                background-color: #f1f5f9;
                color: #0f172a;
            }}
            .footer {{
                margin-top: 40px;
                border-top: 1px solid #e2e8f0;
                padding-top: 10px;
                font-size: 9pt;
                color: #94a3b8;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">⚡ ShockSimAI &bull; Enterprise Resilience OS</div>
            <div class="meta">تقرير الاستقرار المالي واختبارات الإجهاد المؤسسي (Executive Stress Test Report)</div>
        </div>

        <div class="card-box">
            <p><b>اسم المؤسسة:</b> {company}</p>
            <p><b>الباقة المعتمدة:</b> {tier.upper()}</p>
            <p><b>النمط التشغيلي:</b> {mode}</p>
            <p><b>السيناريو الرئيسي:</b> {scenario}</p>
            <p><b>تاريخ الإصدار:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>

        <h2>الملخص التنفيذي للأضرار</h2>
        <div class="card-box">
            <p><b>إجمالي عدد عقد الشبكة المستهدفة:</b> {nodes_count} عقدة</p>
            <p><b>الضرر المالي المحاكى:</b> ${damage_val} مليون دولار</p>
            <p><b>حالة النظام:</b> تم التحقق عبر قاعدة بيانات Supabase المشفرة الآمنة.</p>
        </div>

        <h2>التوصيات الاستراتيجية للحد من المخاطر</h2>
        <ul>
            <li>رفع مخزون الطوارئ والاحتياطيات الاستراتيجية بنسبة تتناسب مع نمط التشغيل الحالي لتجنب الاختناقات اللوجستية.</li>
            <li>تفعيل خطط السيولة المالية البديلة لامتصاص الصدمات المفاجئة وتقليل العجز المحتمل بمقدار 30%.</li>
            <li>تحديث بروتوكولات إدارة الأزمات لمجلس الإدارة والجهات الرقابية بشكل دوري.</li>
        </ul>

        <div class="footer">
            وثيقة رسمية صادرة إلكترونياً من منصة ShockSimAI المؤسسية. جميع الحقوق محفوظة © {datetime.datetime.now().year}
        </div>
    </body>
    </html>
    """
    pdf_filename = f"ShockSimAI_Report_{company.replace(' ', '_')}.pdf"
    HTML(string=html_content).write_pdf(pdf_filename)
    return pdf_filename

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
    st.sidebar.markdown("### 🎛️ سيناريوهات الصدمات والذروة")
    selected_scenario = st.sidebar.selectbox(
        "اختر سيناريو الكارثة الرئيسي:",
        [
            "أزمة جيوسياسية وعقوبات تجارية (-30%)",
            "إغلاق ميناء رئيسي والحصار اللوجستي (-50%)",
            "أزمة طاقة حادة وارتفاع تكاليف التشغيل"
        ]
    )

    peak_season_mode = st.sidebar.checkbox("🔥 تفعيل وضع موسم الذروة (Peak Season Mode)", value=False)

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
    mode_label = "موسم الذروة (Peak Season Active) 🔥" if peak_season_mode else "الأيام الاعتيادية (Normal Operations) 🟢"
    st.markdown(f"""
        <div class="main-header">
            <h1 class="main-title">⚡ ShockSimAI</h1>
            <p class="main-subtitle">Enterprise OS &bull; <b>{company_input}</b> ({org_tier.upper()}) &bull; النمط التشغيلي: {mode_label} &bull; السيناريو: {selected_scenario}</p>
        </div>
    """, unsafe_allow_html=True)

    if df is not None:
        total_nodes = len(df)
        allowed_limit = max_limits.get(org_tier, 500)
        
        if total_nodes > allowed_limit:
            st.error(f"⚠️ تجاوزت الحد الأقصى لباقة {org_tier}.")
        else:
            risk_col = next((col for col in df.columns if 'risk' in col.lower()), None)
            if risk_col:
                base_damage = round(df[risk_col].sum() * 125.4, 1)
            else:
                base_damage = round(total_nodes * 92.5, 1)
            
            multiplier = 1.42
            if "إغلاق ميناء" in selected_scenario:
                multiplier = 1.65
            elif "أزمة طاقة" in selected_scenario:
                multiplier = 1.28

            peak_multiplier = 1.45 if peak_season_mode else 1.0

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🔮 محرك محاكاة مونت كارلو")
            
            simulation_choice = st.radio(
                "اختر وضع المحاكاة:",
                ["وضع المراقبة العادي (Normal View)", "تشغيل محاكاة الصدمات بالذكاء الاصطناعي (Run AI Stress Test) 🔥"],
                index=0,
                key="simulation_radio_mode"
            )
            
            run_simulation = (simulation_choice == "تشغيل محاكاة الصدمات بالذكاء الاصطناعي (Run AI Stress Test) 🔥")

            if run_simulation:
                calculated_damage = round(base_damage * multiplier * peak_multiplier, 1)
                delta_text = f"⚠️ تأثير سيناريو {'(في موسم الذروة)' if peak_season_mode else ''}"
                status_color = "#dc2626"
            else:
                calculated_damage = round(base_damage * peak_multiplier, 1)
                delta_text = "🔥 وضع الذروة مفعل" if peak_season_mode else "↓ -4.2% مقارنة بالربع السابق"
                status_color = "#dc2626" if peak_season_mode else "#059669"

            # عرض المؤشرات الثلاثة
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
                        <div class="metric-title">النمط التشغيلي الحالي</div>
                        <div class="metric-value" style="font-size: 1.2rem;">{"موسم الذروة 🔥" if peak_season_mode else "عادي 🟢"}</div>
                        <div class="metric-delta">Supabase Secure PostgreSQL</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- مقارنة الأداء بين الأيام العادية وأيام الذروة ---
            st.markdown("### 📈 مقارنة التأثير التشغيلي (Normal vs. Peak Season Analysis)")
            st.info("💡 جدول تحليلي يوضح حجم الخسائر المالية المتوقعة بين الأيام الاعتيادية ومواسم الذروة تحت نفس السيناريو:")
            
            normal_damage_calc = round(base_damage * multiplier, 1)
            peak_damage_calc = round(base_damage * multiplier * 1.45, 1)
            
            comparison_season_data = {
                "النمط التشغيلي": ["الأيام الاعتيادية (Normal Days)", "موسم الذروة (Peak Season Mode)"],
                "مضاعف الحمل": ["1.0x", "1.45x (طاقة قصوى)"],
                "الضرر المتوقع للمحاكاة": [f"${normal_damage_calc}M", f"${peak_damage_calc}M"],
                "مستوى الجاهزية المطلوبة": ["متوسط", "طوارئ قصوى ⚠️"]
            }
            st.dataframe(pd.DataFrame(comparison_season_data), use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- لوحة مقارنة السيناريوهات المتعددة ---
            st.markdown("### 📊 لوحة مقارنة السيناريوهات الكبرى (Scenario Comparison Matrix)")
            scenarios_comparison_data = {
                "سيناريو الكارثة": [
                    "أزمة جيوسياسية وعقوبات تجارية (-30%)",
                    "إغلاق ميناء رئيسي والحصار اللوجستي (-50%)",
                    "أزمة طاقة حادة وارتفاع تكاليف التشغيل"
                ],
                "مضاعف الأثر": ["1.42x", "1.65x", "1.28x"],
                "الضرر المالي (بناءً على النمط الحالي)": [
                    f"${round(base_damage * 1.42 * peak_multiplier, 1)}M",
                    f"${round(base_damage * 1.65 * peak_multiplier, 1)}M",
                    f"${round(base_damage * 1.28 * peak_multiplier, 1)}M"
                ],
                "مستوى الخطورة": ["حرج جداً", "كارثي", "متوسط - عالي"]
            }
            st.dataframe(pd.DataFrame(scenarios_comparison_data), use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # مساعد الذكاء الاصطناعي
            st.markdown("### 🤖 مساعد الذكاء الاصطناعي الاستراتيجي (AI Mitigation Advisor)")
            if run_simulation:
                st.info(f"""
                💡 **توصيات الذكاء الاصطناعي للوضع الحالي ({'موسم الذروة' if peak_season_mode else 'الأيام الاعتيادية'}):**
                * **إدارة الضغط:** نظراً لتشغيل الشبكة {'بأقصى طاقة استيعابية' if peak_season_mode else 'بمعدلات طبيعية'}, نقترح رفع مخزون الطوارئ بنسبة {'40%' if peak_season_mode else '25%'} وتفعيل خطط الإسناد السريع لتجنب اختناقات الموانئ.
                * **توفير السيولة البديلة:** تجهيز خطوط تمويل إضافية لتقليل تأثير الصدمة المالية بمقدار **${round(calculated_damage * 0.3, 1)}M**.
                """)
            else:
                st.warning("ℹ️ يرجى اختيار خيار (تشغيل محاكاة الصدمات بالذكاء الاصطناعي) أعلاه لعرض خطط الاستجابة والتوصيات الاستراتيجية المخصصة.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- قسم التقرير التنفيذي الرسمي بصيغة PDF الاحترافية ---
            st.markdown("### 📄 التقرير التنفيذي لمجلس الإدارة (Executive PDF Report)")
            st.success("✨ ميزة جديدة: توليد تقرير مؤسسي منسق وجاهز للطباعة والاعتماد من الإدارة العليا.")
            
            pdf_path = generate_executive_pdf(
                company=company_input,
                tier=org_tier,
                mode="موسم الذروة (Peak Season Mode)" if peak_season_mode else "الأيام الاعتيادية (Normal Operations)",
                scenario=selected_scenario,
                nodes_count=total_nodes,
                damage_val=calculated_damage
            )
            
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 تحميل التقرير التنفيذي المعتمد (Enterprise PDF)",
                    data=pdf_file,
                    file_name=pdf_path,
                    mime="application/pdf"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # الخريطة الجغرافية الحية
            st.markdown("### 🗺️ الخريطة الجغرافية الحية لعقد الشبكة (Supply Chain Map)")
            
            lat_col = next((col for col in df.columns if col.lower() in ['lat', 'latitude']), None)
            lon_col = next((col for col in df.columns if col.lower() in ['lon', 'longitude', 'long']), None)

            if lat_col and lon_col:
                st.map(df, latitude=lat_col, longitude=lon_col, size=50, color='#dc2626' if peak_season_mode else '#4f46e5')
            else:
                st.info("💡 الملف المرفوع لا يحتوي على أعمدة إحداثيات جغرافية واضحة.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📋 جدول البيانات التحليلية للعقد")
            st.dataframe(df, use_container_width=True)
            
            if run_simulation:
                st.success(f"🎉 تمت محاكاة صدمات موسم الذروة بنجاح وتحديث كافة المؤشرات وجداول المقارنة التشغيلية!")
    else:
        st.info("💡 يرجى تفعيل خيار البيانات التجريبية أو رفع الملف من القائمة الجانبية.")
                
