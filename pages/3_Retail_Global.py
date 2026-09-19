import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Retail Dashboard", page_icon="🛒", layout="wide")

# Theme Colors
AZUL_RETAIL = "#0052cc"
VERDE_PROFIT = "#36B37E"
ROJO_LOSS = "#FF5630"
FONDO = "rgba(255,255,255,0.05)"

st.markdown(f"""
    <style>
    .kpi-card {{ background-color: {FONDO}; padding: 20px; border-radius: 10px; border-top: 3px solid {AZUL_RETAIL}; text-align: center; }}
    .kpi-title {{ font-size: 1rem; color: #A0AEC0; }}
    .kpi-value {{ font-size: 2.2rem; font-weight: bold; color: white; }}
    </style>
""", unsafe_allow_html=True)

st.title("🛒 Global Retail Analytics")
st.markdown("Análisis de rentabilidad y distribución geográfica para e-commerce masivo.")

@st.cache_data
def load_retail():
    db_path = "dashboard_data.db"
    if not os.path.exists(db_path): return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql("SELECT * FROM retail_total", conn)
        # Parse numbers
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce').fillna(0)
        df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

df = load_retail()
if df.empty:
    st.warning("Datos no encontrados. Ejecuta etl.py.")
    st.stop()

# Filtros
col_f1, col_f2 = st.columns(2)
with col_f1:
    mercados = ["Todos"] + list(df['market'].dropna().unique())
    mercado_sel = st.selectbox("Mercado", mercados)
with col_f2:
    categorias = ["Todas"] + list(df['category'].dropna().unique())
    cat_sel = st.selectbox("Categoría", categorias)

df_filt = df.copy()
if mercado_sel != "Todos": df_filt = df_filt[df_filt['market'] == mercado_sel]
if cat_sel != "Todas": df_filt = df_filt[df_filt['category'] == cat_sel]

# KPIs
sales = df_filt['sales'].sum()
profit = df_filt['profit'].sum()
margin = (profit / sales * 100) if sales > 0 else 0

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Sales</div><div class='kpi-value'>${sales:,.2f}</div></div>", unsafe_allow_html=True)
with c2: 
    color = VERDE_PROFIT if profit > 0 else ROJO_LOSS
    st.markdown(f"<div class='kpi-card' style='border-color:{color}'><div class='kpi-title'>Total Profit</div><div class='kpi-value' style='color:{color}'>${profit:,.2f}</div></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Profit Margin</div><div class='kpi-value'>{margin:.1f}%</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
col_ch1, col_ch2 = st.columns([2, 1])

with col_ch1:
    st.markdown("### 🗺️ Mapa de Calor Global de Ventas")
    df_country = df_filt.groupby('country')['sales'].sum().reset_index()
    # Need to match country names to plotly's built-in map. 
    fig_map = px.choropleth(df_country, locations='country', locationmode='country names', color='sales',
                            color_continuous_scale="Viridis", title="Ventas por País")
    fig_map.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)', showcoastlines=False), paper_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig_map, use_container_width=True)

with col_ch2:
    st.markdown("### 📦 Rentabilidad por Sub-Categoría")
    df_sub = df_filt.groupby('sub.category')['profit'].sum().reset_index().sort_values('profit', ascending=True).tail(10)
    fig_bar = px.bar(df_sub, x='profit', y='sub.category', orientation='h', 
                     color='profit', color_continuous_scale=[ROJO_LOSS, VERDE_PROFIT])
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# ==============================================================================
# 🤖 BOTÓN FLOTANTE: AGENTE IA CON OPENAI (LangGraph)
# ==============================================================================
import agent_utils

contexto_retail = "Dashboard Retail Global: E-commerce masivo. Análisis de rentabilidad, ganancias (profit), ventas (sales) y distribución geográfica."
ejemplos_retail = """
**🔍 Consultas Básicas**
1. "¿Cuántos países distintos tienen ventas registradas?"
2. "Dime los nombres de las 3 sub-categorías principales."
3. "¿Cuál es el mercado (market) con mayor presencia?"
4. "¿Existen ventas con ganancias (profit) negativas?"

**🧮 Matemáticas y Agrupaciones**
5. "¿Cuál es la suma total de las ventas (sales)?"
6. "Calcula la ganancia total (profit) de la categoría 'Technology'."
7. "Dime el promedio de ganancia por cada venta."
8. "Agrupa por mercado y dime cuál tiene las ventas más altas."
9. "¿Cuál es el país con el peor margen de ganancia?"

**📈 Gráficas y Análisis Complejo**
10. "Genera una gráfica de barras con las 5 sub-categorías más rentables."
11. "Haz un gráfico de pastel mostrando las ventas por categoría."
12. "Genera un diagrama de dispersión (scatter) de Ventas vs Ganancias."

**💾 Exportación de Reportes**
13. "Exporta a Excel las ventas donde hubo pérdida (profit menor a cero)."
14. "Genera un reporte PDF con el top 10 de países con más ventas."
15. "Exporta a Excel un resumen de ventas totales agrupadas por mercado."
"""
agent_utils.render_agent_chat(df_filt, contexto_retail, "retail", ejemplos_retail)
