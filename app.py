import streamlit as st
import requests
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Escritor Editorial Inteligenteimport streamlit as st
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

def call_openrouter(prompt, api_key, model_id):
    """Llamada optimizada a OpenRouter."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Eres un editor y escritor profesional de alto nivel, experto en gramática española y publicaciones para Amazon KDP."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4 # Menor temperatura para mayor consistencia
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error de la API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def extraer_esencia_editorial(plan_completo, api_key, model_id):
    """Destila el plan complejo para guiar la escritura."""
    prompt = f"""
    Analiza este plan editorial complejo y extrae la INTENCIÓN ESTRATÉGICA. 
    Identifica y resume para el autor:
    1. Perfil psicográfico del público.
    2. Tono exacto y diferenciación competitiva.
    3. Temas recurrentes que deben aparecer en cada capítulo.
    
    PLAN EDITORIAL:
    {plan_completo}
    
    Responde con una síntesis técnica para guiar la generación de texto.
    """
    return call_openrouter(prompt, api_key, model_id)

## --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    # Diccionario corregido con comas y IDs de OpenRouter actualizados
    model_options = {
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "Gemini 1.5 Pro": "google/gemini-pro-1.5",
        "GPT-4o": "openai/gpt-4o",
        "Llama 3.1 405B": "meta-llama/llama-3.1-405b-instruct",
        "DeepSeek V3": "deepseek/deepseek-chat",
        "Mistral Large 2": "mistralai/mistral-large-2407",
        "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct"
    }
    
    selected_name = st.selectbox("Cerebro del Escritor", list(model_options.keys()))
    selected_model_id = model_options[selected_name]
    genre = st.text_input("Género (KDP)", value="Ensayo Filosófico / Thriller Legal")

## --- FLUJO PRINCIPAL ---

st.title("🖋️ Escritura Basada en Plan Editorial Complejo")
st.info("Pega tu plan editorial completo. La aplicación analizará el público, la síntesis y la diferenciación antes de redactar.")

plan_input = st.text_area("Cargar Plan Editorial Completo:", height=300, placeholder="Pega aquí el plan con síntesis, público, capítulos...")

if "manuscrito" not in st.session_state:
    st.session_state.manuscrito = ""
if "esencia" not in st.session_state:
    st.session_state.esencia = ""

if st.button("🚀 Analizar y Escribir Libro"):
    if not api_key or not plan_input:
        st.error("Se requiere la API Key y el contenido del plan.")
    else:
        with st.status("Analizando estrategia editorial...", expanded=True) as status:
            # Paso 1: Extracción de la Esencia
            esencia = extraer_esencia_editorial(plan_input, api_key, selected_model_id)
            st.session_state.esencia = esencia
            st.write("**Estrategia de redacción definida.**")
            
            # Paso 2: Identificar Capítulos
            prompt_caps = f"Basado en el plan editorial adjunto, extrae EXCLUSIVAMENTE los títulos de los capítulos que deben escribirse. Devuelve una lista simple, un título por línea, sin números.\n\nPLAN:\n{plan_input}"
            lista_caps_raw = call_openrouter(prompt_caps, api_key, selected_model_id)
            lista_caps = [c.strip() for c in lista_caps_raw.split('\n') if c.strip() and len(c) > 5]
            
            capitulos_finales = []
            contexto_acumulado = ""

            # Paso 3: Generación Secuencial
            for i, titulo in enumerate(lista_caps):
                n_cap = i + 1
                st.write(f"✍️ Redactando Capítulo {n_cap}: {titulo}...")
                
                prompt_redaccion = f"""
                Escribe el texto completo del capítulo indicado. 
                
                ESTRATEGIA EDITORIAL: {st.session_state.esencia}
                GÉNERO: {genre}
                TÍTULO DEL CAPÍTULO: {titulo}
                CONTEXTO PREVIO: {contexto_acumulado[-1500:]}
                
                REQUISITOS INNEGOCIABLES:
                1. LONGITUD: Mínimo 2000 palabras, máximo 2200. Desarrolla los argumentos con profundidad.
                2. TÍTULO: Debe ser exactamente '# Capítulo {n_cap}: {titulo.capitalize()}'.
                3. CAPITALIZACIÓN: Títulos y subtítulos con mayúscula inicial solo en la primera palabra y nombres propios.
                4. PUNTUACIÓN: Usa exclusivamente comillas españolas (« »).
                5. ESTRUCTURA: Integra una sección de contraargumentación y su posterior refutación o respuesta sólida.
                6. ESTILO: Prosa limpia, sin exceso de adjetivos, gramática RAE perfecta.
                7. LIMPIEZA: No incluyas notas de autor ni comentarios de IA. Solo Markdown puro.
                """
                
                cap_texto = call_openrouter(prompt_redaccion, api_key, selected_model_id)
                capitulos_finales.append(cap_texto)
                
                # Alimentamos el contexto para el siguiente capítulo
                contexto_acumulado += f"\nResumen Cap {n_cap}: {titulo}."
                
            st.session_state.manuscrito = "\n\n---\n\n".join(capitulos_finales)
            status.update(label="¡Libro Completo!", state="complete", expanded=False)

## --- DESCARGA ---
if st.session_state.manuscrito:
    st.success("Manuscrito generado.")
    st.download_button(
        "⬇️ Descargar Manuscrito para KDP (.md)",
        st.session_state.manuscrito,
        file_name="libro_final.md",
        mime="text/markdown"
    )
    with st.expander("Ver Análisis de Estrategia Aplicada"):
        st.write(st.session_state.esencia)
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
        "openrouter/free",
        "anthropic/claude-sonnet-4.5",
        "google/gemini-3-flash-preview",
        "qwen/qwen3.5-plus-20260420"
        "minimax/minimax-m2.7",
        "openai/gpt-5.5",
        "openai/gpt-4o-mini",
        "z-ai/glm-5.1"
        "meta-llama/llama-3.1-405b"
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
