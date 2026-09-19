import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(page_title="Logística Aérea", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    .kpi-card { background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border-top: 3px solid #00B8D9; text-align: center; }
    h1, h2, h3 { color: white; }
    </style>
""", unsafe_allow_html=True)

st.title("✈️ Logística Global: Tráfico Aéreo Intercontinental")
st.markdown("Visualización en 3D de rutas de transporte, carga y pasajeros.")

@st.cache_data
def load_flights():
    db_path = "dashboard_data.db"
    if not os.path.exists(db_path): return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql("SELECT * FROM flights_total", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

df = load_flights()
if df.empty:
    st.warning("Datos no encontrados. Ejecuta etl.py.")
    st.stop()

# KPIs
total_vuelos = len(df)
total_pax = df['passengers'].sum()
demorados = len(df[df['status'] == 'Demorado'])

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='kpi-card'><div>Vuelos Activos</div><h2 style='margin:0;'>{total_vuelos:,}</h2></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='kpi-card'><div>Pasajeros en Tránsito</div><h2 style='margin:0;'>{total_pax:,}</h2></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='kpi-card' style='border-color:#FFAB00'><div>Vuelos Demorados</div><h2 style='margin:0;color:#FFAB00'>{demorados:,}</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3D Globe Map
st.markdown("### 🌍 Mapa de Rutas en Vivo")

fig = go.Figure()

# Add flight paths
for i in range(len(df)):
    color = '#00B8D9' if df['status'].iloc[i] == 'A Tiempo' else ('#FFAB00' if df['status'].iloc[i] == 'Demorado' else '#FF5630')
    fig.add_trace(
        go.Scattergeo(
            locationmode = 'ISO-3',
            lon = [df['origin_lon'].iloc[i], df['dest_lon'].iloc[i]],
            lat = [df['origin_lat'].iloc[i], df['dest_lat'].iloc[i]],
            mode = 'lines',
            line = dict(width = 1, color = color),
            opacity = 0.5,
            hoverinfo='text',
            text=f"{df['airline_name'].iloc[i]}: {df['origin_city'].iloc[i]} -> {df['dest_city'].iloc[i]} ({df['status'].iloc[i]})"
        )
    )

fig.update_layout(
    title_text = 'Conexiones Globales de Vuelo',
    showlegend = False,
    geo = dict(
        projection_type = 'orthographic',
        showland = True,
        landcolor = 'rgb(30, 30, 30)',
        countrycolor = 'rgb(50, 50, 50)',
        lakecolor = 'rgb(10, 10, 10)',
        bgcolor = 'rgba(0,0,0,0)',
        showocean = True,
        oceancolor = 'rgb(10, 10, 10)',
    ),
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=0, r=0, t=40, b=0),
    height=600
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
col_b1, col_b2 = st.columns(2)
with col_b1:
    st.markdown("### 🏢 Top 10 Aerolíneas Activas")
    df_top = df['airline_name'].value_counts().head(10).reset_index()
    df_top.columns = ['Aerolínea', 'Vuelos']
    fig_bar = px.bar(df_top, x='Vuelos', y='Aerolínea', orientation='h', color_discrete_sequence=['#00B8D9'])
    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b2:
    st.markdown("### 📊 Estado de los Vuelos")
    fig_pie = px.pie(df, names='status', color_discrete_map={'A Tiempo': '#00B8D9', 'Demorado': '#FFAB00', 'Cancelado': '#FF5630'}, hole=0.5)
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig_pie, use_container_width=True)
