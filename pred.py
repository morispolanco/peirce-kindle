import streamlit as st
import requests
import json

# --- Configuración de la interfaz ---
st.set_page_config(
    page_title="KDP España Pro: Escritor Abductivo", 
    page_icon="🇪🇸", 
    layout="wide"
)

# --- Estilos Personalizados ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background-color: #c0392b; 
        color: white; 
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #e74c3c; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- Diccionario de Modelos Actualizado (2026) ---
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

# --- Lógica de Comunicación con OpenRouter ---
def call_openrouter(prompt, key, model):
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
        return f"Error en la API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error crítico: {str(e)}"

# --- Barra Lateral: Configuración ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model_name = st.selectbox("Cerebro Lógico (LLM):", list(MODELS.keys()))
    selected_model = MODELS[model_name]
    st.divider()
    st.markdown("""
    **Configuración Editorial:**
    - 📍 Mercado: Amazon.es
    - 📖 Capítulos: 12
    - ✍️ Objetivo: 2200 palabras/cap.
    - 🧠 Lógica: Abducción de Peirce
    """)

# --- Cuerpo Principal ---
st.title("🧠 KDP Abductor: Generador de Libros para España")

# ETAPA 1: PREDICCIÓN DE TENDENCIAS
st.header("1. Predicción de Tendencias Locales")
c1, c2 = st.columns(2)
with c1: mes = st.selectbox("Mes de publicación", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
with c2: anio = st.selectbox("Año", [2026, 2027, 2028])

if st.button("🔍 Predecir Tendencias en España"):
    if not api_key: st.error("Falta API Key")
    else:
        prompt_trends = f"""
        Actúa como analista de mercado senior para Amazon.es. 
        Predice 5 tendencias de nicho emergentes en España para {mes} de {anio}.
        Considera la cultura española, leyes locales (como la LOMLOE o el Estatuto del Trabajo) y la economía actual.
        Para cada tendencia, identifica un 'Hecho Sorprendente' (Anomalía) según Charles Peirce.
        """
        with st.spinner("Escaneando el horizonte español..."):
            trends = call_openrouter(prompt_trends, api_key, selected_model)
            st.session_state['trends_es'] = trends

if 'trends_es' in st.session_state:
    st.info(st.session_state['trends_es'])
    
    # ETAPA 2: ANÁLISIS ABDUCTIVO Y PLAN
    st.header("2. Salto Abductivo y Plan Editorial")
    tendencia_sel = st.text_input("Copia y pega la tendencia que deseas desarrollar:")
    
    if st.button("🧠 Generar Plan de 12 Capítulos"):
        prompt_plan = f"""
        Realiza un análisis abductivo de Peirce para la tendencia: '{tendencia_sel}'.
        Propón una Hipótesis (A) que explique la anomalía detectada.
        Luego, crea un PLAN EDITORIAL de 12 capítulos para un libro de Kindle.
        
        REGLAS DE TÍTULOS: Mayúscula inicial solo en la primera palabra y nombres propios.
        Incluye: Título, Subtítulo y Síntesis de la propuesta de valor para el mercado español.
        """
        with st.spinner("Realizando inferencia lógica..."):
            plan = call_openrouter(prompt_plan, api_key, selected_model)
            st.session_state['plan_es'] = plan

if 'plan_es' in st.session_state:
    st.divider()
    st.markdown(st.session_state['plan_es'])

    # ETAPA 3: ESCRITURA CON MEMORIA NARRATIVA
    st.header("3. Redacción del Manuscrito")
    if st.button("✍️ Escribir Libro Completo (Memoria Avanzada)"):
        if not api_key: st.error("Falta API Key")
        else:
            full_book = ""
            prog_bar = st.progress(0)
            status_text = st.empty()
            contexto_previo = "Este es el inicio del libro."
            
            for i in range(1, 13):
                status_text.markdown(f"**Redactando Capítulo {i} de 12...** (Objetivo: 2200 palabras)")
                
                prompt_cap = f"""
                Actúa como un autor profesional. Escribe el Capítulo {i} basado en este plan: {st.session_state['plan_es']}.
                
                CONTEXTO NARRATIVO ANTERIOR:
                {contexto_previo}
                
                DIRECTRICES DE ESCRITURA:
                1. AVANCE NARRATIVO: No repitas definiciones de abducción o contextos que ya se hayan explicado. Construye sobre lo anterior.
                2. EXTENSIÓN: Aproximadamente 2200 palabras. Sé profundo, analítico y exhaustivo.
                3. PUNTUACIÓN: Usa comillas españolas (« »).
                4. TÍTULOS: '# Capítulo {i}: [Título con mayúscula solo al inicio]'.
                5. TONO: Español de España, formal, sin comentarios de IA.
                """
                
                cap_content = call_openrouter(prompt_cap, api_key, selected_model)
                full_book += cap_content + "\n\n"
                
                # Actualización de la memoria para el siguiente capítulo (últimos párrafos)
                contexto_previo = f"En el capítulo anterior ({i}) se concluyó lo siguiente: {cap_content[-1500:]}"
                
                prog_bar.progress(i / 12)
            
            st.session_state['full_book_es'] = full_book
            st.success("¡Manuscrito completado con éxito!")

# ETAPA 4: EXPORTACIÓN
if 'full_book_es' in st.session_state:
    st.divider()
    st.subheader("💾 Descargar Compilación Final")
    
    st.download_button(
        label="📥 Descargar Libro en Markdown (.md)",
        data=st.session_state['full_book_es'],
        file_name=f"kdp_espana_{anio}_{mes}.md",
        mime="text/markdown"
    )
    
    with st.expander("Previsualizar Manuscrito"):
        st.markdown(st.session_state['full_book_es'])
