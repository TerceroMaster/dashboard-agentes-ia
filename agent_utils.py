import streamlit as st
import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langchain_experimental.tools import PythonAstREPLTool
import matplotlib.pyplot as plt

def render_agent_chat(df_filtered: pd.DataFrame, contexto: str, page_key: str, ejemplos: str = ""):
    # CSS para forzar que el popover se posicione flotando en la esquina inferior derecha y sea responsivo
    st.markdown("""
    <style>
        div[data-testid="stPopover"] {
            position: fixed !important;
            bottom: 20px !important;
            right: 20px !important;
            z-index: 99999 !important;
        }
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
        div[data-testid="stPopoverBody"] {
            width: 450px !important;
            max-width: 90vw !important;
            max-height: 80vh !important;
            border-radius: 15px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
            padding: 20px !important;
            resize: both;
            overflow: auto;
        }
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
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
    st.markdown("## 🧠 ¿Cómo funciona la Inteligencia Artificial?")
    
    col_ai1, col_ai2 = st.columns(2)
    with col_ai1:
        st.markdown("""
        ### 🤖 Arquitectura del Agente (LangGraph)
        El chat flotante está impulsado por **LangGraph** y **GPT-4o-mini**, actuando como un equipo de Data Science en tiempo real.
        
        Internamente operan **3 sub-agentes invisibles**:
        1. **El Analista**: Escucha tu pregunta y decide qué columnas de la base de datos necesita.
        2. **El Programador**: Escribe un script en Python exacto para extraer y calcular esos datos.
        3. **El Revisor**: Ejecuta el código, valida los resultados matemáticos y te redacta la respuesta en lenguaje natural.
        """)
        
    with col_ai2:
        st.markdown("""
        ### 🚀 ¿Qué puedes hacer con él?
        Al estar conectado directamente al motor de este dashboard, el Agente puede:
        - **Realizar Matemáticas Complejas**: Sumar, promediar, y agrupar registros al instante.
        - **Generar Gráficos al Vuelo**: Crear gráficos (`.png`) que no existen en el dashboard principal.
        - **Exportar Reportes**: Generar documentos físicos descargables (`.xlsx`, `.pdf`) perfectamente filtrados.
        - **Recordar Contexto**: Mantiene el hilo de la conversación.
        """)
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except (FileNotFoundError, KeyError):
        st.error("🚨 La API Key de OpenAI no está configurada en los secretos. El agente no funcionará.")
        return

    chat_history_key = f"ai_chat_history_{page_key}"
    if chat_history_key not in st.session_state:
        st.session_state[chat_history_key] = [
            {"role": "assistant", "content": f"👋 ¡Hola! Soy tu asistente inteligente para {contexto}. He analizado los datos actuales. ¿Qué quieres descubrir hoy?"}
        ]

    with st.popover("💬 Empezar Conversación", help="Habla con tus datos"):
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.markdown("### 🤖 Asistente de Datos")
        with col2:
            fullscreen = st.checkbox("🔲 Completa", key=f"fs_{page_key}")
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
        
        if ejemplos:
            with st.expander("💡 Ejemplos de lo que puedes preguntarme"):
                st.markdown(ejemplos)
                
        chat_height = 600 if fullscreen else 350
        chat_container = st.container(height=chat_height)
        with chat_container:
            for i, msg in enumerate(st.session_state[chat_history_key]):
                with st.chat_message(msg["role"]):
                    content_display = msg["content"]
                    content_display = content_display.replace("[GRAFICA_GENERADA]", "📊 Aquí tienes tu gráfica:")
                    content_display = content_display.replace("[REPORTE_EXCEL_GENERADO]", "📗 ¡Tu reporte en Excel está listo para descargar!")
                    content_display = content_display.replace("[REPORTE_PDF_GENERADO]", "📕 ¡Tu reporte en PDF está listo para descargar!")
                    st.markdown(content_display)
                    
                    if "image" in msg and os.path.exists(msg["image"]):
                        st.image(msg["image"])
                        with open(msg["image"], "rb") as file:
                            st.download_button("⬇️ Descargar Gráfica", data=file, file_name=f"grafica_{page_key}.png", mime="image/png", key=f"dl_img_{page_key}_{i}")
                            
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        if "excel" in msg and os.path.exists(msg["excel"]):
                            with open(msg["excel"], "rb") as file:
                                st.download_button("⬇️ Excel", data=file, file_name=f"reporte_{page_key}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"dl_xls_{page_key}_{i}")
                    with dl_col2:
                        if "pdf" in msg and os.path.exists(msg["pdf"]):
                            with open(msg["pdf"], "rb") as file:
                                st.download_button("⬇️ PDF", data=file, file_name=f"reporte_{page_key}.pdf", mime="application/pdf", key=f"dl_pdf_{page_key}_{i}")
                    
        with st.form(f"chat_form_{page_key}", clear_on_submit=True):
            col_in, col_btn = st.columns([3, 1])
            with col_in:
                user_input = st.text_input("Escribe tu pregunta...", label_visibility="collapsed")
            with col_btn:
                submit = st.form_submit_button("Enviar", use_container_width=True)
                
            if submit and user_input:
                st.session_state[chat_history_key].append({"role": "user", "content": user_input})
                
                with st.spinner("Analizando datos con LangGraph..."):
                    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=api_key)
                    
                    tool = PythonAstREPLTool(locals={"df": df_filtered})
                    
                    instrucciones = f"""
                    Eres un experto analista de datos. El contexto actual es: {contexto}.
                    La base de datos actual está disponible como un DataFrame de Pandas llamado `df`.
                    
                    REGLAS IMPORTANTES:
                    1. Analiza el dataframe `df` usando tu herramienta de python para responder la pregunta con EXACTITUD matemática.
                    2. Responde SIEMPRE 100% en Español.
                    3. ¡SOPORTE PARA GRÁFICAS!: Si piden gráfica, genera el código usando `matplotlib.pyplot` como `plt`. Usa SIEMPRE `plt.xticks(rotation=45, ha='right')` y `plt.tight_layout()`. Guarda la figura con `plt.savefig('temp_chart_{page_key}.png')`. Respuesta final de texto debe incluir: [GRAFICA_GENERADA].
                    4. ¡SOPORTE PARA EXCEL/PDF!: Si piden Excel, crea el dataframe y guárdalo con `df_nuevo.to_excel('reporte_temp_{page_key}.xlsx', index=False)`. Respuesta final de texto debe incluir: [REPORTE_EXCEL_GENERADO]. Si piden PDF, guarda la tabla como imagen usando matplotlib (`plt.savefig('reporte_temp_{page_key}.pdf', bbox_inches='tight')`). Respuesta final de texto debe incluir: [REPORTE_PDF_GENERADO].
                    """
                    
                    agent_executor = create_react_agent(llm, [tool], state_modifier=instrucciones)
                    
                    messages = []
                    # Pass the last 3 pairs for context
                    for msg in st.session_state[chat_history_key][-7:]:
                        if msg["role"] == "user":
                            messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            messages.append(AIMessage(content=msg["content"]))
                            
                    for temp_file in [f'temp_chart_{page_key}.png', f'reporte_temp_{page_key}.xlsx', f'reporte_temp_{page_key}.pdf']:
                        if os.path.exists(temp_file):
                            try: os.remove(temp_file)
                            except: pass
                            
                    try:
                        response = agent_executor.invoke({"messages": messages})
                        ai_reply = response["messages"][-1].content
                    except Exception as e:
                        ai_reply = f"Ocurrió un error en el razonamiento del agente: {e}"

                    msg_data = {"role": "assistant", "content": ai_reply}
                    if "[GRAFICA_GENERADA]" in ai_reply and os.path.exists(f"temp_chart_{page_key}.png"):
                        msg_data["image"] = f"temp_chart_{page_key}.png"
                    if "[REPORTE_EXCEL_GENERADO]" in ai_reply and os.path.exists(f"reporte_temp_{page_key}.xlsx"):
                        msg_data["excel"] = f"reporte_temp_{page_key}.xlsx"
                    if "[REPORTE_PDF_GENERADO]" in ai_reply and os.path.exists(f"reporte_temp_{page_key}.pdf"):
                        msg_data["pdf"] = f"reporte_temp_{page_key}.pdf"
                        
                    st.session_state[chat_history_key].append(msg_data)
                    st.rerun()
