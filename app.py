import streamlit as st
import pandas as pd
import networkx as nx

from database import init_db, load_memory_from_db, log_event_to_db, get_event_history_df
from engine import get_timeline_impacts, final_impacts, calculate_total_damage, predictive_forecast

init_db()

st.set_page_config(
    page_title="Shock Sim AI — Enterprise Resilience OS",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Shock Sim AI — Enterprise Resilience OS (Final MVP)")
st.caption("منصة التوأم الرقمي المتقدمة لتقييم صدمات سلاسل الإمداد وإدارة المخاطر التشغيلية.")

# خيار تحميل ملف CSV مخصص للشبكة أو استخدام الافتراضية
st.sidebar.header("📁 بيانات الشبكة والسيناريو")
uploaded_file = st.sidebar.file_uploader("رفع ملف شبكة الإمداد (CSV)", type=["csv"])

def build_network(uploaded):
    graph = nx.DiGraph()
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            for _, row in df.iterrows():
                graph.add_edge(row["source"], row["target"], weight=float(row["weight"]), cost=float(row["cost"]))
            st.sidebar.success("تم تحميل شبكة الموردين المخصصة بنجاح!")
            return graph
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة الملف: {e}")
    
    # الشبكة الافتراضية القياسية
    edges = [
        ("Energy", "Suppliers", 0.85, 35),
        ("Raw_Materials", "Suppliers", 0.80, 30),
        ("Suppliers", "Manufacturing", 0.90, 50),
        ("Suppliers", "Logistics", 0.65, 25),
        ("Manufacturing", "Distribution", 0.75, 40),
        ("Logistics", "Distribution", 0.70, 30),
        ("Distribution", "Market", 0.85, 20),
    ]
    for source, target, weight, cost in edges:
        graph.add_edge(source, target, weight=float(weight), cost=float(cost))
    return graph

graph = build_network(uploaded_file)

if "memory" not in st.session_state:
    st.session_state.memory = load_memory_from_db(graph)

company_name = st.sidebar.text_input("اسم الشركة", "Global Manufacturing Corp")
shock_node = st.sidebar.selectbox("مصدر الصدمة الأساسي", list(graph.nodes))
shock_magnitude = st.sidebar.slider("شدة الصدمة (%)", 10, 100, 80)

shock_sources = {shock_node: shock_magnitude}

# تشغيل المحاكاة
timeline = get_timeline_impacts(graph, shock_sources, actions=[], memory=st.session_state.memory, steps=4)
final_imp = final_impacts(timeline)
total_dmg = calculate_total_damage(final_imp)

col1, col2, col3 = st.columns(3)
col1.metric("إجمالي الضرر المتوقع (Damage Units)", f"{total_dmg:.1f}")
col2.metric("عدد العقد المتأثرة", len([n for n, v in final_imp.items() if v > 0]))
col3.metric("حالة القاعدة الدائمة", "متصلة بنجاح (SQLite)")

st.divider()

# قسم التنبؤ المتقدم (مونت كارلو)
st.subheader("🔮 تنبؤات مونت كارلو الاحتمالية (Monte Carlo Forecast)")
if st.button("تشغيل محاكاة التنبؤ الاحترافية"):
    forecast_df, summary = predictive_forecast(graph, shock_sources, st.session_state.memory)
    st.session_state.forecast_df = forecast_df
    st.session_state.summary = summary
    st.success("تم تشغيل محاكاة التنبؤ بنجاح!")

if "forecast_df" in st.session_state:
    p1, p2, p3 = st.columns(3)
    p1.metric("الضرر المتوقع (Expected)", f"{st.session_state.summary['expected_damage']:.1f}")
    p2.metric("ضرر مستوى الثقة P90", f"{st.session_state.summary['p90_damage']:.1f}")
    p3.metric("ضرر مستوى الثقة P95", f"{st.session_state.summary['p95_damage']:.1f}")
    
    st.dataframe(st.session_state.forecast_df.round(2), use_container_width=True, hide_index=True)

st.divider()

# قسم سجل الأحداث والتدقيق الدائم
st.subheader("📋 سجل التدقيق والأحداث المخزنة (Persistent Audit Trail)")
event_history = get_event_history_df()
if not event_history.empty:
    st.dataframe(event_history, use_container_width=True, hide_index=True)
else:
    st.info("لا توجد أحداث مسجلة حتى الآن. يمكنك تسجيل حدث جديد أدناه.")

with st.form("event_form"):
    st.markdown("**تسجيل نتيجة حدث واقعي للمقارنة**")
    obs_dmg = st.number_input("الضرر الفعلي الملاحظ", min_value=0.0, value=50.0)
    conf = st.slider("مستوى الثقة في البيانات (%)", 0, 100, 85)
    submit_event = st.form_submit_button("حفظ في قاعدة البيانات")
    
    if submit_event:
        rec = {
            "Model": "MVP-Final-v1.0",
            "Scenario": f"Shock on {shock_node}",
            "Predicted Expected Damage": total_dmg,
            "Observed Damage": obs_dmg,
            "Confidence (%)": conf
        }
        log_event_to_db(rec)
        st.success("تم تسجيل الأحداث بنجاح في قاعدة البيانات الدائمة!")
        st.rerun()
        
