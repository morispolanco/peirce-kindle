import streamlit as st
import requests
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
# Debe ser la primera instrucción de Streamlit
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
            {"role": "system", "content": "Eres un editor y escritor profesional. Tu prosa es académica, sobria y precisa. Usas comillas españolas (« ») y respetas la gramática de la RAE."},
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
    Resume: 
    1. Público objetivo. 
    2. Tono y diferenciación. 
    3. Puntos clave que el autor no debe olvidar.
    
    PLAN EDITORIAL:
    {plan_completo}
    
    Responde solo con la síntesis técnica para guiar la escritura.
    """
    return call_openrouter(prompt, api_key, model_id)

## --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    # Diccionario corregido con comas y IDs actuales
    model_options = {
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "Gemini 1.5 Pro": "google/gemini-pro-1.5",
        "GPT-4o": "openai/gpt-4o",
        "Llama 3.1 405B": "meta-llama/llama-3.1-405b-instruct",
        "DeepSeek V3": "deepseek/deepseek-chat",
        "Mistral Large 2": "mistralai/mistral-large-2407",
        "Qwen 2.5 72B": "qwen/qwen-2.5-72b-instruct"
    }
    
    selected_name = st.selectbox("Cerebro del Escritor", list(model_options.keys()))
    selected_model_id = model_options[selected_name]
    genre = st.text_input("Género (KDP)", value="Ensayo / Thriller")

## --- FLUJO PRINCIPAL ---

st.title("🖋️ Escritura Basada en Plan Editorial Complejo")
st.info("Pega tu plan editorial completo. El sistema extraerá la estrategia, el público y la estructura automáticamente.")

plan_input = st.text_area("Cargar Plan Editorial Completo:", height=300)

if "manuscrito" not in st.session_state:
    st.session_state.manuscrito = ""
if "esencia" not in st.session_state:
    st.session_state.esencia = ""

if st.button("🚀 Procesar Plan e Iniciar Redacción"):
    if not api_key or not plan_input:
        st.error("Se requiere la API Key y el contenido del plan.")
    else:
        with st.status("Analizando estrategia editorial...", expanded=True) as status:
            # 1. Extraer esencia
            esencia = extraer_esencia_editorial(plan_input, api_key, selected_model_id)
            st.session_state.esencia = esencia
            st.write("**Estrategia extraída con éxito.**")
            
            # 2. Extraer capítulos
            prompt_caps = f"Basado en el plan, lista solo los títulos de capítulos a escribir (uno por línea, sin números).\n\nPLAN:\n{plan_input}"
            lista_caps_raw = call_openrouter(prompt_caps, api_key, selected_model_id)
            lista_caps = [c.strip() for c in lista_caps_raw.split('\n') if len(c.strip()) > 5]
            
            capitulos_finales = []
            contexto_acumulado = ""

            # 3. Escritura secuencial
            for i, titulo in enumerate(lista_caps):
                n_cap = i + 1
                st.write(f"✍️ Redactando Capítulo {n_cap}: {titulo}...")
                
                prompt_redaccion = f"""
                Escribe el texto completo del capítulo.
                ESTRATEGIA: {st.session_state.esencia}
                TEMA: {titulo}
                CONTEXTO PREVIO: {contexto_acumulado[-1500:]}
                
                REQUISITOS:
                1. 2000-2200 palabras (desarrollo profundo).
                2. Título: '# Capítulo {n_cap}: {titulo.capitalize()}'.
                3. Solo mayúscula inicial en títulos y subtítulos.
                4. Comillas españolas (« ») obligatorias.
                5. Incluye contraargumentación y respuesta sólida.
                6. Estilo sobrio, sin exceso de adjetivos.
                7. Markdown puro, sin comentarios de IA.
                """
                
                cap_texto = call_openrouter(prompt_redaccion, api_key, selected_model_id)
                capitulos_finales.append(cap_texto)
                contexto_acumulado += f"\nCapítulo {n_cap}: {titulo} finalizado."
                
            st.session_state.manuscrito = "\n\n---\n\n".join(capitulos_finales)
            status.update(label="¡Libro Completo!", state="complete", expanded=False)

## --- EXPORTACIÓN ---
if st.session_state.manuscrito:
    st.divider()
    st.download_button(
        "⬇️ Descargar Manuscrito (.md)",
        st.session_state.manuscrito,
        file_name="manuscrito_final.md",
        mime="text/markdown"
    )
    with st.expander("Ver Análisis de Estrategia"):
        st.write(st.session_state.esencia)
    st.markdown(st.session_state.manuscrito)
