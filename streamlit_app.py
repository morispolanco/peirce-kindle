import streamlit as st
import pandas as pd
import requests
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Editor Abductivo KDP",
    page_icon="📚",
    layout="wide"
)

# --- ESTILOS CSS (Estética Minimalista / Baroque-Tech) ---
st.markdown("""
    <style>
    .main { background-color: #fdfdfd; }
    .stTextInput>div>div>input { border-radius: 5px; }
    .stButton>button { 
        width: 100%; 
        background-color: #1a1a1a; 
        color: white; 
        font-weight: bold;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #4a4a4a; color: #fff; }
    .report-box { 
        padding: 20px; 
        border: 1px solid #e6e6e6; 
        border-radius: 10px; 
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.markdown("---")
    
    # Manejo de API Key con persistencia en sesión
    saved_key = st.session_state.get("op_api_key", "")
    api_key_input = st.text_input("OpenRouter API Key", value=saved_key, type="password", help="Tu clave se mantendrá activa durante esta sesión.")
    
    if api_key_input:
        st.session_state["op_api_key"] = api_key_input.strip()

    model_option = st.selectbox(
        "Cerebro de IA (Modelo)",
        [
            "anthropic/claude-3.5-sonnet",
            "google/gemini-2.0-flash-001",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.1-405b"
        ],
        help="Claude 3.5 es altamente recomendado para razonamiento lógico complejo."
    )
    
    st.info("La lógica abductiva de Peirce busca la 'mejor explicación' para un conjunto de datos observados (ventas y keywords).")

# --- CUERPO PRINCIPAL ---
st.title("📚 Generador Editorial Abductivo")
st.subheader("Planificación estratégica para Kindle Direct Publishing")

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.markdown("### 🔍 Insumos de Mercado")
    main_keyword = st.text_input("Keyword Principal", placeholder="Ej: Estoicismo para emprendedores")
    target_country = st.text_input("País Objetivo", placeholder="Ej: España")
    
    uploaded_file = st.file_uploader("Informe de Ventas KDP (CSV o Excel)", type=["csv", "xlsx"])

with col2:
    st.markdown("### 🛠️ Parámetros del Libro")
    st.write("- **Longitud:** 40,000 - 50,000 palabras.")
    st.write("- **Estructura:** 20 a 25 capítulos.")
    st.write("- **Metodología:** Inferencia abductiva (Peirce).")

# --- FUNCIÓN DE LLAMADA A API ---
def generar_plan_editorial(keyword, pais, datos_ventas):
    if not st.session_state.get("op_api_key"):
        st.error("❌ Falta la API Key de OpenRouter en la barra lateral.")
        return None

    headers = {
        "Authorization": f"Bearer {st.session_state['op_api_key']}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501", 
        "X-Title": "KDP Abductive Planner"
    }

    # Prompt con enfoque en el Método de Peirce
    prompt_sistema = (
        "Eres un estratega editorial de élite y experto en la filosofía de Charles Sanders Peirce. "
        "Tu tarea es aplicar la LÓGICA ABDUCTIVA para proponer un plan editorial. "
        "La abducción no es solo resumen; es proponer una hipótesis creativa que explique por qué "
        "ciertos datos (ventas y keywords) sugieren un éxito futuro. "
        "Debes diseñar libros de no ficción para Amazon KDP de 40,000 a 50,000 palabras."
    )

    prompt_usuario = f"""
    DATOS OBSERVADOS (El Hecho Sorprendente):
    - Keyword: {keyword}
    - Mercado: {pais}
    - Datos de Ventas/Contexto: {datos_ventas}

    INSTRUCCIONES DE DISEÑO:
    1. Elabora una HIPÓTESIS ABDUCTIVA: ¿Qué ángulo único o necesidad no satisfecha explica estos datos?
    2. TÍTULO Y SUBTÍTULO: Atractivos, con alto potencial SEO.
    3. SÍNTESIS: Un argumento sólido que justifique la existencia del libro.
    4. TABLA DE CONTENIDOS: Exactamente entre 20 y 25 capítulos. Cada capítulo debe tener una breve descripción de su enfoque para asegurar que el manuscrito alcance las 40k-50k palabras.

    Formatea la respuesta con Markdown elegante.
    """

    payload = {
        "model": model_option,
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ],
        "temperature": 0.7
    }

    try:
        with st.spinner("Realizando inferencia abductiva..."):
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                data=json.dumps(payload),
                timeout=90
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                st.error(f"Error de API ({response.status_code}): {response.text}")
                return None
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

# --- ACCIÓN ---
if st.button("🚀 Generar Plan Editorial"):
    if not main_keyword or not target_country:
        st.warning("Por favor, completa al menos la Keyword y el País.")
    else:
        # Procesamiento de archivo de ventas
        ventas_str = "No se proporcionaron datos históricos."
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                # Tomamos una muestra representativa para no saturar el contexto de la IA
                ventas_str = df.head(50).to_string(index=False)
            except Exception as e:
                st.error(f"Error al leer el archivo de ventas: {e}")

        resultado = generar_plan_editorial(main_keyword, target_country, ventas_str)
        
        if resultado:
            st.markdown("---")
            st.markdown("## 📋 Propuesta Editorial")
            st.markdown(resultado)
            
            # Opción para descargar el plan
            st.download_button(
                label="Descargar Plan como TXT",
                data=resultado,
                file_name=f"plan_editorial_{main_keyword.replace(' ', '_')}.txt",
                mime="text/plain"
            )

st.markdown("---")
st.caption("Desarrollado para optimización de catálogo en Amazon Kindle Publishing mediante IA Generativa.")
