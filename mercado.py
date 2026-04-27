import streamlit as st
import requests
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Escritor Editorial Pro: Market Intelligence", page_icon="📚", layout="wide")

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
            {"role": "system", "content": "Eres un experto en inteligencia de mercado editorial y autor de best-sellers. Usas comillas españolas (« ») y prosa académica profunda. Tu precisión en datos de tendencias de Amazon es absoluta."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4 
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
if "analisis_mercado" not in st.session_state:
    st.session_state.analisis_mercado = ""

## --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key_input = st.text_input("OpenRouter API Key", type="password", value=persistence["key"])
    if api_key_input: persistence["key"] = api_key_input

    model_options = {
        "Claude 4.5 Sonnet": "anthropic/claude-sonnet-4.5",
        "GPT-5.5 (OpenAI)": "openai/gpt-5.5",
        "Llama 3.1 405B": "meta-llama/llama-3.1-405b",
        "GPT-4o Mini": "openai/gpt-4o-mini",
        "Gemini 3 Flash": "google/gemini-3-flash-preview"
    }
    selected_model_id = model_options[st.selectbox("Modelo", list(model_options.keys()))]
    
    st.divider()
    genre = st.selectbox("Nicho de Mercado", ["Ensayo Filosófico", "Derecho", "Historia", "Sociología", "Economía Política", "Ciencia"])
    target_audience = st.text_input("Público Objetivo", placeholder="Ej: Académicos, Estudiantes de postgrado...")

    if st.button("🗑️ Resetear Todo"):
        st.session_state.clear()
        st.rerun()

## --- FLUJO PRINCIPAL ---
st.title("🖋️ Ingeniería Editorial basada en Tendencias de Amazon")
st.markdown("---")

# PASO 0: ANÁLISIS DE MERCADO Y GENERACIÓN DE TÍTULO
st.subheader("📊 Fase 1: Análisis de Tendencias y Oportunidad")
market_query = st.text_input("Describe el tema general o área de interés:", placeholder="Ej: El impacto de la IA en la ética jurídica contemporánea")

if st.button("🔎 Analizar Mercado y Proponer Estructura"):
    if not market_query:
        st.warning("Por favor, introduce un tema de interés.")
    else:
        with st.spinner("Analizando algoritmos de Amazon y tendencias de búsqueda..."):
            # Prompt de análisis de mercado
            prompt_mercado = f"""
            Actúa como un analista de datos de Amazon KDP y experto editorial. 
            TEMA: {market_query}
            NICHO: {genre}
            AUDIENCIA: {target_audience}

            TAREA:
            1. Analiza las tendencias actuales de ventas (2024-2026) en este nicho.
            2. Identifica el «gap» o vacío de contenido en los libros actuales.
            3. Propón el TÍTULO con mayor potencial de éxito comercial (gancho + autoridad).
            4. Genera una ESTRUCTURA DETALLADA de capítulos optimizada para SEO y retención del lector.
            
            FORMATO DE SALIDA:
            - TÍTULO PROPUESTO: [Título]
            - JUSTIFICACIÓN DE MERCADO: [Breve análisis de por qué este título venderá]
            - ESTRUCTURA DE CAPÍTULOS: Uno por línea, precedido por el número.
            """
            st.session_state.analisis_mercado = call_openrouter(prompt_mercado, persistence["key"], selected_model_id)
            
            # Extraer capítulos automáticamente del análisis
            prompt_caps = f"""
            De este análisis de mercado, extrae exclusivamente los títulos de los capítulos propuestos. 
            No añadas introducciones, solo el listado de capítulos.
            ANÁLISIS: {st.session_state.analisis_mercado}
            """
            raw_titles = call_openrouter(prompt_caps, persistence["key"], selected_model_id)
            st.session_state.lista_caps_titulos = [t.strip() for t in raw_titles.split('\n') if len(t.strip()) > 3]
            st.session_state.esencia_cache = st.session_state.analisis_mercado # El análisis sirve de contexto

if st.session_state.analisis_mercado:
    st.info("💡 **Análisis de Oportunidad Generado**")
    st.markdown(st.session_state.analisis_mercado)

# PASO 2: GENERACIÓN DE CONTENIDO
if st.session_state.lista_caps_titulos:
    st.markdown("---")
    st.subheader(f"🚀 Fase 2: Redacción de la Obra ({len(st.session_state.lista_caps_titulos)} Capítulos)")
    
    with st.expander("📋 Ver Estructura Programada"):
        for idx, t in enumerate(st.session_state.lista_caps_titulos):
            st.text(f"{idx+1}. {t}")

    btn_label = "🚀 Iniciar Escritura del Best-Seller" if not st.session_state.manuscrito_lista else "🔄 Continuar Generación"
    
    if st.button(btn_label):
        with st.status("Escribiendo manuscrito de alta precisión...", expanded=True) as status:
            total = len(st.session_state.lista_caps_titulos)
            
            for i, titulo in enumerate(st.session_state.lista_caps_titulos):
                if i < len(st.session_state.manuscrito_lista):
                    continue
                
                n_cap = i + 1
                st.write(f"✍️ Redactando {n_cap}/{total}: **{titulo}**")
                
                prompt_redaccion = f"""
                Eres un autor de élite. Escribe el capítulo {n_cap} de {total}.
                TÍTULO: '# {titulo}'.
                BASADO EN EL ANÁLISIS DE MERCADO: {st.session_state.esencia_cache}
                ESTILO: Académico, profundo, uso de «comillas españolas», lenguaje preciso.
                LONGITUD: Extensa y detallada (mínimo 2000 palabras).
                OBJETIVO: Convertir este capítulo en el referente definitivo sobre el tema.
                """
                
                texto = call_openrouter(prompt_redaccion, persistence["key"], selected_model_id)
                
                if "Error" not in texto:
                    st.session_state.manuscrito_lista.append(texto)
                else:
                    st.error(f"Error en capítulo {n_cap}. Proceso pausado.")
                    break
            
            status.update(label="¡Obra completada con éxito!", state="complete")

# --- ÁREA DE DESCARGA ---
if st.session_state.manuscrito_lista:
    st.divider()
    full_text = "\n\n---\n\n".join(st.session_state.manuscrito_lista)
    st.download_button("⬇️ Descargar Manuscrito Final (.md)", full_text, file_name="best_seller_proyectado.md")
    with st.expander("📖 Previsualizar Obra"):
        st.markdown(full_text)
