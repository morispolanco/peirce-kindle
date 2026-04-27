import streamlit as st
import requests
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Escritor Editorial Pro | KDP",
    page_icon="🖋️",
    layout="wide"
)

# --- ESTILOS CSS CORREGIDOS ---
st.markdown(
    """
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #2c3e50; 
        color: white;
        font-weight: bold;
    }
    .stTextArea textarea {
        font-family: 'Georgia', serif;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

## --- BARRA LATERAL: CONFIGURACIÓN ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password", help="Introduce tu clave de API de OpenRouter.")
    
    model_options = {
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "GPT-4o": "openai/gpt-4o",
        "Llama 3.1 405B": "meta-llama/llama-3.1-405b-instruct",
        "Claude 3 Opus": "anthropic/claude-3-opus",
        "DeepSeek V3": "deepseek/deepseek-chat",
        "Gemini Flash 1.5": "google/gemini-flash-1.5",
        "Gemma 2 27B": "google/gemma-2-27b-it",
        "Mistral Large 2": "mistralai/mistral-large-2407",
        "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct",
        "Phi-3 Medium": "microsoft/phi-3-medium-128k-instruct"
    }
    
    selected_model = st.selectbox("Modelo de Lenguaje", list(model_options.keys()))
    genre = st.selectbox("Género Editorial", ["Ensayo Filosófico", "Derecho y Crítica", "Historia de Guatemala", "Estrategia de Negocios"])
    
    st.divider()
    st.caption("Estilo: KDP Estándar")
    st.caption("Ortografía: RAE + Comillas Españolas")

## --- FUNCIONES DE NÚCLEO ---

def call_openrouter(prompt, api_key, model):
    """Llamada a la API de OpenRouter con manejo de errores."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_options[model],
        "messages": [
            {
                "role": "system", 
                "content": "Eres un escritor editorial de élite. Tu prosa es limpia, precisa y académica. No usas lenguaje de relleno ni comentarios de IA."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error de API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

## --- INTERFAZ PRINCIPAL ---

st.title("🖋️ Generador Editorial Automático")
st.write("Crea libros completos capítulo a capítulo con coherencia interna y estilo profesional.")

# Entrada del Plan Editorial
plan_editorial = st.text_area(
    "Pega aquí tu Plan Editorial (un capítulo por línea):", 
    height=250,
    placeholder="Capítulo 1: La génesis del pensamiento barroco\nCapítulo 2: El ingenio como herramienta analítica..."
)

# Inicialización de estados
if "libro_completo" not in st.session_state:
    st.session_state.libro_completo = ""
if "capitulos_generados" not in st.session_state:
    st.session_state.capitulos_generados = []

if st.button("🚀 Iniciar Generación Secuencial"):
    if not api_key:
        st.error("Falta la API Key.")
    elif not plan_editorial:
        st.warning("Por favor, introduce el plan editorial.")
    else:
        # Limpieza de líneas del plan
        lineas = [line.strip() for line in plan_editorial.split('\n') if line.strip()]
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        contexto_previo = "" # Memoria para evitar repeticiones
        st.session_state.capitulos_generados = [] # Reiniciar si se pulsa de nuevo

        for idx, linea in enumerate(lineas):
            n_cap = idx + 1
            status_text.info(f"⏳ Procesando Capítulo {n_cap}: {linea}...")
            
            # Prompt de ingeniería para cumplir los requisitos estrictos
            prompt = f"""
            Escribe el texto íntegro del siguiente capítulo para un libro de {genre}.
            
            TEMA DEL CAPÍTULO: {linea}
            CONTEXTO DEL LIBRO (Hasta ahora): {contexto_previo[-1500:]}
            
            REGLAS DE OBLIGADO CUMPLIMIENTO:
            1. EXTENSIÓN: El capítulo debe tener entre 2000 y 2200 palabras. No te detengas hasta alcanzar este volumen de análisis profundo.
            2. FORMATO DE TÍTULO: Comienza exactamente con '# Capítulo {n_cap}: [Título]'. Solo la primera palabra y nombres propios en mayúscula.
            3. SUBTÍTULOS: Usa '## [Subtítulo]'. Solo mayúscula inicial en la primera palabra.
            4. ORTOGRAFÍA: Usa estrictamente comillas españolas (« »). Gramática impecable según la RAE.
            5. ESTILO: Evita el exceso de adjetivos. Busca una prosa sobria, clara y directa.
            6. ESTRUCTURA: Debe incluir una sección de contraargumentación (objeciones a la tesis planteada) y su respectiva respuesta dialéctica.
            7. COHERENCIA: Verifica que no se repitan conceptos ya explicados en el contexto anterior.
            8. LIMPIEZA: No añadas saludos, despedidas, ni comentarios como "Aquí tienes el capítulo". Entrega solo el contenido en Markdown.
            """
            
            contenido = call_openrouter(prompt, api_key, selected_model)
            
            if "Error" in contenido:
                st.error(contenido)
                break
                
            st.session_state.capitulos_generados.append(contenido)
            
            # Actualizar contexto para el siguiente capítulo
            # Tomamos un resumen implícito de lo generado
            contexto_previo += f"\nEn el capítulo {n_cap} se trató: {linea}. No repetir estos puntos clave."
            
            progress_bar.progress((idx + 1) / len(lineas))
            
        st.session_state.libro_completo = "\n\n---\n\n".join(st.session_state.capitulos_generados)
        status_text.success("✅ ¡Libro generado con éxito!")

## --- EXPORTACIÓN ---

if st.session_state.libro_completo:
    st.divider()
    st.subheader("📄 Resultado Final")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="⬇️ Descargar archivo Markdown (.md)",
            data=st.session_state.libro_completo,
            file_name="manuscrito_kdp.md",
            mime="text/markdown"
        )
    
    with col2:
        if st.button("🧹 Limpiar sesión"):
            st.session_state.libro_completo = ""
            st.session_state.capitulos_generados = []
            st.rerun()

    with st.expander("🔍 Previsualizar Manuscrito"):
        st.markdown(st.session_state.libro_completo)
