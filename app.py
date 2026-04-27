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

## --- LÓGICA DE PERSISTENCIA REAL ---
# Usamos cache_resource para que la clave sobreviva al "refresh" del navegador
# mientras el servidor de Streamlit esté corriendo.
@st.cache_resource
def get_persistent_key():
    return {"key": ""}

persistence = get_persistent_key()

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
            {"role": "system", "content": "Eres un autor profesional. Usas comillas españolas (« ») y prosa académica profunda."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

def extraer_esencia_editorial(plan_completo, api_key, model_id):
    prompt = f"Analiza este plan editorial y extrae público, tono y estructura:\n\n{plan_completo}"
    return call_openrouter(prompt, api_key, model_id)

## --- BARRA LATERAL ---

with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Si ya hay una clave guardada en el recurso persistente, la usamos
    current_key = persistence["key"]
    
    api_key_input = st.text_input("OpenRouter API Key", type="password", value=current_key)
    
    if api_key_input != current_key:
        persistence["key"] = api_key_input
        st.success("API Key guardada para esta sesión.")

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
    
    selected_name = st.selectbox("Modelo", list(model_options.keys()))
    selected_model_id = model_options[selected_name]

    no_fiction_genres = [
        "Ensayo Filosófico", "Derecho y Crítica Legal", "Historia Contemporánea",
        "Biografía Académica", "Manual de Estrategia de Negocios", "Tratado de Sociología",
        "Divulgación Científica", "Economía Política", "Desarrollo Personal",
        "Periodismo de Investigación", "Crítica Literaria", "Filosofía de la Tecnología",
        "Guía de Gestión Pública", "Análisis Geopolítico", "Historia de las Ideas",
        "Ética y Moral", "Educación y Pedagogía", "Antropología Cultural",
        "Teología y Religión", "Comunicación y Retórica"
    ]
    genre = st.selectbox("Subgénero de No Ficción", no_fiction_genres)

## --- FLUJO PRINCIPAL ---

st.title("🖋️ Escritura Editorial")
plan_input = st.text_area("Cargar Plan Editorial Completo:", height=250)

if "manuscrito" not in st.session_state:
    st.session_state.manuscrito = ""

if st.button("🚀 Iniciar Libro"):
    active_key = persistence["key"]
    if not active_key:
        st.error("Por favor, introduce la API Key en la barra lateral.")
    elif not plan_input:
        st.error("El plan editorial está vacío.")
    else:
        with st.status("Procesando...", expanded=True) as status:
            esencia = extraer_esencia_editorial(plan_input, active_key, selected_model_id)
            
            prompt_caps = f"Lista títulos de capítulos (uno por línea):\n{plan_input}"
            lista_caps_raw = call_openrouter(prompt_caps, active_key, selected_model_id)
            lista_caps = [c.strip() for c in lista_caps_raw.split('\n') if len(c.strip()) > 5]
            
            capitulos_finales = []
            contexto_previo = ""

            for i, titulo in enumerate(lista_caps):
                n_cap = i + 1
                st.write(f"✍️ Redactando Capítulo {n_cap}: {titulo}...")
                
                prompt_redaccion = f"""
                Escribe el capítulo {n_cap} de un libro de {genre}.
                TÍTULO: '# Capítulo {n_cap}: {titulo.capitalize()}'.
                ESTRATEGIA: {esencia}
                REGLAS: 2000-2200 palabras, comillas españolas « », contraargumentación necesaria.
                """
                
                cap_texto = call_openrouter(prompt_redaccion, active_key, selected_model_id)
                capitulos_finales.append(cap_texto)
                contexto_previo += f"\nCap {n_cap} hecho."
                
            st.session_state.manuscrito = "\n\n---\n\n".join(capitulos_finales)
            status.update(label="¡Libro Completo!", state="complete")

if st.session_state.manuscrito:
    st.download_button("⬇️ Descargar .md", st.session_state.manuscrito, file_name="libro.md")
    st.markdown(st.session_state.manuscrito)
