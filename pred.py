import streamlit as st
import requests
import json
from datetime import datetime

# --- Configuración de la página ---
st.set_page_config(page_title="KDP Future Abductor 2026", page_icon="📅", layout="wide")

# --- Diccionario de Modelos 2026 ---
MODELS = {
    "Auto: OpenRouter Free": "openrouter/free",
    "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
    "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
    "Qwen 3.5 Plus (2026)": "qwen/qwen3.5-plus-20260420",
    "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
    "GPT-4o Mini": "openai/gpt-4o-mini",
    "Llama 3.1 405B": "meta-llama/llama-3.1-405b"
}

# --- Estilos ---
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .trend-card { padding: 15px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 10px; background: white; }
    </style>
""", unsafe_allow_html=True)

# --- Funciones de API ---
def call_openrouter(prompt, key, model):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]})
        )
        return response.json()['choices'][0]['message']['content']
    except:
        return None

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🛡️ Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model_name = st.selectbox("Modelo de Inteligencia:", list(MODELS.keys()))
    selected_model = MODELS[model_name]
    st.divider()
    st.markdown("**Metodología:** Predicción Predictiva + Salto Abductivo de Peirce.")

# --- CUERPO PRINCIPAL ---
st.title("🚀 KDP Trend & Niche Abductor")

# ETAPA 1: Predicción de Tendencias
st.header("1. Horizonte Temporal")
col1, col2 = st.columns(2)
with col1:
    month = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
with col2:
    year = st.selectbox("Año", [2026, 2027, 2028])

if st.button("🔍 Predecir Tendencias Emergentes"):
    if not api_key: st.error("Falta API Key")
    else:
        prompt = f"Actúa como un experto en análisis de tendencias. Predice 5 tendencias de nicho para publicar libros en Amazon KDP en la fecha {month} de {year}. Devuelve una lista numerada con nombre de tendencia y una breve descripción."
        with st.spinner("Analizando el futuro..."):
            tendencias = call_openrouter(prompt, api_key, selected_model)
            st.session_state['tendencias'] = tendencias

if 'tendencias' in st.session_state:
    st.markdown("### Tendencias detectadas:")
    st.info(st.session_state['tendencias'])
    
    # ETAPA 2: Selección y Abducción
    st.header("2. Análisis Abductivo")
    tendencia_elegida = st.text_input("Copia y pega la tendencia que más te interese aquí:")
    
    if st.button("🧠 Realizar Análisis Abductivo"):
        prompt_abduccion = f"""
        Utiliza la lógica de Charles Sanders Peirce para la tendencia: '{tendencia_elegida}'.
        
        1. Identifica el 'Hecho Sorprendente' (C) (¿Qué falla o vacío hay en esta tendencia?).
        2. Genera la 'Hipótesis Abductiva' (A) (¿Qué tipo de libro explicaría y satisfaría ese vacío?).
        3. Crea un PLAN EDITORIAL COMPLETO:
           - TÍTULO Y SUBTÍTULO (SEO)
           - SÍNTESIS DEL PROYECTO
           - TABLA DE CONTENIDOS (10 Capítulos)
        """
        with st.spinner("Realizando el salto de Peirce..."):
            plan_final = call_openrouter(prompt_abduccion, api_key, selected_model)
            st.session_state['plan_final'] = plan_final

# ETAPA 3: Resultados y Exportación
if 'plan_final' in st.session_state:
    st.divider()
    st.header("📚 Plan Editorial Generado")
    st.markdown(st.session_state['plan_final'])
    
    st.download_button(
        label="📥 Exportar Plan Editorial (.txt)",
        data=st.session_state['plan_final'],
        file_name=f"plan_kdp_{month}_{year}.txt",
        mime="text/plain"
    )
