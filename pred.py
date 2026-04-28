import streamlit as st
import requests
import json

# --- Configuración de página ---
st.set_page_config(page_title="KDP Book Creator Pro", page_icon="📚", layout="wide")

# --- Modelos Disponibles ---
MODELS = {
    "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
    "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
    "Gemini 3 Flash Preview": "google/gemini-3-flash-preview",
    "Qwen 3.5 Plus (2026)": "qwen/qwen3.5-plus-20260420",
    "Llama 3.1 405B": "meta-llama/llama-3.1-405b",
    "GPT-4o Mini": "openai/gpt-4o-mini"
}

# --- Funciones de API ---
def call_openrouter(prompt, key, model):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]})
        )
        return response.json()['choices'][0]['message']['content']
    except:
        return "Error en la conexión con la API."

# --- Interfaz Lateral ---
with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password")
    model_choice = st.selectbox("Modelo", list(MODELS.keys()))
    selected_model = MODELS[model_choice]
    st.divider()
    st.info("Este sistema genera libros completos siguiendo la lógica de Peirce y estándares editoriales estrictos.")

# --- Flujo de Aplicación ---
st.title("📚 Escritor Editorial Abductivo 2026")

# PASO 1: PREDICCIÓN DE TENDENCIAS
st.header("1. Predicción de Tendencias")
c1, c2 = st.columns(2)
with c1: mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
with c2: anio = st.selectbox("Año", [2026, 2027, 2028])

if st.button("🔍 Predecir Futuros Nichos"):
    prompt_trends = f"Actúa como analista de tendencias. Lista 5 tendencias de nicho para KDP en {mes} de {anio}. Explica por qué son relevantes."
    trends = call_openrouter(prompt_trends, api_key, selected_model)
    st.session_state['trends'] = trends

if 'trends' in st.session_state:
    st.markdown(st.session_state['trends'])
    
    # PASO 2: SELECCIÓN Y ABDUCCIÓN
    st.header("2. Elección y Análisis Abductivo")
    tendencia_user = st.text_input("Escribe o pega la tendencia elegida:")
    
    if st.button("🧠 Generar Plan Editorial de 20 Capítulos"):
        prompt_plan = f"""
        Realiza un análisis abductivo de Peirce para la tendencia '{tendencia_user}'. 
        Detecta la anomalía (Hecho sorprendente C) y propón la hipótesis (A).
        Luego, crea un plan editorial de 20 capítulos. 
        Reglas: Títulos con mayúscula inicial solo en la primera palabra y nombres propios.
        Incluye Título, Subtítulo y Síntesis.
        """
        plan = call_openrouter(prompt_plan, api_key, selected_model)
        st.session_state['plan'] = plan
        st.session_state['ready_to_write'] = True

if 'plan' in st.session_state:
    st.divider()
    st.markdown(st.session_state['plan'])

    # PASO 3: ESCRITURA CAPÍTULO A CAPÍTULO
    if st.session_state.get('ready_to_write'):
        st.header("3. Escritura del Libro")
        if st.button("✍️ Iniciar Redacción del Libro Completo"):
            full_book = ""
            progress_bar = st.progress(0)
            
            # Simulamos el bucle para los 20 capítulos
            for i in range(1, 21):
                st.write(f"Redactando Capítulo {i}...")
                prompt_cap = f"""
                Escribe el Capítulo {i} del libro basado en el siguiente plan: {st.session_state['plan']}.
                CONVENCIONES:
                - Extensión: Aproximadamente 2000 palabras.
                - Formato: Empezar con '# Capítulo {i}: [título del capítulo]'.
                - Títulos: Mayúscula inicial solo en la primera palabra.
                - Puntuación: Usa comillas españolas (« »).
                - Estilo: Profesional, profundo y sin comentarios de IA.
                """
                cap_content = call_openrouter(prompt_cap, api_key, selected_model)
                full_book += cap_content + "\n\n"
                progress_bar.progress(i / 20)
            
            st.session_state['full_book_md'] = full_book
            st.success("¡Libro completado!")

# PASO 4: EXPORTACIÓN
if 'full_book_md' in st.session_state:
    st.header("4. Compilación Final")
    st.text_area("Previsualización de Markdown", st.session_state['full_book_md'][:1000] + "...", height=300)
    
    st.download_button(
        label="📥 Descargar Libro Completo (Markdown)",
        data=st.session_state['full_book_md'],
        file_name="libro_kdp_completo.md",
        mime="text/markdown"
    )
