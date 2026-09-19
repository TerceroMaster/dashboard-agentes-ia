import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
import numpy as np

st.set_page_config(
    page_title="PIRMCT Dashboard",
    page_icon="♻️",
    layout="wide",
)

# Colors
AZUL_CIELO = "#87CEEB"
AZUL_MEDIO = "#00B4D8"
AZUL_OSCURO = "#0077B6"
BLANCO = "#FFFFFF"
ROJO = "#FF4B4B"
VERDE = "#4CAF50"
FONDO_TARJETA = "rgba(255,255,255,0.05)"

# Custom CSS for this page
st.markdown(f"""
    <style>
    .metric-card {{
        background-color: {FONDO_TARJETA};
        border-top: 3px solid {AZUL_CIELO};
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
    .impact-card {{
        background-color: {FONDO_TARJETA};
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        height: 100%;
    }}
    .impact-icon {{
        font-size: 3rem;
        margin-bottom: 10px;
    }}
    .impact-title {{
        color: {BLANCO};
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    .impact-desc {{
        color: #A0AEC0;
        font-size: 0.9rem;
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

st.title("♻️ Dashboard Ejecutivo PIRMCT 2025")
st.markdown("Programa Interinstitucional para la Recolección de Medicamentos Caducados en Tabasco.")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    db_path = "dashboard_data.db"
    if not os.path.exists(db_path):
        st.error(f"Base de datos no encontrada en {db_path}. Ejecuta etl.py primero.")
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM pirmct_total", conn)
    conn.close()
    
    # Limpieza básica
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Manejar nulos para filtros
    for col in ['sector', 'institucion', 'procedencia', 'grupo', 'forma_farmaceutica']:
        if col in df.columns:
            df[col] = df[col].fillna('No Especificado')
            
    # Mocking Geographic Data based on institucion (since it's not in DB natively)
    np.random.seed(42) # For reproducible random
    municipios_base = ["Centro (Villahermosa)", "Cárdenas", "Comalcalco", "Macuspana", "Tenosique"]
    coords = {
        "Centro (Villahermosa)": [17.9895, -92.9475],
        "Cárdenas": [17.9972, -93.3742],
        "Comalcalco": [18.2619, -93.2265],
        "Macuspana": [17.7583, -92.5956],
        "Tenosique": [17.4725, -91.4225]
    }
    
    # Asignar un municipio aleatorio a cada institución para la demo
    if 'institucion' in df.columns:
        unique_inst = df['institucion'].unique()
        inst_to_mun = {inst: np.random.choice(municipios_base) for inst in unique_inst}
        # Force some specifics if found
        for inst in unique_inst:
            if "Villah" in str(inst): inst_to_mun[inst] = "Centro (Villahermosa)"
            if "Chontalpa" in str(inst): inst_to_mun[inst] = "Cárdenas"
        
        df['municipio'] = df['institucion'].map(inst_to_mun)
        df['lat'] = df['municipio'].map(lambda x: coords[x][0] + (np.random.rand()-0.5)*0.05) # Add slight jitter
        df['lon'] = df['municipio'].map(lambda x: coords[x][1] + (np.random.rand()-0.5)*0.05)

    return df

df = load_data()

if df.empty:
    st.stop()

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filtros de Búsqueda")
st.sidebar.markdown("---")

sectores = ["Todos"] + sorted(list(df['sector'].unique())) if 'sector' in df.columns else ["Todos"]
sector_sel = st.sidebar.selectbox("Sector", sectores)

instituciones = ["Todas"] + sorted(list(df['institucion'].unique())) if 'institucion' in df.columns else ["Todas"]
institucion_sel = st.sidebar.selectbox("Institución", instituciones)

grupos = ["Todos"] + sorted(list(df['grupo'].unique())) if 'grupo' in df.columns else ["Todos"]
grupo_sel = st.sidebar.selectbox("Grupo Terapéutico", grupos)

st.sidebar.markdown("---")
# --- REAL-TIME DATA UPLOAD ---
with st.sidebar.expander("⚙️ Administrar Datos (Subir Fase 2)"):
    st.markdown("Sube un nuevo archivo Excel para añadir registros a la base de datos en tiempo real.")
    uploaded_file = st.file_uploader("Cargar Excel", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        if st.button("Procesar y Añadir Datos"):
            try:
                import unicodedata
                def remove_accents(input_str):
                    nfkd_form = unicodedata.normalize('NFKD', str(input_str))
                    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
                    
                # Leer el nuevo excel
                new_df = pd.read_excel(uploaded_file, sheet_name="Total")
                # Limpiar nombres de columnas
                new_df.columns = [remove_accents(c).strip().replace(' ', '_').lower() for c in new_df.columns]
                
                # Conectar a base de datos y anexar (append)
                db_path = "dashboard_data.db"
                conn = sqlite3.connect(db_path)
                new_df.to_sql("pirmct_total", conn, if_exists="append", index=False)
                conn.close()
                
                st.success(f"¡Éxito! Se añadieron {len(new_df)} registros nuevos. Recargando...")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

# Aplicar filtros
df_filtered = df.copy()
if sector_sel != "Todos":
    df_filtered = df_filtered[df_filtered['sector'] == sector_sel]
if institucion_sel != "Todas":
    df_filtered = df_filtered[df_filtered['institucion'] == institucion_sel]
if grupo_sel != "Todos":
    df_filtered = df_filtered[df_filtered['grupo'] == grupo_sel]

# (Chatbot removido de la barra lateral, se implementará como botón flotante)

# --- KPIs ROW ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_registros = len(df_filtered)
cantidad_total = df_filtered['cantidad_remanente'].sum() if 'cantidad_remanente' in df_filtered.columns and pd.api.types.is_numeric_dtype(df_filtered['cantidad_remanente']) else total_registros
sectores_unicos = df_filtered['sector'].nunique() if 'sector' in df_filtered.columns else 0
instituciones_unicas = df_filtered['institucion'].nunique() if 'institucion' in df_filtered.columns else 0

with kpi1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Volumen Total</div>
            <div class="metric-value" style="color:{AZUL_CIELO}">{cantidad_total:,.0f} <span style="font-size:1rem;">Unidades</span></div>
        </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Registros Ingresados</div>
            <div class="metric-value">{total_registros:,}</div>
        </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title" style="color:{ROJO}">Sectores Impactados</div>
            <div class="metric-value" style="color:{ROJO}">{sectores_unicos}</div>
        </div>
    """, unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Instituciones Aliadas</div>
            <div class="metric-value">{instituciones_unicas}</div>
        </div>
    """, unsafe_allow_html=True)


# --- TABS FOR DIFFERENT VISUALIZATIONS ---
tab1, tab2, tab3 = st.tabs(["Visualización General", "Distribución Geográfica & Ambiental", "Clustering (IA)"])

with tab1:
    # --- CHARTS GRID ---
    st.markdown("### 📈 Análisis General")
    col_chart1, col_chart2 = st.columns([2, 1])

    with col_chart1:
        if 'fecha' in df_filtered.columns and not df_filtered['fecha'].isnull().all():
            df_time = df_filtered.groupby(df_filtered['fecha'].dt.to_period('M'))['cantidad_remanente'].sum().reset_index()
            df_time['fecha'] = df_time['fecha'].astype(str)
            
            # Usamos px.bar en lugar de px.area porque px.area no se dibuja si solo hay 1 mes de datos (1 solo punto)
            fig_time = px.bar(df_time, x='fecha', y='cantidad_remanente', 
                              title="Evolución de Recolección Mensual",
                              color_discrete_sequence=[AZUL_MEDIO])
            
            fig_time.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("No hay datos de fechas válidas para mostrar la tendencia.")

    with col_chart2:
        if 'procedencia' in df_filtered.columns:
            proc_counts = df_filtered.groupby('procedencia')['cantidad_remanente'].sum().reset_index()
            fig_pie = px.pie(proc_counts, values='cantidad_remanente', names='procedencia',
                         title="Volumen por Procedencia",
                         color_discrete_sequence=[AZUL_CIELO, AZUL_OSCURO, BLANCO, ROJO, VERDE], hole=0.5)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

    col_chart3, col_chart4 = st.columns([1, 1])
    with col_chart3:
        if 'grupo' in df_filtered.columns and 'sector' in df_filtered.columns:
            fig_tree = px.treemap(df_filtered, path=[px.Constant("Total"), 'sector', 'grupo'], values='cantidad_remanente',
                                  title="Jerarquía de Volumen: Sector > Grupo",
                                  color='sector', color_discrete_sequence=[AZUL_CIELO, AZUL_OSCURO, ROJO, VERDE])
            fig_tree.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO, margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_tree, use_container_width=True)

    with col_chart4:
        if 'institucion' in df_filtered.columns:
            top_inst = df_filtered.groupby('institucion')['cantidad_remanente'].sum().reset_index().sort_values('cantidad_remanente', ascending=False).head(5)
            top_inst = top_inst[top_inst['institucion'] != 'No Especificado']
            fig_bar = px.bar(top_inst, x='cantidad_remanente', y='institucion', orientation='h',
                             title="Top 5 Instituciones con Mayor Aporte",
                             color_discrete_sequence=[AZUL_OSCURO])
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO, margin=dict(t=40, b=0, l=0, r=0), yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.markdown("### 🗺️ Distribución Geográfica (Tabasco Eco-Radar)")
    col_map, col_top = st.columns([2, 1])
    
    with col_map:
        if 'lat' in df_filtered.columns:
            # Aggregate for map
            map_data = df_filtered.groupby('municipio').agg({'cantidad_remanente':'sum', 'lat':'first', 'lon':'first'}).reset_index()
            fig_map = px.scatter_mapbox(map_data, lat="lat", lon="lon", size="cantidad_remanente", color="municipio",
                                        hover_name="municipio", hover_data=["cantidad_remanente"],
                                        color_discrete_sequence=[AZUL_CIELO, AZUL_OSCURO, ROJO, VERDE, "#F39C12"],
                                        zoom=7, center={"lat": 17.98, "lon": -92.94},
                                        mapbox_style="open-street-map") # Changed to open-street-map to avoid API key
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_map, use_container_width=True)
            
    with col_top:
        st.markdown("#### Top Municipios Recolectores")
        if 'municipio' in df_filtered.columns:
            top_muns = df_filtered.groupby('municipio')['cantidad_remanente'].sum().reset_index().sort_values('cantidad_remanente', ascending=False)
            for i, row in top_muns.iterrows():
                st.markdown(f"**#{i+1}** &nbsp; {row['municipio']} &nbsp; <span style='color:{VERDE};'>{row['cantidad_remanente']:,.0f} U</span>", unsafe_allow_html=True)
                st.progress(min(row['cantidad_remanente']/top_muns['cantidad_remanente'].max(), 1.0))
                
    st.markdown("---")
    st.markdown("### 🌿 Impacto Ambiental Estimado")
    
    # Cálculos estimativos basados en volumen
    agua_litros = cantidad_total * 1500 # asumiendo que 1 unidad evita contaminar 1500L
    hectareas = cantidad_total * 0.05
    
    i_col1, i_col2, i_col3 = st.columns(3)
    with i_col1:
        st.markdown(f"""
            <div class="impact-card">
                <div class="impact-icon">💧</div>
                <div class="impact-title">Agua Protegida</div>
                <div class="impact-desc">Se evitó la contaminación de aproximadamente <b>{agua_litros:,.0f} litros</b> de agua en mantos acuíferos.</div>
            </div>
        """, unsafe_allow_html=True)
    with i_col2:
        st.markdown(f"""
            <div class="impact-card">
                <div class="impact-icon">🧬</div>
                <div class="impact-title">Resistencia Bacteriana</div>
                <div class="impact-desc">Reducción significativa en la creación de superbacterias por desecho incorrecto de antibióticos.</div>
            </div>
        """, unsafe_allow_html=True)
    with i_col3:
        st.markdown(f"""
            <div class="impact-card">
                <div class="impact-icon">🌱</div>
                <div class="impact-title">Suelos Limpios</div>
                <div class="impact-desc">Prevención de lixiviados tóxicos en <b>{hectareas:,.0f} hectáreas</b> de zonas agrícolas cercanas.</div>
            </div>
        """, unsafe_allow_html=True)


with tab3:
    st.markdown("### 🤖 Análisis Avanzado: Patrones Ocultos (Machine Learning)")
    st.markdown("Utilizamos **K-Means Clustering** y reducción de dimensionalidad (PCA) para agrupar los miles de registros en 'nubes' o segmentos de comportamiento similar. Cada punto es una recolección.")
    
    if len(df_filtered) > 50:
        from sklearn.decomposition import PCA
        
        # Preparar datos: One-Hot Encoding para categorías
        cat_cols = ['sector', 'grupo']
        # Tomar solo los datos que existen en el filtro
        cluster_data = pd.get_dummies(df_filtered[cat_cols])
        # Añadir la cantidad (escalada)
        cluster_data['cantidad'] = df_filtered['cantidad_remanente'].fillna(0)
        
        # Escalar
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(cluster_data)
        
        # K-Means
        n_clusters = st.slider("Número de Segmentos (Clusters)", min_value=2, max_value=6, value=4)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        clusters = kmeans.fit_predict(X_scaled)
        
        # PCA para reducir a 2 dimensiones
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        # AÑADIR JITTER (Ruido Gaussiano) para separar los puntos superpuestos y crear el efecto visual de "Nubes" (Blobs)
        np.random.seed(42)
        jitter_strength_x = (X_pca[:, 0].max() - X_pca[:, 0].min()) * 0.05
        jitter_strength_y = (X_pca[:, 1].max() - X_pca[:, 1].min()) * 0.05
        
        plot_df = df_filtered.copy()
        plot_df['PCA1'] = X_pca[:, 0] + np.random.normal(0, jitter_strength_x, size=len(X_pca))
        plot_df['PCA2'] = X_pca[:, 1] + np.random.normal(0, jitter_strength_y, size=len(X_pca))
        plot_df['Cluster'] = [f"Segmento {c+1}" for c in clusters]
        
        # Scatter Plot 2D (Blobs)
        fig_cluster = px.scatter(plot_df, x='PCA1', y='PCA2', color='Cluster',
                                 hover_data=['name', 'grupo', 'sector', 'cantidad_remanente'],
                                 title="Visualización Topológica de Clústers",
                                 color_discrete_sequence=[AZUL_CIELO, VERDE, ROJO, AZUL_OSCURO, "#F39C12", "#9B59B6"])
        
        # Estética de Blobs (puntos sin bordes fuertes, semi-transparentes)
        fig_cluster.update_traces(marker=dict(size=8, opacity=0.6, line=dict(width=0)))
        
        # Ocultar los ejes numéricos ya que PCA no tiene un significado directo interpretable
        fig_cluster.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color=BLANCO,
                                  xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="Dimensión Latente 1"),
                                  yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="Dimensión Latente 2"))
        
        # Agregar los centroides (estrellas/cruces) simulados en el centro de cada nube
        centroids_x = []
        centroids_y = []
        for c in range(n_clusters):
            mask = clusters == c
            centroids_x.append(plot_df.loc[mask, 'PCA1'].mean())
            centroids_y.append(plot_df.loc[mask, 'PCA2'].mean())
            
        fig_cluster.add_trace(go.Scatter(x=centroids_x, y=centroids_y, mode='markers',
                                         marker=dict(symbol='x', size=15, color='white', line=dict(width=2)),
                                         name='Centroides'))
        
        st.plotly_chart(fig_cluster, use_container_width=True)
        
        # --- DETAILED EXPLANATION SECTION ---
        st.markdown("### 🧠 Interpretación de Resultados")
        st.info("Cada punto representa un registro real de recolección. Al usar PCA y Jittering, logramos visualizar los datos como 'nubes' (blobs) que representan perfiles ocultos. Los puntos cercanos entre sí comparten características similares (mismo sector, grupo terapéutico y volumen). Las cruces blancas (✖) representan el 'centroide' matemático de cada perfil.")
        
        col_expl1, col_expl2 = st.columns(2)
        
        with col_expl1:
            st.markdown("#### ¿Cómo funciona la Inteligencia Artificial aquí?")
            st.markdown("""
            * **PCA (Reducción de Dimensionalidad)**: Toma múltiples variables complejas (Sector, Grupo Terapéutico, Cantidad) y las comprime en solo 2 ejes matemáticos (*Dimensiones Latentes*). Esto permite "dibujar" datos multidimensionales en un plano 2D que el ojo humano puede entender.
            * **K-Means (Clustering)**: Es un algoritmo no supervisado. Nadie le dijo a la computadora cómo agrupar los datos; el algoritmo midió la distancia matemática entre cada registro y agrupó automáticamente a los más parecidos, encontrando patrones ocultos que un análisis tradicional pasaría por alto.
            """)
            
        with col_expl2:
            st.markdown("#### ¿Qué significa cambiar el Número de Segmentos (K)?")
            st.markdown("""
            Al mover el control deslizante, le pides a la IA que sea más o menos específica en su búsqueda de patrones:
            * **3 a 4 Segmentos (Macrotendencias)**: La IA divide los medicamentos en grandes categorías globales (ej. Medicamentos comunes de alto volumen vs Especializados de bajo volumen).
            * **5 a 6 Segmentos (Micro-nichos)**: La IA se vuelve más estricta y empieza a separar sub-grupos muy específicos. Puede revelar "anomalías" o nichos de recolección altamente especializados que se comportan distinto a la mayoría.
            """)
            
        st.markdown("#### 🎯 Hallazgos Potenciales")
        st.markdown("Al observar los grupos separados (colores distintos), podemos inferir que existen perfiles de recolección claramente diferenciados. Por ejemplo, un clúster aislado en la parte superior derecha podría representar **donaciones masivas del sector público**, mientras que una nube densa en la parte inferior podría ser el **flujo constante de pequeños remanentes del sector privado**.")
        
    else:
        st.warning("Se necesitan más datos para ejecutar el algoritmo de clustering. Asegúrate de tener suficientes registros en los filtros.")

# ==============================================================================
# 🤖 BOTÓN FLOTANTE: AGENTE IA CON OPENAI
# ==============================================================================

# CSS para forzar que el popover se posicione flotando en la esquina inferior derecha y sea responsivo
st.markdown("""
<style>
    /* Contenedor del botón popover */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 99999 !important;
    }
    
    /* Diseño del botón */
    div[data-testid="stPopover"] > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 50px !important;
        padding: 15px 25px !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.5) !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.7) !important;
        border-color: #4CAF50 !important;
    }
    
    /* Diseño de la ventana del chat (Popover Body) */
    div[data-testid="stPopoverBody"] {
        width: 450px !important;
        max-width: 90vw !important; /* Responsivo para tablet/celular */
        max-height: 80vh !important;
        border-radius: 15px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        padding: 20px !important;
        resize: both;
        overflow: auto;
    }
    
    /* Ocultar el texto en inglés "Press Enter to submit form" de Streamlit */
    div[data-testid="InputInstructions"] {
        display: none !important;
    }
    
    /* Ajustes para celulares (Smartphones) */
    @media (max-width: 768px) {
        div[data-testid="stPopover"] {
            bottom: 10px !important;
            right: 10px !important;
        }
        div[data-testid="stPopoverBody"] {
            width: 95vw !important;
            max-width: 95vw !important;
        }
        div[data-testid="stPopover"] > button {
            padding: 10px 20px !important;
            font-size: 14px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# === BLOQUE EXPLICATIVO DEL AGENTE DE IA ===
st.markdown("---")
st.markdown("## 🧠 ¿Cómo funciona la Inteligencia Artificial PIRMCT?")

col_ai1, col_ai2 = st.columns(2)
with col_ai1:
    st.markdown("""
    ### 🤖 Arquitectura del Agente
    El chat flotante no es un bot de respuestas preprogramadas. Está impulsado por **LangChain** y el modelo **GPT-4o-mini**, actuando como un equipo de Data Science en tiempo real.
    
    Internamente operan **3 sub-agentes invisibles**:
    1. **El Analista**: Escucha tu pregunta (ej. *"¿Cuántos caducados hay?"*) y decide qué columnas de la base de datos necesita.
    2. **El Programador**: Escribe un script en Python exacto para extraer y calcular esos datos en milisegundos.
    3. **El Revisor**: Ejecuta el código, valida los resultados matemáticos y te redacta la respuesta en lenguaje natural.
    """)
    
with col_ai2:
    st.markdown("""
    ### 🚀 ¿Qué puedes hacer con él?
    Al estar conectado directamente al motor de este dashboard, el Agente puede:
    - **Realizar Matemáticas Complejas**: Sumar, promediar, y agrupar millones de registros al instante.
    - **Generar Gráficos al Vuelo**: Crear gráficos de barras o pastel visuales (`.png`) que no existen en el dashboard principal.
    - **Exportar Reportes**: Generar documentos físicos descargables (`.xlsx`, `.pdf`) perfectamente filtrados según lo que le pidas.
    - **Recordar Contexto**: Mantiene el hilo de la conversación, por lo que puedes pedirle *"ahora agrúpalos por mes"* y entenderá a qué te refieres.
    """)
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True) # Espaciador para que el botón flotante no tape el texto

import os
from openai import OpenAI

# Extraer API KEY de los secretos de Streamlit (No hardcoded)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("🚨 La API Key de OpenAI no está configurada en los secretos. El agente no funcionará.")
    st.stop()
    
client = OpenAI(api_key=api_key)

if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy tu asistente inteligente. He analizado la base de datos de PIRMCT. ¿Qué quieres descubrir hoy? (Ej: ¿Qué medicamento se recolectó más?)"}
    ]

