import streamlit as st
import requests
import json

# --- Configuración y Estilos ---
st.set_page_config(page_title="KDP España: Escritura Garantizada", page_icon="🇪🇸", layout="wide")

# --- Modelos 2026 ---
MODELS = {
    "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
    "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
    "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
    "Llama 3.1 405B": "meta-llama/llama-3.1-405b"
}

def call_openrouter(prompt, key, model):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]})
        )
        return response.json()['choices'][0]['message']['content']
    except:
        return "Error en la conexión. Reintente."

# --- Estado de la Sesión ---
if 'libro_progresivo' not in st.session_state:
    st.session_state['libro_progresivo'] = {} # Diccionario para guardar cada capítulo

# --- Interfaz ---
with st.sidebar:
    st.title("🛡️ Control de Fallos")
    api_key = st.text_input("API Key", type="password")
    model_name = st.selectbox("Modelo", list(MODELS.keys()))
    st.info("Esta versión genera un capítulo a la vez para evitar cortes de conexión.")

st.title("📚 Generador de Libros KDP: Proceso Estratificado")

# ETAPA 1 Y 2 (Resumidas para brevedad)
tema = st.text_input("Palabra clave o tendencia elegida:", "Inteligencia Artificial en el sistema educativo español")
plan_guia = st.text_area("Plan Editorial (Pega aquí el plan de 12 capítulos generado previamente):")

if plan_guia:
    st.divider()
    st.header("✍️ Escritura Controlada")
    
    # Creamos 12 columnas o un selector para elegir qué capítulo escribir
    num_cap = st.number_input("Selecciona el capítulo a redactar:", min_value=1, max_value=12, step=1)
    
    col_write, col_view = st.columns([1, 2])
    
    with col_write:
        if st.button(f"🚀 Redactar Capítulo {num_cap}"):
            if not api_key:
                st.error("Introduce la API Key")
            else:
                # Recuperar contexto del capítulo anterior si existe
                contexto_previo = ""
                if num_cap > 1 and (num_cap - 1) in st.session_state['libro_progresivo']:
                    contexto_previo = f"El capítulo anterior terminó así: {st.session_state['libro_progresivo'][num_cap-1][-1000:]}"
                
                prompt = f"""
                Escribe el Capítulo {num_cap} del libro basado en: {plan_guia}.
                Contexto anterior: {contexto_previo}
                REGLAS: ~2200 palabras, comillas « », mayúscula inicial solo en la primera palabra del título. 
                Formato: '# Capítulo {num_cap}: [Título]'.
                """
                
                with st.spinner(f"Escribiendo capítulo {num_cap}..."):
                    contenido = call_openrouter(prompt, api_key, MODELS[model_name])
                    st.session_state['libro_progresivo'][num_cap] = contenido
                    st.success(f"Capítulo {num_cap} guardado en memoria.")

    with col_view:
        if num_cap in st.session_state['libro_progresivo']:
            st.markdown("### Previsualización del Capítulo:")
            st.markdown(st.session_state['libro_progresivo'][num_cap])
        else:
            st.warning("Este capítulo aún no ha sido redactado.")

    # COMPILACIÓN Y DESCARGA
    st.divider()
    if len(st.session_state['libro_progresivo']) > 0:
        st.header("📥 Compilación Final")
        capitulos_listos = sorted(st.session_state['libro_progresivo'].keys())
        st.write(f"Capítulos redactados: {capitulos_listos}")
        
        libro_completo = "\n\n".join([st.session_state['libro_progresivo'][k] for k in capitulos_listos])
        
        st.download_button(
            label="💾 Descargar Libro Compilado (.md)",
            data=libro_completo,
            file_name="manuscrito_seguro.md",
            mime="text/markdown"
        )
