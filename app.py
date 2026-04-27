import streamlit as st
import requests
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Escritor Editorial Pro", page_icon="📚", layout="wide")

## --- PERSISTENCIA ---
@st.cache_resource
def get_persistent_key():
    return {"key": ""}
persistence = get_persistent_key()

## --- LÓGICA DE API ---
def call_openrouter(prompt, api_key, model_id):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Eres un autor profesional. Usas comillas españolas (« ») y prosa académica profunda. Tu precisión numérica es absoluta."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3 # Temperatura baja para mayor precisión en la estructura
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data), timeout=180)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

## --- ESTADOS DE SESIÓN ---
if "manuscrito_lista" not in st.session_state:
    st.session_state.manuscrito_lista = []
if "lista_caps_titulos" not in st.session_state:
    st.session_state.lista_caps_titulos = []
if "esencia_cache" not in st.session_state:
    st.session_state.esencia_cache = ""

## --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key_input = st.text_input("OpenRouter API Key", type="password", value=persistence["key"])
    if api_key_input: persistence["key"] = api_key_input

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
    selected_model_id = model_options[st.selectbox("Modelo", list(model_options.keys()))]
    genre = st.selectbox("Subgénero", ["Ensayo Filosófico", "Derecho", "Historia", "Sociología", "Economía Política", "Ciencia"])

    if st.button("🗑️ Resetear Todo"):
        st.session_state.clear()
        st.rerun()

## --- FLUJO PRINCIPAL ---
st.title("🖋️ Escritura Editorial de Alta Precisión")

plan_input = st.text_area("Cargar Plan Editorial Completo:", height=250)

# PASO 1: EXTRAER Y VALIDAR CAPÍTULOS
if st.button("🔍 1. Analizar Estructura y Validar Capítulos"):
    if not plan_input:
        st.error("El plan está vacío.")
    else:
        with st.spinner("Extrayendo todos los capítulos..."):
            st.session_state.esencia_cache = call_openrouter(f"Resume la esencia de este plan: {plan_input}", persistence["key"], selected_model_id)
            
            # Prompt reforzado para evitar el truncamiento
            prompt_caps = f"""
            Analiza el plan editorial adjunto. 
            Extrae TODOS los títulos de capítulos sin omitir ninguno. 
            Si el plan menciona 24 capítulos, debes listar 24 líneas.
            FORMATO: Solo el título, uno por línea.
            PLAN: {plan_input}
            """
            raw_titles = call_openrouter(prompt_caps, persistence["key"], selected_model_id)
            st.session_state.lista_caps_titulos = [t.strip() for t in raw_titles.split('\n') if len(t.strip()) > 3]
            st.success(f"Se han detectado {len(st.session_state.lista_caps_titulos)} capítulos.")

# Mostrar lista para que el usuario confirme
if st.session_state.lista_caps_titulos:
    with st.expander("📋 Revisar lista de capítulos detectados", expanded=False):
        for idx, t in enumerate(st.session_state.lista_caps_titulos):
            st.text(f"{idx+1}. {t}")

    # PASO 2: GENERACIÓN
    btn_label = "🚀 2. Iniciar/Continuar Escritura" if not st.session_state.manuscrito_lista else "🔄 Continuar desde el corte"
    
    if st.button(btn_label):
        with st.status("Escribiendo manuscrito...", expanded=True) as status:
            total = len(st.session_state.lista_caps_titulos)
            
            for i, titulo in enumerate(st.session_state.lista_caps_titulos):
                if i < len(st.session_state.manuscrito_lista):
                    continue # Saltar ya escritos
                
                n_cap = i + 1
                st.write(f"✍️ Escribiendo {n_cap}/{total}: {titulo}")
                
                prompt_redaccion = f"""
                Escribe el capítulo {n_cap} de {total} del libro de {genre}.
                TÍTULO: '# Capítulo {n_cap}: {titulo}'.
                CONTEXTO: {st.session_state.esencia_cache}
                ESTILO: Académico, comillas españolas, profundidad filosófica. 2000 palabras.
                """
                
                texto = call_openrouter(prompt_redaccion, persistence["key"], selected_model_id)
                
                if "Error" not in texto:
                    st.session_state.manuscrito_lista.append(texto)
                else:
                    st.error(f"Error en capítulo {n_cap}. Detenido.")
                    break
            
            status.update(label="¡Manuscrito finalizado!", state="complete")

# --- DESCARGA ---
if st.session_state.manuscrito_lista:
    full_text = "\n\n---\n\n".join(st.session_state.manuscrito_lista)
    st.download_button("⬇️ Descargar Libro Completo", full_text, file_name="obra_completa.md")
    st.markdown(full_text)
