import streamlit as st
import pandas as pd
import requests
import json
from streamlit_local_storage import LocalStorage

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Editor Abductivo KDP",
    page_icon="📚",
    layout="wide"
)

# Inicializamos el almacenamiento local (persistencia en navegador)
local_storage = LocalStorage()

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

# --- LÓGICA DE PERSISTENCIA DE API KEY ---
# Intentamos recuperar la clave del LocalStorage al cargar la página
ls_api_key = local_storage.getItem("op_api_key")

# Si existe en LocalStorage y no está en el estado de sesión actual, la sincronizamos
if ls_api_key and "op_api_key" not in st.session_state:
    st.session_state["op_api_key"] = ls_api_key

# --- SIDEBAR: CONFIGURACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.markdown("---")
    
    # Input de la API Key: usamos el valor guardado (si existe)
    saved_key = st.session_state.get("op_api_key", "")
    api_key_input = st.text_input(
        "OpenRouter API Key", 
        value=saved_key, 
        type="password", 
        help="Tu clave se guardará en este navegador y no se borrará al refrescar."
    )
    
    # Si el usuario cambia la clave, actualizamos sesión y almacenamiento local
    if api_key_input and api_key_input != ls_api_key:
        st.session_state["op_api_key"] = api_key_input.strip()
        local_storage.setItem("op_api_key", api_key_input.strip())

    model_option = st.selectbox(
        "Cerebro de IA (Modelo)",
        [
            "anthropic/claude-3.5-sonnet",
            "google/gemini-pro-1.5",
            "openai/gpt-4o",
            "meta-llama/llama-3.1-405b"
        ],
        help="Claude 3.5 es altamente recomendado para razonamiento lógico complejo."
    )
    
    st.info("La lógica abductiva de Peirce busca la 'mejor explicación' para un conjunto de datos observados.")

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
    # Recuperamos la clave directamente de la sesión (que ya está sincronizada con LS)
    api_key = st.session_state.get("op_api_key")
    
    if not api_key:
        st.error("❌ Falta la API Key de OpenRouter en la barra lateral.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501", 
        "X-Title": "KDP Abductive Planner"
    }

    prompt_sistema = (
        "Eres un estratega editorial de élite y experto en la filosofía de Charles Sanders Peirce. "
        "Tu tarea es aplicar la LÓGICA ABDUCTIVA para proponer un plan editorial. "
        "La abducción no es solo resumen; es proponer una hipótesis creativa que explique por qué "
        "ciertos datos sugieren un éxito futuro. Diseña libros de 40k-50k palabras."
    )

    prompt_usuario = f"""
    DATOS OBSERVADOS:
    - Keyword: {keyword}
    - Mercado: {pais}
    - Datos de Ventas: {datos_ventas}

    INSTRUCCIONES:
    1. Elabora una HIPÓTESIS ABDUCTIVA única.
    2. TÍTULO Y SUBTÍTULO SEO.
    3. SÍNTESIS del argumento.
    4. TABLA DE CONTENIDOS (20-25 capítulos con descripción).
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
                timeout=120
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
        ventas_str = "No se proporcionaron datos históricos."
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                ventas_str = df.head(50).to_string(index=False)
            except Exception as e:
                st.error(f"Error al leer el archivo: {e}")

        resultado = generar_plan_editorial(main_keyword, target_country, ventas_str)
        
        if resultado:
            st.markdown("---")
            st.markdown("## 📋 Propuesta Editorial")
            st.markdown(resultado)
            
            st.download_button(
                label="Descargar Plan como TXT",
                data=resultado,
                file_name=f"plan_{main_keyword.replace(' ', '_')}.txt",
                mime="text/plain"
            )

st.markdown("---")
st.caption("Optimizador KDP con persistencia de credenciales local.")
