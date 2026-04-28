import streamlit as st
import requests
import json

# --- Configuración de la interfaz ---
st.set_page_config(page_title="KDP Abductive Engine 2026", page_icon="🧬", layout="wide")

# --- Estilos Personalizados ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #2c3e50; color: white; font-weight: bold; }
    .report-box { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

# --- Diccionario de Modelos (Actualizado 2026) ---
MODELS = {
    "Auto: OpenRouter Free": "openrouter/free",
    "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
    "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
    "Qwen 3.5 Plus (2026)": "qwen/qwen3.5-plus-20260420",
    "Minimax M2.7": "minimax/minimax-m2.7",
    "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
    "GPT-4o Mini": "openai/gpt-4o-mini",
    "GLM 5.1 (Z-AI)": "z-ai/glm-5.1",
    "Kimi-k2.6 (Moonshot)": "moonshotai/kimi-k2.6",
    "Llama 3.1 405B": "meta-llama/llama-3.1-405b"
}

# --- Barra Lateral ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model_name = st.selectbox("Cerebro Lógico (LLM):", list(MODELS.keys()))
    selected_model = MODELS[model_name]
    st.divider()
    st.info("**Lógica de Peirce:** La abducción identifica la 'Anomalía' y propone la 'Hipótesis' ganadora.")

# --- Lógica de API ---
def call_abduction_api(keyword, key, model):
    prompt = f"""
    Actúa como un experto en lógica abductiva de Charles Sanders Peirce y analista senior de Amazon KDP.
    Analiza la palabra clave: '{keyword}'.
    
    Estructura tu respuesta estrictamente para un Plan Editorial profesional:
    
    1. HECHO SORPRENDENTE (Anomalía detectada en el mercado actual).
    2. HIPÓTESIS ABDUCTIVA (Por qué este nicho es la explicación a la demanda insatisfecha).
    
    --- INICIO DEL PLAN EDITORIAL ---
    TÍTULO: [Título impactante]
    SUBTÍTULO: [Optimizado con keywords secundarias]
    SÍNTESIS: [Resumen detallado del libro y su propuesta única de 3 párrafos]
    TABLA DE CONTENIDOS:
    - Capítulo 1 a 10 con descripciones breves de los temas a tratar.
    --- FIN DEL PLAN EDITORIAL ---
    """
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error API: {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Cuerpo Principal ---
st.title("🧬 Generador de Planes Editoriales Abductivos")
target_keyword = st.text_input("Ingresa una palabra clave o tema semilla:", placeholder="Ej: Estoicismo para programadores")

if st.button("Generar Plan Editorial"):
    if not api_key:
        st.error("Por favor, introduce tu API Key de OpenRouter.")
    elif not target_keyword:
        st.warning("Escribe una palabra clave para comenzar.")
    else:
        with st.spinner("Ejecutando salto abductivo y estructurando contenido..."):
            plan_text = call_abduction_api(target_keyword, api_key, selected_model)
            st.session_state['current_plan'] = plan_text
            st.session_state['last_keyword'] = target_keyword
            st.markdown("--- ")
            st.markdown(plan_text)

# --- Sección de Exportación ---
if 'current_plan' in st.session_state:
    st.divider()
    st.subheader("💾 Exportar Resultado")
    
    st.download_button(
        label="📥 Descargar Plan Editorial (.txt)",
        data=st.session_state['current_plan'],
        file_name=f"plan_editorial_{st.session_state['last_keyword'].replace(' ', '_')}.txt",
        mime="text/plain"
    )
