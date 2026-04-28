import streamlit as st
import requests
import json

# --- Configuración de la interfaz ---
st.set_page_config(page_title="KDP España: Escritor Abductivo", page_icon="🇪🇸", layout="wide")

# --- Modelos 2026 ---
MODELS = {
    "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
    "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
    "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
    "Qwen 3.5 Plus (2026)": "qwen/qwen3.5-plus-20260420",
    "Llama 3.1 405B": "meta-llama/llama-3.1-405b",
    "GPT-4o Mini": "openai/gpt-4o-mini"
}

# --- Lógica de Comunicación ---
def call_openrouter(prompt, key, model):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]})
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Panel Lateral ---
with st.sidebar:
    st.title("🇪🇸 Configuración España")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model_choice = st.selectbox("Modelo de Inteligencia", list(MODELS.keys()))
    selected_model = MODELS[model_choice]
    st.divider()
    st.info("Filtro: Mercado Amazon.es | 12 Capítulos | 2200 palabras/cap.")

# --- Interfaz Principal ---
st.title("🧠 KDP Abductor: Mercado España")

# 1. TENDENCIAS ORIENTADAS A ESPAÑA
st.header("1. Predicción de Tendencias en España")
col_m, col_a = st.columns(2)
with col_m: mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
with col_a: anio = st.selectbox("Año", [2026, 2027, 2028])

if st.button("🔍 Detectar Tendencias en Amazon.es"):
    prompt_es = f"""
    Actúa como experto en el mercado editorial de España (Amazon.es). 
    Predice 5 nichos de mercado emergentes para {mes} de {anio} en España.
    Considera factores locales: leyes españolas, cultura, festividades, clima o tendencias tecnológicas en la península.
    Explica el 'Hecho Sorprendente' de cada una.
    """
    trends = call_openrouter(prompt_es, api_key, selected_model)
    st.session_state['trends_es'] = trends

if 'trends_es' in st.session_state:
    st.info(st.session_state['trends_es'])
    
    # 2. SELECCIÓN Y ABDUCCIÓN
    st.header("2. Salto Abductivo")
    tendencia_sel = st.text_input("Copia la tendencia española elegida:")
    
    if st.button("🧠 Generar Plan de 12 Capítulos"):
        prompt_plan = f"""
        Aplica la lógica abductiva de Peirce para la tendencia '{tendencia_sel}' en España.
        Genera un plan de 12 capítulos con títulos que usen mayúscula inicial solo en la primera palabra.
        Define la anomalía del mercado y la hipótesis de éxito.
        """
        plan = call_openrouter(prompt_plan, api_key, selected_model)
        st.session_state['plan_es'] = plan

if 'plan_es' in st.session_state:
    st.divider()
    st.markdown(st.session_state['plan_es'])

    # 3. ESCRITURA PROFUNDA
    st.header("3. Redacción del Manuscrito")
    if st.button("✍️ Escribir Libro Completo (12 x 2200 palabras)"):
        full_text = ""
        bar = st.progress(0)
        for i in range(1, 13):
            st.write(f"Redactando Capítulo {i}...")
            prompt_writing = f"""
            Escribe el capítulo {i} basándote en el plan: {st.session_state['plan_es']}.
            
            REGLAS ESTRICTAS:
            - Extensión: 2200 palabras (sé muy exhaustivo y analítico).
            - Título: '# Capítulo {i}: [Título con mayúscula solo al inicio]'.
            - Puntuación: Usa comillas españolas (« »).
            - Estilo: Dirigido al público de España, evita localismos de otros países.
            - Sin notas de IA.
            """
            cap = call_openrouter(prompt_writing, api_key, selected_model)
            full_text += cap + "\n\n"
            bar.progress(i / 12)
        
        st.session_state['book_es'] = full_text
        st.success("¡Libro para el mercado español finalizado!")

# 4. EXPORTACIÓN
if 'book_es' in st.session_state:
    st.divider()
    st.download_button(
        label="📥 Descargar Libro para Amazon.es (.md)",
        data=st.session_state['book_es'],
        file_name="manuscrito_espana_kdp.md",
        mime="text/markdown"
    )
