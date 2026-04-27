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
    .stTextArea textarea { font-size: 14px; line-height: 1.6; font-family: 'Georgia', serif; }
    </style>
    """, 
    unsafe_allow_html=True
)

## --- LÓGICA DE PROCESAMIENTO ---

def call_openrouter(prompt, api_key, model_id):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Eres un autor y editor profesional. Tu prosa es limpia, académica y profunda. Usas comillas españolas (« »)."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error de la API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def extraer_esencia_editorial(plan_completo, api_key, model_id):
    prompt = f"""
    Analiza este plan editorial complejo y extrae la INTENCIÓN ESTRATÉGICA. 
    Resume obligatoriamente: 
    1. Público objetivo y tono de voz.
    2. Diferenciación y razones del éxito previstas.
    3. Estructura lógica de los capítulos identificados.
    
    PLAN EDITORIAL:
    {plan_completo}
    
    Responde solo con la síntesis técnica para guiar la escritura.
    """
    return call_openrouter(prompt, api_key, model_id)

## --- BARRA LATERAL ---

with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Persistencia de la API Key en el estado de sesión
    if "api_key_saved" not in st.session_state:
        st.session_state.api_key_saved = ""
    
    api_key_input = st.text_input("OpenRouter API Key", type="password", value=st.session_state.api_key_saved)
    if api_key_input:
        st.session_state.api_key_saved = api_key_input

    model_options = {
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
    
    selected_name = st.selectbox("Selecciona el Modelo", list(model_options.keys()))
    selected_model_id = model_options[selected_name]

    # Menú de 20 subgéneros de no ficción
    no_fiction_genres = [
        "Ensayo Filosófico", "Derecho y Crítica Legal", "Historia Contemporánea",
        "Biografía Académica", "Manual de Estrategia de Negocios", "Tratado de Sociología",
        "Divulgación Científica", "Economía Política", "Desarrollo Personal / Psicología",
        "Periodismo de Investigación", "Crítica Literaria", "Filosofía de la Tecnología",
        "Guía de Gestión Pública", "Análisis Geopolítico", "Historia de las Ideas",
        "Ética y Moral", "Educación y Pedagogía", "Antropología Cultural",
        "Teología y Religión", "Comunicación y Retórica"
    ]
    genre = st.selectbox("Subgénero de No Ficción", no_fiction_genres)

## --- FLUJO PRINCIPAL ---

st.title("🖋️ Escritura Editorial Basada en Estrategia")
st.info("Sube tu plan editorial complejo. El sistema analizará el público y la intención antes de redactar cada capítulo.")

plan_input = st.text_area("Cargar Plan Editorial Completo:", height=250, placeholder="Pega aquí todo el documento del plan editorial (síntesis, público, capítulos, etc.)...")

if "manuscrito" not in st.session_state:
    st.session_state.manuscrito = ""
if "esencia" not in st.session_state:
    st.session_state.esencia = ""

if st.button("🚀 Analizar Plan e Iniciar Libro"):
    if not st.session_state.api_key_saved or not plan_input:
        st.error("Se requiere la API Key y el contenido del plan editorial.")
    else:
        with st.status("Destilando estrategia editorial...", expanded=True) as status:
            # 1. Extraer esencia estratégica
            esencia = extraer_esencia_editorial(plan_input, st.session_state.api_key_saved, selected_model_id)
            st.session_state.esencia = esencia
            st.write("**Estrategia de redacción establecida.**")
            
            # 2. Identificar capítulos del plan
            prompt_caps = f"Basado en el plan editorial, lista exclusivamente los títulos de capítulos a escribir. Uno por línea, sin números.\n\nPLAN:\n{plan_input}"
            lista_caps_raw = call_openrouter(prompt_caps, st.session_state.api_key_saved, selected_model_id)
            lista_caps = [c.strip() for c in lista_caps_raw.split('\n') if len(c.strip()) > 5]
            
            capitulos_finales = []
            contexto_previo = ""

            # 3. Escritura secuencial
            for i, titulo in enumerate(lista_caps):
                n_cap = i + 1
                st.write(f"✍️ Redactando Capítulo {n_cap}: {titulo}...")
                
                prompt_redaccion = f"""
                Escribe el texto completo del capítulo indicado para un libro de {genre}.
                ESTRATEGIA EDITORIAL: {st.session_state.esencia}
                TEMA DEL CAPÍTULO: {titulo}
                CONTEXTO PREVIO: {contexto_previo[-1500:]}
                
                REGLAS CRÍTICAS DE ESTILO:
                1. EXTENSIÓN: Entre 2000 y 2200 palabras. Desarrollo intelectual profundo.
                2. TÍTULO: '# Capítulo {n_cap}: {titulo.capitalize()}'.
                3. CAPITALIZACIÓN: Títulos y subtítulos con mayúscula inicial solo en la primera palabra.
                4. ORTOGRAFÍA: Usa estrictamente comillas españolas (« ») y gramática RAE.
                5. ESTRUCTURA: Incluye obligatoriamente una sección de contraargumentación y su respuesta sólida.
                6. ADJETIVACIÓN: Mínima y precisa. Estilo profesional y directo.
                7. LIMPIEZA: No incluyas comentarios, introducciones o cierres de la IA. Solo Markdown.
                """
                
                cap_texto = call_openrouter(prompt_redaccion, st.session_state.api_key_saved, selected_model_id)
                capitulos_finales.append(cap_texto)
                contexto_previo += f"\nCapítulo {n_cap}: {titulo}."
                
            st.session_state.manuscrito = "\n\n---\n\n".join(capitulos_finales)
            status.update(label="¡Libro Completo!", state="complete", expanded=False)

## --- EXPORTACIÓN ---
if st.session_state.manuscrito:
    st.divider()
    st.subheader("📄 Manuscrito Finalizado")
    
    st.download_button(
        "⬇️ Descargar Libro en Markdown (.md)",
        st.session_state.manuscrito,
        file_name="manuscrito_kdp.md",
        mime="text/markdown"
    )
    
    with st.expander("Ver Resumen Estratégico aplicado"):
        st.write(st.session_state.esencia)
    
    st.markdown(st.session_state.manuscrito)
