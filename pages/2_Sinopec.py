import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Sinopec HSE Dashboard",
    page_icon="👷",
    layout="wide",
)

# Colors
ROJO_SINOPEC = "#E60000"
GRIS_OSCURO = "#333333"
BLANCO = "#FFFFFF"
VERDE_CERRADO = "#4CAF50"
AMARILLO_ABIERTO = "#FFC107"
FONDO_TARJETA = "rgba(255,255,255,0.05)"

# Custom CSS
st.markdown(f"""
    <style>
    .metric-card {{
        background-color: {FONDO_TARJETA};
        border-top: 3px solid {ROJO_SINOPEC};
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        margin-bottom: 15px;
    }}
    .metric-title {{
        color: #A0AEC0;
        font-size: 0.9rem;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .metric-value {{
        color: {BLANCO};
        font-size: 2rem;
        font-weight: bold;
    }}
    h1, h2, h3, h4 {{
        color: {BLANCO};
    }}
    .stPlotlyChart {{
        background-color: {FONDO_TARJETA};
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    </style>
""", unsafe_allow_html=True)

st.title("👷 Dashboard de Gestión HSE - Sinopec")
st.markdown("Auditoría y Control de Puntos de Acción de Seguridad (Proyecto Tuxpan 2D).")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    db_path = "dashboard_data.db"
    if not os.path.exists(db_path):
        st.error(f"Base de datos no encontrada. Ejecuta etl.py primero.")
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql("SELECT * FROM sinopec_total", conn)
    except:
        conn.close()
        return pd.DataFrame()
    conn.close()
    
    # Limpieza específica de Sinopec
    # Remover filas de totales al final del Excel (donde estado es raro)
    df = df[df['estado_abierto'].isin([1, 0, None]) | df['estado_cerrado'].isin([1, 0, None])]
    # Remove rows where all statuses are NaN to be safe, but actually let's just create a unified status
    df['Estado'] = df.apply(lambda x: 'Cerrado' if x['estado_cerrado'] == 1 else ('Abierto' if x['estado_abierto'] == 1 else 'Desconocido'), axis=1)
    df = df[df['Estado'] != 'Desconocido'] # Filter out garbage summary rows
    
    if 'fecha_de_reporte' in df.columns:
        df['fecha_de_reporte'] = pd.to_datetime(df['fecha_de_reporte'], errors='coerce')
        
    for col in ['departamento', 'fuente', 'responsable', 'categoria_de_riesgo']:
        if col in df.columns:
            df[col] = df[col].fillna('No Especificado')
            
    return df

df = load_data()

if df.empty:
    st.warning("No hay datos de Sinopec disponibles en la base de datos.")
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filtros HSE")
st.sidebar.markdown("---")

departamentos = ["Todos"] + sorted(list(df['departamento'].unique()))
dep_sel = st.sidebar.selectbox("Departamento", departamentos)

responsables = ["Todos"] + sorted(list(df['responsable'].unique()))
resp_sel = st.sidebar.selectbox("Responsable", responsables)

estados = ["Todos", "Abierto", "Cerrado"]
est_sel = st.sidebar.selectbox("Estado", estados)

# Aplicar filtros
df_filtered = df.copy()
if dep_sel != "Todos":
    df_filtered = df_filtered[df_filtered['departamento'] == dep_sel]
if resp_sel != "Todos":
    df_filtered = df_filtered[df_filtered['responsable'] == resp_sel]
if est_sel != "Todos":
    df_filtered = df_filtered[df_filtered['Estado'] == est_sel]

# --- KPIs ROW ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_puntos = len(df_filtered)
abiertos = len(df_filtered[df_filtered['Estado'] == 'Abierto'])
cerrados = len(df_filtered[df_filtered['Estado'] == 'Cerrado'])
tasa_cumplimiento = (cerrados / total_puntos * 100) if total_puntos > 0 else 0

with kpi1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Puntos de Acción</div>
            <div class="metric-value">{total_puntos}</div>
        </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
        <div class="metric-card" style="border-top-color: {AMARILLO_ABIERTO}">
            <div class="metric-title">Puntos Abiertos (Pendientes)</div>
            <div class="metric-value" style="color:{AMARILLO_ABIERTO}">{abiertos}</div>
        </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
        <div class="metric-card" style="border-top-color: {VERDE_CERRADO}">
            <div class="metric-title">Puntos Cerrados (Resueltos)</div>
            <div class="metric-value" style="color:{VERDE_CERRADO}">{cerrados}</div>
        </div>
    """, unsafe_allow_html=True)
with kpi4:
    color_tasa = VERDE_CERRADO if tasa_cumplimiento > 80 else AMARILLO_ABIERTO if tasa_cumplimiento > 50 else ROJO_SINOPEC
    st.markdown(f"""
        <div class="metric-card" style="border-top-color: {color_tasa}">
            <div class="metric-title">Tasa de Cumplimiento</div>
            <div class="metric-value" style="color:{color_tasa}">{tasa_cumplimiento:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)

