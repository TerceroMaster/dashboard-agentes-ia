import streamlit as st

st.set_page_config(
    page_title="DataViz Studio | Inicio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Landing Page
st.markdown("""
    <style>
    .main-header {
        font-size: 4rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #007BFF, #00C6FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A0AEC0;
        text-align: center;
        margin-bottom: 3rem;
    }
    .project-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 2rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .project-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 10px 20px rgba(0, 123, 255, 0.2);
        border: 1px solid rgba(0, 123, 255, 0.5);
    }
    .project-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #FFFFFF;
        margin-bottom: 1rem;
    }
    .project-desc {
        color: #CBD5E0;
        margin-bottom: 2rem;
    }
    /* Hide Streamlit standard components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


st.markdown('<p class="main-header">Data Analytics & BI Portfolio</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transformando datos en decisiones estratégicas a través de visualizaciones interactivas de alto impacto.</p>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("---")
st.markdown("### 🚀 Casos de Éxito Destacados y Alcance Analítico")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="project-card" style="min-height: 250px;">
            <h3 class="project-title">♻️ PIRMCT (Sostenibilidad)</h3>
            <div class="project-desc">
                <p><strong>De qué trata:</strong> Dashboard ejecutivo para el Programa de Recolección de Medicamentos Caducados en Tabasco.</p>
                <p><strong>Alcance:</strong> Procesamiento de +2,900 registros. Demuestra capacidades de filtrado dinámico, cálculo de impacto ambiental, mapeo geoespacial base y segmentación predictiva usando Machine Learning (Clustering).</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
with col2:
    st.markdown("""
        <div class="project-card" style="min-height: 250px;">
            <h3 class="project-title">👷 Sinopec (Auditoría HSE)</h3>
            <div class="project-desc">
                <p><strong>De qué trata:</strong> Plataforma de control de Seguridad Industrial e incidentes para el Proyecto Tuxpan 2D.</p>
                <p><strong>Alcance:</strong> Transformación de listas de auditoría crudas en KPIs accionables. Muestra habilidades para rastrear cuellos de botella operativos, cumplimiento de objetivos (SLA) y análisis de riesgos empresariales.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="project-card" style="min-height: 250px;">
            <h3 class="project-title">🛒 Global Retail (E-Commerce)</h3>
            <div class="project-desc">
                <p><strong>De qué trata:</strong> Análisis de rentabilidad de una tienda transnacional masiva.</p>
                <p><strong>Alcance:</strong> Ingesta de +50,000 transacciones. Destaca la capacidad de calcular márgenes de ganancia complejos, visualización financiera y mapeo de calor a nivel mundial para la toma de decisiones directivas.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
        <div class="project-card" style="min-height: 250px;">
            <h3 class="project-title">🧠 NLP Sentimiento (Twitter)</h3>
            <div class="project-desc">
                <p><strong>De qué trata:</strong> Clasificador de emociones mediante Inteligencia Artificial en Redes Sociales.</p>
                <p><strong>Alcance:</strong> Big Data y NLP. Limpieza matemática de 1.6 millones de interacciones, extrayendo las palabras clave exactas que generan reseñas positivas o quejas en tiempo real (Wordclouds).</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
        <div class="project-card" style="min-height: 250px;">
            <h3 class="project-title">✈️ Logística Global (Aérea)</h3>
            <div class="project-desc">
                <p><strong>De qué trata:</strong> Monitoreo de tráfico intercontinental de vuelos comerciales.</p>
                <p><strong>Alcance:</strong> Renderizado avanzado 3D. Creación de algoritmos geoespaciales para simular y rastrear interconexiones, demoras y volúmenes de carga entre las principales metrópolis del mundo.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
        <div class="project-card" style="min-height: 250px; border-style: dashed; border-color: #555; background: transparent; display: flex; flex-direction: column; justify-content: center;">
            <h3 class="project-title" style="color: #888;">🚀 Tu Empresa Aquí</h3>
            <p class="project-desc" style="color: #888; text-align: center;">Contáctanos para transformar tus datos en el próximo gran caso de éxito.</p>
        </div>
    """, unsafe_allow_html=True)

st.info("👉 **Selecciona cualquiera de los Dashboards en el menú de la izquierda para interactuar con ellos.**")

st.markdown("---")
st.markdown("### 💼 Nuestros Servicios")

s_col1, s_col2 = st.columns(2)
with s_col1:
    st.markdown("#### 📊 Modelado de Datos\nEstructuración y limpieza de bases de datos complejas para análisis óptimo.")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📈 Analítica Predictiva\nIntegración de modelos estadísticos y Machine Learning para predecir tendencias futuras.")

with s_col2:
    st.markdown("#### 💻 Dashboards Interactivos\nDiseño de interfaces web intuitivas para consumo de datos en tiempo real.")
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🤖 Agentes de Inteligencia Artificial\nCreación de Agentes de IA (texto, voz o multimodal) conectados directamente a tus datos corporativos, dándole vida, interactividad y usabilidad a tu información.")

st.markdown("---")
st.markdown("### 🤖 Interactúa con tus Datos (Demo de Agente IA)")
st.markdown("Imagina poder 'platicar' con tu base de datos en lugar de solo ver gráficas. Prueba esta simulación de nuestro Asistente de IA Corporativo:")

# --- CHAT SIMULATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu Agente de IA entrenado con los datos de tu empresa. Puedo buscar ventas, predecir tendencias o encontrar anomalías. ¿Qué te gustaría saber hoy?"}
    ]

# Mostrar historial del chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input del usuario
if prompt := st.chat_input("Ej: ¿Cuáles fueron las ganancias del mes pasado?"):
    # Agregar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Respuesta simulada de la IA
    import time
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        simulated_reply = f"He analizado tu base de datos respecto a '{prompt}'. Los indicadores muestran una tendencia positiva en este trimestre. Si esto fuera una conexión real, aquí te mostraría el cálculo exacto y una gráfica generada al instante. ¡Ese es el poder de conectar IA a tus datos!"
        
        # Efecto de escritura tipo "máquina de escribir"
        for chunk in simulated_reply.split():
            full_response += chunk + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
