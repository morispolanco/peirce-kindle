import streamlit as st
import requests
import json

# --- Configuración de la interfaz ---
st.set_page_config(
    page_title="KDP España: Escritor Abductivo Pro", 
    page_icon="🇪🇸", 
    layout="wide"
)

# --- Estilos Personalizados ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3em; 
        background-color: #c0392b; 
        color: white; 
        font-weight: bold;
    }
    .chapter-box {
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        border-left: 5px solid #c0392b;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Diccionario de Modelos 2026 ---
MODELS = {
    "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
    "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
    "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
    "Qwen 3.5 Plus (2026)": "qwen/qwen3.5-plus-20260420",
    "Llama 3.1 405B": "meta-llama/llama-3.1-405b",
    "GPT-4o Mini": "openai/gpt-4o-mini"
}

# --- Inicialización de Estado ---
if 'libro_dict' not in st.session_state:
    st.session_state['libro_dict'] = {}
if 'plan_editorial' not in st.session_state:
    st.session_state['plan_editorial'] = ""

# --- Funciones Core ---
def call_openrouter(prompt, key, model):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]})
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- Barra Lateral ---
with st.sidebar:
    st.title("🇪🇸 Control Editorial")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model_choice = st.selectbox("Cerebro Lógico", list(MODELS.keys()))
    st.divider()
    st.info("Estrategia: 12 Capítulos de 2200 palabras cada uno. Enfoque exclusivo en Amazon.es.")

# --- Menú de Navegación ---
tab1, tab2, tab3 = st.tabs(["🔍 1. Tendencias", "🧠 2. Plan Abductivo", "✍️ 3. Escritura por Capítulos"])

# --- TAB 1: TENDENCIAS ---
with tab1:
    st.header("Predicción de Nichos en España")
    col_m, col_a = st.columns(2)
    with col_m: mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    with col_a: anio = st.selectbox("Año", [2026, 2027, 2028])
    
    if st.button("Buscar Anomalías de Mercado"):
        prompt = f"Actúa como analista senior de KDP España. Predice 5 nichos para {mes} de {anio} en España. Usa la lógica de Peirce para identificar un 'hecho sorprendente' en cada uno."
        with st.spinner("Analizando Amazon.es..."):
            res = call_openrouter(prompt, api_key, MODELS[model_choice])
            st.write(res)

# --- TAB 2: PLAN EDITORIAL ---
with tab2:
    st.header("Planificación de la Obra")
    tendencia = st.text_area("Introduce la tendencia o idea elegida:")
    if st.button("Generar Plan de 12 Capítulos"):
        prompt_plan = f"""
        Crea un plan editorial de 12 capítulos para un libro basado en '{tendencia}'.
        Aplica la abducción de Peirce (Hecho C -> Hipótesis A).
        REGLAS: Títulos con mayúscula inicial solo en la primera palabra. 
        Incluye Título, Subtítulo y breve descripción de cada capítulo.
        """
        with st.spinner("Estructurando plan editorial..."):
            st.session_state['plan_editorial'] = call_openrouter(prompt_plan, api_key, MODELS[model_choice])
            st.success("Plan generado.")
    
    if st.session_state['plan_editorial']:
        st.markdown(st.session_state['plan_editorial'])

# --- TAB 3: ESCRITURA ---
with tab3:
    st.header("Redacción del Manuscrito (Capítulo a Capítulo)")
    if not st.session_state['plan_editorial']:
        st.warning("Primero genera un plan en la pestaña anterior.")
    else:
        # Selector de capítulo
        n_cap = st.select_slider("Selecciona el capítulo a redactar:", options=list(range(1, 13)))
        
        st.markdown(f"### Redactando Capítulo {n_cap}")
        if st.button(f"🚀 Generar Capítulo {n_cap} (2200 palabras)"):
            # Recuperar contexto previo
            contexto = "Inicio del libro."
            if n_cap > 1 and (n_cap-1) in st.session_state['libro_dict']:
                contexto = f"Resumen del final del capítulo anterior: {st.session_state['libro_dict'][n_cap-1][-1500:]}"
            
            prompt_write = f"""
            Escribe el Capítulo {n_cap} basado en este plan: {st.session_state['plan_editorial']}.
            Contexto anterior: {contexto}
            
            CONVENCIONES:
            - Extensión: Mínimo 2200 palabras (profundidad máxima).
            - Estilo: Español de España, comillas « », mayúscula inicial solo al principio del título.
            - Inicio: '# Capítulo {n_cap}: [Título]'.
            - No repitas definiciones de capítulos anteriores. Avanza en la tesis.
            """
            with st.spinner(f"Escribiendo {n_cap}/12..."):
                contenido = call_openrouter(prompt_write, api_key, MODELS[model_choice])
                st.session_state['libro_dict'][n_cap] = contenido
        
        # Previsualización y descarga
        if n_cap in st.session_state['libro_dict']:
            st.markdown("---")
            st.markdown(st.session_state['libro_dict'][n_cap])
            
        st.divider()
        if len(st.session_state['libro_dict']) > 0:
            st.subheader("Compilación Final")
            caps_listos = sorted(st.session_state['libro_dict'].keys())
            st.write(f"Capítulos listos: {caps_listos}")
            
            full_text = "\n\n".join([st.session_state['libro_dict'][k] for k in caps_listos])
            st.download_button(
                label="📥 Descargar Libro Completo (.md)",
                data=full_text,
                file_name=f"libro_kdp_espana.md",
                mime="text/markdown"
            )