# --- CHARTS ---
st.markdown("### 📊 Análisis de Desempeño")
col1, col2 = st.columns([2, 1])

with col1:
    # Evolución Temporal
    if 'fecha_de_reporte' in df_filtered.columns and not df_filtered['fecha_de_reporte'].isnull().all():
        df_time = df_filtered.groupby([df_filtered['fecha_de_reporte'].dt.to_period('M'), 'Estado']).size().reset_index(name='Cantidad')
        df_time['fecha_de_reporte'] = df_time['fecha_de_reporte'].astype(str)
        fig_time = px.bar(df_time, x='fecha_de_reporte', y='Cantidad', color='Estado',
                          title="Evolución de Puntos de Acción por Mes",
                          color_discrete_map={"Abierto": AMARILLO_ABIERTO, "Cerrado": VERDE_CERRADO},
                          barmode='group')
        fig_time.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO)
        st.plotly_chart(fig_time, use_container_width=True)

with col2:
    # Distribución de Estados
    fig_pie = px.pie(names=['Abierto', 'Cerrado'], values=[abiertos, cerrados], 
                     title="Proporción de Resolución",
                     color_discrete_sequence=[AMARILLO_ABIERTO, VERDE_CERRADO], hole=0.5)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO)
    st.plotly_chart(fig_pie, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    # Categoría de Riesgo
    if 'categoria_de_riesgo' in df_filtered.columns:
        riesgo_counts = df_filtered['categoria_de_riesgo'].value_counts().reset_index()
        riesgo_counts.columns = ['Categoría', 'Cantidad']
        fig_riesgo = px.bar(riesgo_counts, x='Cantidad', y='Categoría', orientation='h',
                            title="Clasificación por Categoría de Riesgo",
                            color_discrete_sequence=[ROJO_SINOPEC])
        fig_riesgo.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_riesgo, use_container_width=True)

with col4:
    # Top Responsables con tareas Abiertas
    df_abiertos = df_filtered[df_filtered['Estado'] == 'Abierto']
    if not df_abiertos.empty:
        resp_counts = df_abiertos['responsable'].value_counts().reset_index().head(5)
        resp_counts.columns = ['Responsable', 'Pendientes']
        fig_resp = px.bar(resp_counts, x='Responsable', y='Pendientes',
                          title="Top 5 Responsables con Más Puntos Abiertos",
                          color_discrete_sequence=[AMARILLO_ABIERTO])
        fig_resp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO)
        st.plotly_chart(fig_resp, use_container_width=True)
    else:
        st.success("¡Excelente! No hay puntos de acción abiertos para los filtros seleccionados.")

# Data Table
st.markdown("---")
st.markdown("### 📝 Registro Detallado")
with st.expander("Ver Lista Completa de Puntos de Acción"):
    cols_to_show = ['no', 'fuente', 'departamento', 'fecha_de_reporte', 'situacion_observada/reportada', 'accion_correctiva_tomada_o_sugerida', 'responsable', 'Estado']
    display_df = df_filtered[[c for c in cols_to_show if c in df_filtered.columns]]
    st.dataframe(display_df, use_container_width=True)

# ==============================================================================
# 🤖 BOTÓN FLOTANTE: AGENTE IA CON OPENAI (LangGraph)
# ==============================================================================
import agent_utils

contexto_sinopec = "Dashboard Sinopec: Gestión HSE, Auditoría y Control de Puntos de Acción de Seguridad. Analiza responsables, categorías de riesgo y estados abiertos/cerrados."
ejemplos_sinopec = """
**🔍 Consultas Básicas**
1. "¿Cuántos puntos de acción hay en total?"
2. "¿Cuáles son los departamentos involucrados?"
3. "Dime los nombres de todos los responsables que tienen tareas asignadas."
4. "¿Cuáles son las fuentes de donde provienen más reportes?"

**🧮 Matemáticas y Agrupaciones**
5. "¿Cuántos puntos de acción están en estado 'Abierto' y cuántos en 'Cerrado'?"
6. "Cuenta cuántos puntos de acción tiene asignados cada responsable."
7. "¿Cuál es el departamento con más puntos de acción registrados?"
8. "Dime qué porcentaje de las tareas ya están en estado Cerrado."
9. "Agrupa los puntos por categoría de riesgo y dime cuántos hay de cada una."

**📈 Gráficas y Análisis Complejo**
10. "Genera una gráfica de barras con el top 5 de responsables con más puntos."
11. "Genera un gráfico de pastel mostrando la proporción de puntos Abiertos vs Cerrados."
12. "Genera una gráfica mostrando los departamentos con más incidencias."

**💾 Exportación de Reportes**
13. "Exporta a PDF la tabla de los 10 puntos de acción más recientes."
14. "Exporta a Excel todos los puntos que estén en estado 'Abierto'."
15. "Hazme un reporte en Excel de las tareas agrupadas por responsable."
"""
agent_utils.render_agent_chat(df_filtered, contexto_sinopec, "sinopec", ejemplos_sinopec)
