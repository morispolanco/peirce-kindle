import streamlit as st
import requests
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Escritor Editorial Inteligente",
    page_icon="📚",
    layout="wide"
)

# --- ESTILOS CSS ---
st.markdown(
    """
    <style>
    .main { background-color: #f4f7f6; }
    .stButton>button { 
        width: 100%; border-radius: 4px; height: 3em; 
        background-color: #1a1a1a; color: white; font-weight: bold;
    }
    .stTextArea textarea { font-size: 14px; line-height: 1.6; }
    </style>
    """, 
    unsafe_allow_html=True
)

## --- LÓGICA DE PROCESAMIENTO ---

def call_openrouter(prompt, api_key, model):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_options[model],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def extraer_esencia_editorial(plan_completo, api_key, model):
    """Analiza el plan complejo para extraer la intención, público y estilo."""
    prompt = f"""
    Analiza el siguiente plan editorial complejo y extrae una 'Guía de Estilo y Propósito' sintética. 
    Identifica: 
    1. Público objetivo.
    2. Tono de voz (formal, académico, persuasivo, etc.).
    3. Propuesta de valor/Diferenciación.
    4. Estructura de capítulos (solo títulos y breve descripción).
    
    PLAN EDITORIAL:
    {plan_completo}
    
    Responde solo con la síntesis estructurada para ser usada como contexto de escritura.
    """
    return call_openrouter(prompt, api_key, model)

## --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    model_options = {
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "GPT-4o": "openai/gpt-4o",
        "Llama 3.1 405B": "meta-llama/llama-3.1-405b-instruct",
        "DeepSeek V3": "deepseek/deepseek-chat",
        "Gemini Pro 1.5": "google/gemini-pro-1.5",
        "Mistral Large 2": "mistralai/mistral-large-2407"
    }
    selected_model = st.selectbox("Cerebro del Escritor", list(model_options.keys()))
    genre = st.text_input("Género (KDP)", value="Ensayo Académico / Thriller")

## --- FLUJO PRINCIPAL ---

st.title("🖋️ Escritura Basada en Plan Editorial Complejo")
st.info("Pega tu plan editorial completo (con síntesis, público, diferenciación, etc.). La IA extraerá la intención estratégica automáticamente.")

plan_input = st.text_area("Cargar Plan Editorial Completo:", height=300)

if "manuscrito" not in st.session_state:
    st.session_state.manuscrito = ""
if "esencia" not in st.session_state:
    st.session_state.esencia = ""

if st.button("🚀 Analizar y Escribir Libro"):
    if not api_key or not plan_input:
        st.error("Se requiere la API Key y el contenido del plan.")
    else:
        # Paso 1: Extracción de la Esencia
        with st.status("Analizando estrategia editorial...", expanded=True) as status:
            esencia = extraer_esencia_editorial(plan_input, api_key, selected_model)
            st.session_state.esencia = esencia
            st.write("**Estrategia Extraída:**")
            st.caption(esencia)
            
            # Paso 2: Identificar Capítulos
            # Pedimos a la IA que nos dé una lista limpia de capítulos basada en el análisis
            prompt_caps = f"Basado en esta esencia: {esencia}, genera una lista simple de los títulos de capítulos a escribir. Uno por línea."
            lista_caps = call_openrouter(prompt_caps, api_key, selected_model).split('\n')
            lista_caps = [c.strip() for c in lista_caps if c.strip()]
            
            capitulos_finales = []
            contexto_acumulado = ""

            # Paso 3: Generación Secuencial
            for i, titulo in enumerate(lista_caps):
                st.write(f"✍️ Redactando Capítulo {i+1}...")
                
                prompt_redaccion = f"""
                Eres un autor profesional. Escribe el siguiente capítulo siguiendo estrictamente estos criterios:
                
                ESTRATEGIA EDITORIAL: {st.session_state.esencia}
                CAPÍTULO ACTUAL: {titulo}
                GÉNERO: {genre}
                COHERENCIA (Capítulos anteriores): {contexto_acumulado[-1500:]}
                
                REGLAS DE ESTILO:
                - Longitud: 2000 a 2200 palabras.
                - Formato Título: '# Capítulo {i+1}: [Título con solo mayúscula inicial]'.
                - Subtítulos: Solo mayúscula inicial.
                - Ortografía: Comillas españolas (« ») y gramática RAE.
                - Estructura: Incluye contraargumentación y respuesta sólida.
                - Adjetivación: Mínima y precisa.
                - Sin comentarios de IA.
                """
                
                cap_texto = call_openrouter(prompt_redaccion, api_key, selected_model)
                capitulos_finales.append(cap_texto)
                contexto_acumulado += f"\nCapítulo {i+1} finalizado: {titulo}."
                
            st.session_state.manuscrito = "\n\n---\n\n".join(capitulos_finales)
            status.update(label="¡Libro Completo!", state="complete", expanded=False)

## --- DESCARGA ---
if st.session_state.manuscrito:
    st.success("Generación finalizada.")
    st.download_button(
        "⬇️ Descargar Manuscrito para KDP (.md)",
        st.session_state.manuscrito,
        file_name="libro_final.md"
    )
    with st.expander("Ver Análisis de Intención"):
        st.write(st.session_state.esencia)
