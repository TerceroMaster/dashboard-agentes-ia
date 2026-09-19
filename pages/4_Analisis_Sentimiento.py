import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Análisis de Sentimiento", page_icon="🧠", layout="wide")

# Theme Colors
FONDO = "rgba(255,255,255,0.05)"

st.markdown(f"""
    <style>
    .kpi-card {{ background-color: {FONDO}; padding: 20px; border-radius: 10px; border-left: 5px solid #1DA1F2; text-align: center; }}
    h1, h2, h3, h4 {{ color: white; }}
    </style>
""", unsafe_allow_html=True)

st.title("🧠 NLP: Análisis de Sentimiento en Redes Sociales")
st.markdown("Clasificación por Inteligencia Artificial de 10,000 interacciones reales en Twitter.")

@st.cache_data
def load_twitter():
    db_path = "dashboard_data.db"
    if not os.path.exists(db_path): return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql("SELECT * FROM twitter_total", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

df = load_twitter()
if df.empty:
    st.warning("Datos no encontrados. Ejecuta etl.py.")
    st.stop()

# KPIs
total_tweets = len(df)
positivos = len(df[df['sentiment'] == 'Positivo'])
negativos = len(df[df['sentiment'] == 'Negativo'])

c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='kpi-card'><div>Total de Interacciones</div><h2 style='margin:0;'>{total_tweets:,}</h2></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='kpi-card' style='border-color:#00C853'><div>Sentimiento Positivo</div><h2 style='margin:0;color:#00C853'>{positivos:,}</h2></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='kpi-card' style='border-color:#FF1744'><div>Sentimiento Negativo</div><h2 style='margin:0;color:#FF1744'>{negativos:,}</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Proporción de Sentimiento")
    fig_pie = px.pie(names=['Positivo', 'Negativo'], values=[positivos, negativos], 
                     color_discrete_sequence=['#00C853', '#FF1744'], hole=0.4)
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("### ☁️ Nube de Palabras (Wordcloud)")
    
    filtro_nube = st.radio("Ver nube de palabras para:", ("Positivo", "Negativo"), horizontal=True)
    
    texto_combinado = " ".join(df[df['sentiment'] == filtro_nube]['text'].astype(str).tolist())
    
    if texto_combinado.strip():
        # Generar WordCloud
        cmap = "Greens" if filtro_nube == "Positivo" else "Reds"
        wordcloud = WordCloud(width=800, height=400, background_color='black', colormap=cmap).generate(texto_combinado)
        
        # Plotear en Matplotlib y pasar a Streamlit
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='black')
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("No hay suficiente texto para la nube de palabras.")
        
st.markdown("---")
st.markdown("### 💬 Muestra de Tweets Recientes")
st.dataframe(df[['date', 'user', 'sentiment', 'text']].head(50), use_container_width=True)

# ==============================================================================
# 🤖 BOTÓN FLOTANTE: AGENTE IA CON OPENAI (LangGraph)
# ==============================================================================
import agent_utils

contexto_nlp = "Dashboard Análisis de Sentimiento (NLP): Clasificación de interacciones de Twitter en Positivo y Negativo."
agent_utils.render_agent_chat(df, contexto_nlp, "sentimiento")
