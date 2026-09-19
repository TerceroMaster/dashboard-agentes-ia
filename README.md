# 📊 AI-Augmented BI Dashboards Portfolio (SaaS Platform)

Bienvenido al repositorio central de **Dashboards Interactivos con Inteligencia Artificial**. Este proyecto no es un simple panel de métricas, sino un **Motor Multi-Empresa (B2B)** diseñado para ofrecer Inteligencia de Negocios de próxima generación a *N* cantidad de empresas e industrias.

El objetivo de esta plataforma es **comercializar y escalar la integración de Agentes de IA en empresas**, permitiendo que cualquier organización (Farmacéutica, Retail, Logística, Energía, etc.) pueda "hablar" directamente con sus bases de datos sin necesidad de saber programar.

---

## 🏢 Arquitectura Multi-Empresa (Casos de Uso Incluidos)

El proyecto está estructurado de manera modular para alojar dashboards independientes por cliente/industria. Algunos de los módulos activos en este portafolio son:

*   💊 **PIRMCT (Sector Salud/Farmacéutico):** Análisis de recolección de medicamentos caducados (Implementación insignia actual del Agente de IA).
*   ⛽ **Sinopec (Sector Energía/Petróleo):** Análisis de producción y métricas operativas.
*   🛒 **Retail Global (E-Commerce):** Ventas, inventarios y logística comercial.
*   ✈️ **Logística Aérea (Airlines):** Métricas de vuelos, rutas y eficiencias.
*   🧠 **Análisis de Sentimiento:** Procesamiento de lenguaje natural sobre redes sociales (Ej. Twitter).

---

## ✨ Características del Producto (El Valor Agregado)

Lo que diferencia a estos Dashboards de soluciones estáticas como Tableau o PowerBI tradicional es la capa de **Agentes de Inteligencia Artificial Autónomos**:

*   **🤖 Científico de Datos Integrado:** Un botón de chat flotante impulsado por IA que responde preguntas matemáticas exactas sobre el negocio en tiempo real.
*   **💾 Exportación de Reportes Dinámicos:** Los clientes pueden pedir verbalmente "Genérame un reporte de las ventas caídas en marzo" y la IA genera un archivo **Excel (.xlsx)** o **PDF** descargable al instante.
*   **📊 Gráficas Generativas al Vuelo:** Generación de gráficos (Barras, Pastel, Dispersión) que no estaban programados originalmente en el dashboard, dibujados a petición del cliente por el Agente.
*   **🗑️ Garbage Collection Automático:** Eficiencia a nivel servidor; todo documento físico temporal generado por la IA se auto-destruye tras ser entregado al cliente, minimizando costos de almacenamiento.

---

## 🛠️ Tecnologías y Stack (Bajo el Capó)

Para lograr un sistema tan reactivo, escalable y modular, utilizamos el siguiente stack tecnológico de punta:

*   **[Streamlit](https://streamlit.io/):** Framework web ultra rápido para crear interfaces corporativas sin latencia.
*   **[LangChain](https://www.langchain.com/):** El "cerebro" orquestador. Usamos la arquitectura `create_pandas_dataframe_agent` para que el LLM pueda escribir y ejecutar scripts de Python internamente.
*   **[OpenAI (GPT-4o-mini)](https://openai.com/):** Motor de lenguaje natural (LLM) altamente eficiente en costos para escalar a múltiples empresas.
*   **[Pandas](https://pandas.pydata.org/):** Core engine para procesamiento de millones de filas de datos.
*   **[SQLite](https://www.sqlite.org/):** Base de datos embebida, fácilmente reemplazable por PostgreSQL o Snowflake en producción.
*   **[Matplotlib & Openpyxl]:** Motores de renderizado visual y creación de reportes empresariales.

---

## 🚀 Instalación y Ejecución Local

Para levantar el motor de Dashboards en tu máquina o servidor local:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/TerceroMaster/dashboard-agentes-ia.git
    cd dashboard-agentes-ia
    ```

2.  **Instala las dependencias necesarias:**
    ```bash
    pip install streamlit pandas sqlite3 langchain langchain-experimental langchain-openai openai matplotlib openpyxl
    ```

3.  **Configura la llave maestra de la API (OpenAI):**
    Crea la carpeta oculta `.streamlit` y protege tu llave:
    ```bash
    mkdir .streamlit
    # Crea el archivo .streamlit/secrets.toml y agrega:
    # OPENAI_API_KEY = "sk-tu-api-key-aqui"
    ```

4.  **Enciende el servidor:**
    ```bash
    python -m streamlit run app.py
    ```

---

*Diseñado para escalar. Construido para revolucionar la Inteligencia de Negocios.*
