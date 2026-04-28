import streamlit as st
import requests
import json

# --- Configuración de la interfaz ---
st.set_page_config(page_title="KDP Abductive Engine 2026", page_icon="🧬", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2e4053; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- Diccionario de Modelos (Actualizado 2026) ---
MODELS = {
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

# --- Barra Lateral ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    model_name = st.selectbox("Cerebro Lógico (LLM):", list(MODELS.keys()))
    selected_model = MODELS[model_name]
    
    st.divider()
    st.write("**Lógica de Peirce:**")
    st.caption("La abducción no es adivinanza; es la construcción de una hipótesis basada en una anomalía detectada en el caos del mercado.")

# --- Lógica de API ---
def call_abduction_api(keyword, key, model):
    prompt = f"""
    Eres un analista de mercado experto en Amazon KDP y un lógico peirciano.
    Tu objetivo es encontrar un nicho de mercado para la palabra clave: "{keyword}".
    
    Aplica rigurosamente el proceso abductivo:
    1. Identifica un 'Hecho Sorprendente' (C) en Amazon relacionado con "{keyword}" (ej. un desajuste entre intención de búsqueda y calidad de oferta).
    2. Formula la 'Hipótesis' (A) que, de ser cierta, explicaría ese desajuste y se convertiría en un nicho rentable.
    3. Justifica por qué 'A' es una explicación plausible y necesaria.
    
    Salida esperada:
    - Título del Nicho Hipotético.
    - Descripción de la Anomalía detectada.
    - Estrategia Editorial (Ángulo de ataque).
    - Sugerencia de 2 títulos potenciales.
    """
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error en la comunicación: {str(e)}"

# --- Cuerpo Principal ---
st.title("🧬 Motor de Abducción KDP")
st.markdown("### De la Palabra Clave a la Hipótesis de Mercado")

target_keyword = st.text_input("Ingresa una sola palabra clave o concepto:", placeholder="Ej: Estoicismo, Ciberseguridad, Jardinería Zen...")

if st.button("Iniciar Proceso de Inferencia"):
    if not api_key:
        st.error("Por favor, introduce tu API Key.")
    elif not target_keyword:
        st.warning("Escribe una palabra clave para comenzar.")
    else:
        with st.spinner(f"El modelo {model_name} está detectando anomalías..."):
            resultado = call_abduction_api(target_keyword, api_key, selected_model)
            
            st.success("Salto Abductivo Completado")
            st.markdown("---")
            st.markdown(resultado)

# --- Documentación Educativa ---
with st.expander("¿Cómo funciona el silogismo abductivo aquí?"):
    st.write("""
    1. **Observación (C):** Se observa un hecho sorprendente $C$ en los datos de Amazon.
    2. **Hipótesis (A):** Si la hipótesis $A$ fuera verdadera, $C$ sería una cuestión de curso.
    3. **Conclusión:** Por lo tanto, hay razón para sospechar que $A$ es verdadera.
    
    La IA analiza los patrones de consumo asociados a tu palabra clave para proponer esa $A$ que falta.
    """)
