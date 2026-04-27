import streamlit as st
import pandas as pd
import requests
import json

# Configuración de página
st.set_page_config(page_title="Generador Editorial Abductivo", layout="wide")

# Estilos personalizados (Minimalismo y sofisticación)
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1a1a1a; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: Configuración de API y Modelos ---
with st.sidebar:
    st.title("Configuración de IA")
    api_key = st.text_input("OpenRouter API Key", type="password")
    if api_key:
        st.session_state['openrouter_api_key'] = api_key
    
    model_option = st.selectbox(
        "Selecciona el Modelo",
        [
            "google/gemini-2.0-flash-001",
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o-mini",
            "meta-llama/llama-3.1-405b"
        ],
        index=0
    )

st.title("🏛️ Planificador Editorial: Lógica Abductiva")
st.markdown("Genera planes para KDP (40k-50k palabras) basados en inferencia hipotética y datos de mercado.")

# --- ENTRADA DE DATOS ---
col1, col2 = st.columns(2)

with col1:
    keyword = st.text_input("Keyword Principal (Ej: 'Filosofía Estoica', 'AI en Finanzas')")
    pais = st.text_input("País de Publicación (Ej: España, México, USA)")

with col2:
    uploaded_file = st.file_uploader("Cargar Informe de Ventas (CSV o Excel)", type=['csv', 'xlsx'])

# --- LÓGICA DE PROCESAMIENTO ---
def llamar_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {st.session_state.get('openrouter_api_key', '')}",
        "HTTP-Referer": "http://localhost:8501",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_option,
        "messages": [
            {
                "role": "system", 
                "content": (
                    "Eres un consultor editorial experto en KDP que utiliza la lógica abductiva de Charles Sanders Peirce. "
                    "Tu objetivo es realizar una 'Hipótesis Explicativa' basada en datos. "
                    "El plan debe estructurarse para libros de no ficción de 40,000 a 50,000 palabras, con 20 a 25 capítulos."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.text}"

if st.button("Generar Plan Editorial"):
    if not api_key:
        st.error("Por favor, ingresa tu API Key en la barra lateral.")
    elif not keyword or not pais:
        st.warning("Faltan datos (Keyword o País).")
    else:
        with st.spinner("Aplicando lógica abductiva a los datos..."):
            # Procesar informe si existe
            contexto_ventas = "No se proporcionó informe de ventas previo."
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('csv') else pd.read_excel(uploaded_file)
                    contexto_ventas = df.to_string(index=False)[:2000] # Limitar contexto
                except Exception as e:
                    st.error(f"Error al leer el archivo: {e}")

            # Construcción del Prompt Peirceano
            prompt_final = f"""
            APLICA EL MÉTODO DEL INGENIUM Y LA ABDUCCIÓN DE PEIRCE:
            
            1. HECHOS (Datos):
            - Keyword: {keyword}
            - País: {pais}
            - Contexto de Ventas/Tendencias: {contexto_ventas}
            
            2. TAREA:
            Genera una 'Hipótesis de Éxito' (Plan Editorial) que explique cómo capturar este mercado. 
            El plan debe incluir:
            - Título Sugestivo y Subtítulo SEO-optimizado.
            - Síntesis Argumentativa (basada en el insight abductivo).
            - Tabla de Contenidos Detallada: Exactamente de 20 a 25 capítulos diseñados para alcanzar un volumen de 40k-50k palabras.
            
            Presenta el resultado con un tono profesional, elegante y estratégico.
            """
            
            resultado = llamar_openrouter(prompt_final)
            st.markdown("---")
            st.markdown(resultado)