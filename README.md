# 📊 Dashboard Ejecutivo con Inteligencia Artificial (IA Agents)

Bienvenido al repositorio del **Dashboard Ejecutivo PIRMCT 2025**, una plataforma analítica de nueva generación que combina la visualización tradicional de Inteligencia de Negocios (BI) con el poder de los **Agentes de Inteligencia Artificial**.

Este proyecto transforma una base de datos estática en un ecosistema vivo donde los usuarios pueden "platicar" con sus datos, pedir cálculos matemáticos complejos, generar reportes en Excel/PDF y crear gráficas al vuelo, todo mediante lenguaje natural.

---

## ✨ Características Principales

*   **📈 Visualizaciones Dinámicas:** Gráficos interactivos nativos para explorar volúmenes de recolección, instituciones aliadas y sectores impactados.
*   **🤖 Asistente de Datos (IA Agent):** Un botón flotante de chat en la esquina inferior que actúa como un Científico de Datos dedicado.
*   **🧠 Arquitectura Multi-Agente:** Impulsado por LangChain, el agente analiza tu pregunta, programa un script de extracción en Python en milisegundos, valida las matemáticas y te responde en lenguaje natural.
*   **💾 Exportación de Reportes Bajo Demanda:** Pídele al agente "Expórtame un Excel con el top 5 de laboratorios" y generará un archivo `.xlsx` listo para descargar.
*   **📊 Gráficas Generativas:** Pídele gráficas personalizadas que no están en el dashboard por defecto y la IA las dibujará y te dará un botón para descargarlas como imagen.
*   **🗑️ Garbage Collection:** Sistema de auto-limpieza que elimina archivos temporales (Excel, PDF, PNG) del servidor inmediatamente después de la descarga para optimizar memoria.

---

## 🛠️ Tecnologías y Stack

Este proyecto fue construido utilizando herramientas modernas de Data Science y Desarrollo Web:

*   **[Python 3](https://www.python.org/):** El lenguaje base del proyecto.
*   **[Streamlit](https://streamlit.io/):** Framework web utilizado para renderizar la interfaz de usuario, los gráficos y el diseño responsivo sin necesidad de HTML/JS complejo.
*   **[LangChain](https://www.langchain.com/):** Framework utilizado para orquestar el `create_pandas_dataframe_agent`, dotando al modelo de la capacidad de ejecutar código Python interno.
*   **[OpenAI (GPT-4o-mini)](https://openai.com/):** El motor de procesamiento de lenguaje natural (LLM) que interpreta las peticiones del usuario y razona sobre los datos.
*   **[Pandas](https://pandas.pydata.org/):** Librería core para el análisis, manipulación y filtrado de los DataFrames en memoria.
*   **[SQLite](https://www.sqlite.org/):** Motor de base de datos relacional ligero (vía `dashboard_data.db` y `etl.py`).
*   **[Matplotlib](https://matplotlib.org/):** Para el dibujado generativo de gráficas solicitadas a la IA.
*   **[Openpyxl](https://openpyxl.readthedocs.io/):** Motor detrás de la generación y exportación dinámica de archivos Excel (`.xlsx`).

---

## 🚀 Instalación y Ejecución Local

Sigue estos pasos para correr el proyecto en tu propia máquina:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/TerceroMaster/dashboard-agentes-ia.git
    cd dashboard-agentes-ia
    ```

2.  **Instala las dependencias:**
    Asegúrate de tener instaladas las siguientes librerías en tu entorno de Python:
    ```bash
    pip install streamlit pandas sqlite3 langchain langchain-experimental langchain-openai openai matplotlib openpyxl
    ```

3.  **Configura tu API Key de OpenAI:**
    Crea una carpeta oculta llamada `.streamlit` en la raíz del proyecto y dentro un archivo `secrets.toml`:
    ```bash
    mkdir .streamlit
    # Dentro de .streamlit/secrets.toml escribe:
    # OPENAI_API_KEY = "sk-tu-api-key-aqui"
    ```

4.  **Ejecuta el Dashboard:**
    ```bash
    python -m streamlit run app.py
    ```

---

## 📁 Estructura del Proyecto

*   `app.py`: Archivo principal (Landing Page).
*   `pages/`: Directorio que contiene las sub-páginas del dashboard (ej. `1_PIRMCT.py` donde reside la lógica principal del Agente IA).
*   `etl.py`: Script de Extracción, Transformación y Carga que prepara `dashboard_data.db`.
*   `dashboard_data.db`: Base de datos SQLite pre-cargada.
*   `.streamlit/`: Carpeta de configuración y secretos (ignorada en Git por seguridad).

---

*Desarrollado con pasión para llevar la Inteligencia de Negocios al siguiente nivel.*
