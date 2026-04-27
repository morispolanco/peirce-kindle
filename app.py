import streamlit as st
import requests
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Escritor Editorial Inteligente Pro",
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
    .stProgress > div > div > div > div { background-color: #1a1a1a; }
    </style>
    """, 
    unsafe_allow_html=True
)

# --- PERSISTENCIA DE API KEY ---
@st.cache_resource
def get_persistent_key():
    return {"key": ""}

persistence = get_persistent_key()

# --- LÓGICA DE PROCESAMIENTO ---

def call_openrouter(prompt, api_key, model_id):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Eres un autor profesional de alto nivel. Usas comillas españolas (« ») y prosa académica profunda. Tu objetivo es la exhaustividad y el rigor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data), timeout=120)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def extraer_esencia_editorial(plan_completo, api_key, model_id):
    prompt = f"Analiza este plan editorial y extrae público objetivo, tono específico y estructura narrativa principal:\n\n{plan_completo}"
    return call_openrouter(prompt, api_key, model_id)

# --- INICIALIZACIÓN DE ESTADOS (Evita desapariciones) ---
if "manuscrito_lista" not in st.session_state:
    st.session_state.manuscrito_lista = []  # Guardamos capítulos como lista para mayor seguridad
if "lista_caps_titulos" not in st.session_state:
    st.session_state.lista_caps_titulos = []
if "esencia_cache" not in st.session_state:
    st.session_state.esencia_cache = ""

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    current_key = persistence["key"]
    api_key_input = st.text_input("OpenRouter API Key", type="password", value=current_key)
    
    if api_key_input != current_key:
        persistence["key"] = api_key_input
        st.success("API Key vinculada.")

    model_options = {
        "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
        "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
        "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
        "Llama 3.1 405B": "meta-llama/llama-3.1-405b",
        "GPT-4o Mini": "openai/gpt-4o-mini"
    }
    
    selected_name = st.selectbox("Modelo", list(model_options.keys()))
    selected_model_id = model_options[selected_name]

    no_fiction_genres = [
        "Ensayo Filosófico", "Derecho y Crítica Legal", "Historia Contemporánea",
        "Biografía Académica", "Manual de Estrategia de Negocios", "Tratado de Sociología",
        "Divulgación Científica", "Economía Política", "Desarrollo Personal"
    ]
    genre = st.selectbox("Subgénero", no_fiction_genres)

    if st.button("🗑️ Resetear Progreso"):
        st.session_state.manuscrito_lista = []
        st.session_state.lista_caps_titulos = []
        st.session_state.esencia_cache = ""
        st.rerun()

# --- FLUJO PRINCIPAL ---

st.title("🖋️ Escritor Editorial Inteligente")
st.info("Esta versión guarda automáticamente cada capítulo. Si el proceso se detiene, pulsa 'Continuar Escritura'.")

plan_input = st.text_area("Cargar Plan Editorial Completo:", height=200, placeholder="Pega aquí el índice o plan detallado...")

# Lógica del Botón Principal
btn_label = "🚀 Iniciar Libro" if not st.session_state.manuscrito_lista else "🔄 Continuar Escritura"

if st.button(btn_label):
    active_key = persistence["key"]
    
    if not active_key:
        st.error("Introduce la API Key.")
    elif not plan_input:
        st.error("El plan editorial está vacío.")
    else:
        with st.status("Trabajando en la obra...", expanded=True) as status:
            
            # 1. Obtener esencia y títulos si es la primera vez
            if not st.session_state.lista_caps_titulos:
                st.write("🔍 Analizando estructura...")
                st.session_state.esencia_cache = extraer_esencia_editorial(plan_input, active_key, selected_model_id)
                
                prompt_caps = f"Lista exclusivamente los títulos de los capítulos, uno por línea, sin números: \n{plan_input}"
                raw_titles = call_openrouter(prompt_caps, active_key, selected_model_id)
                st.session_state.lista_caps_titulos = [t.strip() for t in raw_titles.split('\n') if len(t.strip()) > 3]

            # 2. Bucle de escritura incremental
            total_caps = len(st.session_state.lista_caps_titulos)
            
            for i, titulo in enumerate(st.session_state.lista_caps_titulos):
                # Si el capítulo ya existe en la lista, lo saltamos
                if i < len(st.session_state.manuscrito_lista):
                    continue
                
                n_cap = i + 1
                st.write(f"✍️ Redactando Capítulo {n_cap}/{total_caps}: **{titulo}**...")
                
                prompt_redaccion = f"""
                Escribe el capítulo {n_cap} de un libro de {genre}.
                TÍTULO: '# Capítulo {n_cap}: {titulo}'.
                CONTEXTO EDITORIAL: {st.session_state.esencia_cache}
                REGLAS: Mínimo 2000 palabras. Usa comillas españolas « ». 
                Estructura: Introducción profunda, desarrollo con contraargumentación y conclusión académica.
                """
                
                contenido_cap = call_openrouter(prompt_redaccion, active_key, selected_model_id)
                
                if "Error" not in contenido_cap:
                    # PERSISTENCIA INMEDIATA
                    st.session_state.manuscrito_lista.append(contenido_cap)
                    # Forzamos un pequeño guardado visual
                    st.toast(f"Capítulo {n_cap} guardado.")
                else:
                    st.error(f"Fallo en capítulo {n_cap}. Deteniendo para evitar pérdida de créditos.")
                    break
            
            status.update(label="Proceso finalizado o pausado.", state="complete")

# --- ÁREA DE DESCARGA Y VISUALIZACIÓN ---

if st.session_state.manuscrito_lista:
    full_text = "\n\n---\n\n".join(st.session_state.manuscrito_lista)
    
    st.divider()
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.subheader("📦 Entrega")
        st.download_button(
            label="⬇️ Descargar Manuscrito (.md)",
            data=full_text,
            file_name="manuscrito_editorial.md",
            mime="text/markdown"
        )
        st.write(f"**Capítulos completados:** {len(st.session_state.manuscrito_lista)}")
    
    with col2:
        st.subheader("📖 Previsualización")
        with st.expander("Ver contenido completo", expanded=True):
            st.markdown(full_text)
