import streamlit as st
import requests
import json

# --- Configuración de la página ---
st.set_page_config(page_title="KDP Writer Pro: 12 Capítulos", page_icon="🖋️", layout="wide")

# --- Diccionario de Modelos 2026 ---
MODELS = {
    "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
    "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
    "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
    "Qwen 3.5 Plus (2026)": "qwen/qwen3.5-plus-20260420",
    "Llama 3.1 405B": "meta-llama/llama-3.1-405b",
    "GPT-4o Mini": "openai/gpt-4o-mini"
}

# --- Estilos CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #1e8449; color: white; }
    .progress-text { font-size: 1.2rem; font-weight: bold; color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

# --- Función de Comunicación con OpenRouter ---
def call_openrouter(prompt, key, model):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]})
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- Barra Lateral ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model_choice = st.selectbox("Cerebro Lógico", list(MODELS.keys()))
    selected_model = MODELS[model_choice]
    st.divider()
    st.info("Configurado para: 12 Capítulos de 2200 palabras.")

# --- Flujo de Trabajo ---
st.title("🚀 Generador Editorial Abductivo")

# ETAPA 1: PREDICCIÓN
st.header("1. Horizonte Temporal")
col1, col2 = st.columns(2)
with col1: mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
with col2: anio = st.selectbox("Año", [2026, 2027, 2028])

if st.button("🔍 Predecir Tendencias Emergentes"):
    prompt_trends = f"Actúa como analista de tendencias futuras. Predice 5 nichos específicos para KDP en {mes} de {anio}. Explica la justificación de cada uno."
    trends = call_openrouter(prompt_trends, api_key, selected_model)
    st.session_state['trends'] = trends

if 'trends' in st.session_state:
    st.markdown("### Tendencias Detectadas")
    st.info(st.session_state['trends'])
    
    # ETAPA 2: ABDUCCIÓN Y PLAN
    st.header("2. Análisis Abductivo y Plan Editorial")
    chosen_trend = st.text_input("Ingresa la tendencia elegida:")
    
    if st.button("🧠 Crear Plan de 12 Capítulos"):
        prompt_plan = f"""
        Aplica la lógica abductiva de Peirce para la tendencia: '{chosen_trend}'.
        1. Identifica el Hecho Sorprendente (Anomalía de mercado).
        2. Plantea la Hipótesis Abductiva.
        3. Genera un PLAN EDITORIAL de 12 CAPÍTULOS.
        
        REGLAS DE FORMATO:
        - Títulos: Mayúscula inicial solo en la primera palabra y nombres propios.
        - Estructura: Título, Subtítulo, Síntesis y Tabla de contenidos.
        """
        plan = call_openrouter(prompt_plan, api_key, selected_model)
        st.session_state['plan'] = plan

if 'plan' in st.session_state:
    st.divider()
    st.markdown(st.session_state['plan'])

    # ETAPA 3: ESCRITURA
    st.header("3. Redacción del Libro")
    if st.button("✍️ Iniciar Escritura del Libro (12 Capítulos x 2200 palabras)"):
        book_content = ""
        prog_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(1, 13):
            status_text.markdown(f"**Escribiendo Capítulo {i} de 12...** (Extensión objetivo: 2200 palabras)")
            prompt_writing = f"""
            Escribe el capítulo {i} basado en el plan: {st.session_state['plan']}.
            
            CONVENCIONES OBLIGATORIAS:
            - Extensión: Aproximadamente 2200 palabras. Sé extremadamente detallado, profundo y analítico.
            - Inicio: Comienza exactamente con '# Capítulo {i}: [Título del capítulo]'.
            - Títulos: Mayúscula inicial solo en la primera palabra (salvo nombres propios).
            - Puntuación: Usa únicamente comillas españolas (« »).
            - No incluyas comentarios de IA, introducciones o despedidas del asistente.
            - Idioma: Español formal y técnico.
            """
            chapter_text = call_openrouter(prompt_writing, api_key, selected_model)
            book_content += chapter_text + "\n\n"
            prog_bar.progress(i / 12)
            
        st.session_state['full_book'] = book_content
        st.success("¡Redacción finalizada con éxito!")

# ETAPA 4: EXPORTACIÓN
if 'full_book' in st.session_state:
    st.divider()
    st.subheader("💾 Compilación Final")
    
    st.download_button(
        label="📥 Descargar Libro en Markdown (.md)",
        data=st.session_state['full_book'],
        file_name="manuscrito_kdp_abductivo.md",
        mime="text/markdown"
    )