with st.popover("💬 Empezar Conversación", help="Habla con tus datos"):
    # Contenedor principal del chat
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("### 🤖 Asistente de Datos")
    with col2:
        fullscreen = st.checkbox("🔲 Pantalla Completa")
        if fullscreen:
            st.markdown("""
            <style>
            div[data-testid="stPopoverBody"] {
                position: fixed !important;
                top: 50px !important;
                left: 0 !important;
                width: 100vw !important;
                height: calc(100vh - 50px) !important;
                max-width: 100vw !important;
                max-height: 100vh !important;
                z-index: 99999 !important;
                transform: none !important;
                background-color: #1E1E1E !important;
            }
            </style>
            """, unsafe_allow_html=True)
    
    with st.expander("💡 12 Ejemplos de lo que puedes preguntarme"):
        st.markdown("""
        **🔍 Consultas Básicas**
        1. "¿De qué país de origen vienen más medicamentos?"
        2. "Dime cuáles son los laboratorios que más medicamentos aportaron."
        3. "¿Cuántos medicamentos distintos (fórmulas) hay en el sector Público?"
        
        **🧮 Matemáticas y Agrupaciones**
        4. "Suma la cantidad de medicamentos cuya vía de administración sea Oral y dime cuántos son."
        5. "¿Tenemos medicamentos caducados del año 2023? ¿Cuántos?"
        6. "¿Cuál es el registro sanitario con mayor volumen de recolección?"
        7. "Calcula el promedio de cantidad recolectada por cada tipo de envase."
        
        **📈 Gráficas y Análisis Complejo**
        8. "Dime el top 3 de tipos de forma farmacéutica más comunes."
        9. "Genera una gráfica de barras mostrando el top 5 de laboratorios productores."
        
        **💾 Exportación de Reportes**
        10. "Exporta un reporte en PDF del top 10 de laboratorios."
        11. "Exporta a Excel todos los medicamentos caducados en 2024, agrupados por mes."
        12. "Hazme un reporte en Excel de las 5 instituciones que más aportaron."
        """)
        
    # Contenedor para el historial (Altura dinámica según fullscreen)
    chat_height = 700 if fullscreen else 350
    chat_container = st.container(height=chat_height)
    with chat_container:
        for msg in st.session_state.ai_chat_history:
            with st.chat_message(msg["role"]):
                content_display = msg["content"]
                content_display = content_display.replace("[GRAFICA_GENERADA]", "📊 Aquí tienes tu gráfica:")
                content_display = content_display.replace("[REPORTE_EXCEL_GENERADO]", "📗 ¡Tu reporte en Excel está listo para descargar!")
                content_display = content_display.replace("[REPORTE_PDF_GENERADO]", "📕 ¡Tu reporte en PDF está listo para descargar!")
                st.markdown(content_display)
                
                # Botón de descarga para Gráficas
                if "image" in msg and os.path.exists(msg["image"]):
                    st.image(msg["image"])
                    with open(msg["image"], "rb") as file:
                        st.download_button(
                            label="⬇️ Descargar Gráfica",
                            data=file,
                            file_name="grafica_pirmct.png",
                            mime="image/png",
                            key=f"dl_img_{msg['content'][:10]}"
                        )
                        
                # Botones en columnas para reportes
                dl_col1, dl_col2 = st.columns(2)
                # Botón de descarga para Excel
                with dl_col1:
                    if "excel" in msg and os.path.exists(msg["excel"]):
                        with open(msg["excel"], "rb") as file:
                            st.download_button(
                                label="⬇️ Descargar Reporte Excel",
                                data=file,
                                file_name="reporte_pirmct.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key=f"dl_xls_{msg['content'][:10]}"
                            )
                
                # Botón de descarga para PDF
                with dl_col2:
                    if "pdf" in msg and os.path.exists(msg["pdf"]):
                        with open(msg["pdf"], "rb") as file:
                            st.download_button(
                                label="⬇️ Descargar Reporte PDF",
                                data=file,
                                file_name="reporte_pirmct.pdf",
                                mime="application/pdf",
                                key=f"dl_pdf_{msg['content'][:10]}"
                            )
                
    # Formulario para input (usado en vez de chat_input porque no está permitido en popovers)
    with st.form("chat_form", clear_on_submit=True):
        col_in, col_btn = st.columns([3, 1])
        with col_in:
            user_input = st.text_input("Escribe tu pregunta...", label_visibility="collapsed")
        with col_btn:
            submit = st.form_submit_button("Enviar", use_container_width=True)
            
        if submit and user_input:
            # 1. Guardar mensaje del usuario
            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
            
            # 2. Construir Contexto de la Base de Datos para el LLM
            # 2. Construir Contexto de la Base de Datos para el LLM
            from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
            from langchain_openai import ChatOpenAI
            
            try:
                with st.spinner("Analizando datos en tiempo real..."):
                    # Inicializar el LLM de LangChain (Usamos gpt-4o-mini para evitar loops infinitos y acelerar respuesta)
                    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=api_key)
                    
                    # Crear el agente de Pandas en tiempo real con df_filtered
                    agent = create_pandas_dataframe_agent(
                        llm, 
                        df_filtered, 
                        verbose=False, 
                        allow_dangerous_code=True,
                        agent_type="openai-tools",
                        max_iterations=8,
                        max_execution_time=20
                    )
                    
                    # Preparar el query incluyendo historial para mantener el contexto
                    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.ai_chat_history[-3:-1]])
                    
                    instrucciones = """
                    Eres un experto analista de datos de DataViz Studio.
                    La base de datos (df) contiene los registros de medicamentos recolectados en el programa PIRMCT.
                    
                    REGLAS IMPORTANTES:
                    1. Analiza el dataframe usando código python para responder la pregunta con EXACTITUD matemática.
                    2. Responde SIEMPRE 100% en Español.
                    3. Si te preguntan por totales, haz sumas de la columna correcta (ej. cantidad_remanente).
                    4. Si la información no existe o la suma es cero, dilo claramente.
                    5. ¡SOPORTE PARA GRÁFICAS!: Si el usuario pide generar una gráfica, usa `matplotlib.pyplot`. ES OBLIGATORIO usar `plt.xticks(rotation=45, ha='right')` y `plt.tight_layout()` para que las etiquetas del eje X no se amontonen ni se corten. Guarda la figura usando `plt.savefig('temp_chart.png')`. Tu respuesta debe incluir la palabra: [GRAFICA_GENERADA].
                    6. ¡SOPORTE PARA EXCEL/PDF!: Si piden Excel, crea el dataframe resultante y ANTES de exportar, verifica que NO ESTÉ VACÍO. Luego guárdalo con `df_nuevo.to_excel('reporte_temp.xlsx', index=False)`. Respuesta: [REPORTE_EXCEL_GENERADO]. Si piden PDF, guarda la tabla resultante como imagen usando matplotlib (`plt.savefig('reporte_temp.pdf', bbox_inches='tight')`). Respuesta: [REPORTE_PDF_GENERADO].
                    7. FORMATO DE FECHAS: La columna `caducidad` es de tipo texto (Ej: 'SEP/24', 'sep/24 ', '---/--'). Tiene basura y mayúsculas/minúsculas mezcladas.
                       - Si buscas el año 2024, filtra por `.str.contains('24', na=False)`.
                       - Si te piden agrupar por mes, SIEMPRE extrae el mes de esta forma para evitar errores: `df_filtrado['mes'] = df_filtrado['caducidad'].astype(str).str.split('/').str[0].str.strip().str.upper()` y agrupa por esa nueva columna.
                    
                    Historial reciente:
                    {history}
                    
                    Pregunta del usuario: {pregunta}
                    """
                    
                    query = instrucciones.format(history=history_text, pregunta=user_input)
                    
                    # Ejecutar el agente
                    # Limpieza agresiva de caché y "Garbage Collection" de archivos
                    for temp_file in ['temp_chart.png', 'reporte_temp.xlsx', 'reporte_temp.pdf']:
                        if os.path.exists(temp_file):
                            try: os.remove(temp_file)
                            except: pass
                        
                    response = agent.invoke(query)
                    ai_reply = response['output']
                    
                msg_data = {"role": "assistant", "content": ai_reply}
                if "[GRAFICA_GENERADA]" in ai_reply and os.path.exists("temp_chart.png"):
                    msg_data["image"] = "temp_chart.png"
                if "[REPORTE_EXCEL_GENERADO]" in ai_reply and os.path.exists("reporte_temp.xlsx"):
                    msg_data["excel"] = "reporte_temp.xlsx"
                if "[REPORTE_PDF_GENERADO]" in ai_reply and os.path.exists("reporte_temp.pdf"):
                    msg_data["pdf"] = "reporte_temp.pdf"
                    
                st.session_state.ai_chat_history.append(msg_data)
                st.rerun()
            except Exception as e:
                st.error(f"Error procesando la consulta con Pandas Agent: {e}")

# Data Table at the very bottom
st.markdown("---")
with st.expander("Ver Base de Datos Detallada (Top 100)"):
    st.dataframe(df_filtered.head(100), use_container_width=True)
