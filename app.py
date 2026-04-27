import streamlit as st
import requests
import json
import time

# Configuración de la página y estética
st.set_page_config(page_title="Escritor Editorial Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1e1e1e; color: white; }
    </style>
    """, unsafe_all_html=True)

## --- TÍTULO Y CONFIGURACIÓN ---
st.title("🖋️ Generador de Libros Académicos y Literarios")
st.subheader("Optimizado para Kindle Direct Publishing (KDP)")

with st.sidebar:
    st.header("Configuración de API")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
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
    
    selected_model = st.selectbox("Selecciona el Modelo", list(model_options.keys()))
    genre = st.selectbox("Género para Estilo KDP", ["Ensayo Filosófico", "Thriller Legal", "Historia", "Negocios"])
    
    st.divider()
    st.info("Este sistema genera capítulos de 2000-2200 palabras con ortografía española estricta.")

## --- LÓGICA DE GENERACIÓN ---

def call_openrouter(prompt, api_key, model):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501", 
        "Content-Type": "application/json"
    }
    data = {
        "model": model_options[model],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

def format_title(title):
    # Solo mayúscula en la primera palabra y nombres propios (simplificado para la IA)
    return title.capitalize()

## --- INTERFAZ PRINCIPAL ---

plan_editorial = st.text_area("Pega aquí el Plan Editorial (Capítulos y estructura):", height=200)

if "libro_completo" not in st.session_state:
    st.session_state.libro_completo = ""
if "capitulos_generados" not in st.session_state:
    st.session_state.capitulos_generados = []

if st.button("Comenzar Generación de Libro"):
    if not api_key or not plan_editorial:
        st.error("Por favor, introduce la API Key y el Plan Editorial.")
    else:
        lineas = [line for line in plan_editorial.split('\n') if line.strip()]
        progress_bar = st.progress(0)
        
        contexto_acumulado = "" # Para mantener coherencia
        
        for i, cap_info in enumerate(lineas):
            st.write(f"Generando: {cap_info}...")
            
            prompt_sistema = f"""
            Actúa como un autor experto en {genre} para Kindle Direct Publishing.
            Escribe el capítulo basado en: {cap_info}.
            
            REGLAS CRÍTICAS:
            1. Longitud: Entre 2000 y 2200 palabras. Desarrolla profundamente cada idea.
            2. Estilo: Evita el exceso de adjetivación. Usa un tono sobrio y preciso.
            3. Ortografía: Usa estrictamente comillas españolas (« »). Gramática impecable.
            4. Estructura de Título: Debe empezar exactamente con '# Capítulo {i+1}: [Título con solo mayúscula inicial]'.
            5. Subtítulos: Solo mayúscula inicial en la primera palabra.
            6. Contenido: Incluye secciones de contraargumentación y respuesta dialéctica.
            7. Coherencia: El capítulo debe conectar con lo anterior: {contexto_acumulado[-1000:] if contexto_acumulado else "Inicio del libro"}.
            8. No incluyas comentarios, introducciones o cierres de la IA. Solo el texto del libro en Markdown.
            """
            
            contenido_cap = call_openrouter(prompt_sistema, api_key, selected_model)
            
            st.session_state.capitulos_generados.append(contenido_cap)
            contexto_acumulado += f"\nResumen del capítulo {i+1}: {contenido_cap[:500]}..." 
            
            progress_bar.progress((i + 1) / len(lineas))
            st.success(f"Capítulo {i+1} completado.")
            time.sleep(2) # Evitar rate limits

        st.session_state.libro_completo = "\n\n---\n\n".join(st.session_state.capitulos_generados)

## --- ÁREA DE DESCARGA Y PREVISUALIZACIÓN ---

if st.session_state.libro_completo:
    st.divider()
    st.header("Libro Compilado")
    
    st.download_button(
        label="Descargar Libro en Markdown (.md)",
        data=st.session_state.libro_completo,
        file_name="libro_generado_kdp.md",
        mime="text/markdown"
    )
    
    with st.expander("Ver Vista Previa del Libro"):
        st.markdown(st.session_state.libro_completo)
