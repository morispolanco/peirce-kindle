import streamlit as st
import requests
import json

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Abductor de Nichos KDP",
    page_icon="🔍",
    layout="wide"
)

# --- Estilos Personalizados ---
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 1.1rem; }
    .reportview-container { background: #fdfdfd; }
    </style>
""", unsafe_allow_html=True)

# --- Barra Lateral: Configuración ---
with st.sidebar:
    st.title("⚙️ Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    model_choice = st.selectbox(
        "Cerebro Lógico",
        options=[
            "google/gemini-pro-1.5",
            "anthropic/claude-3-sonnet",
            "openai/gpt-4o",
            "meta-llama/llama-3-70b-instruct"
        ],
        index=0
    )
    
    st.divider()
    st.markdown("""
    **La Lógica de la Invención:**
    Según Peirce, la abducción es la única operación lógica que introduce una **idea nueva**. 
    Aquí, la IA 'observa' el mercado por ti para encontrar lo que otros pasan por alto.
    """)

# --- Función de Comunicación ---
def call_openrouter(prompt, key, model):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model,
                "messages": [{"role": "system", "content": "Eres un experto en lógica peirciana y análisis de mercados en Amazon KDP."},
                             {"role": "user", "content": prompt}]
            })
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# --- Interfaz Principal ---
st.title("💡 Generador de Hipótesis KDP")
st.markdown("### De la Palabra Clave al Hecho Sorprendente")

# Entrada del usuario
keyword = st.text_input("Ingresa una palabra clave o tema general:", placeholder="Ej: Inteligencia Artificial, Jardinería, Cripto...")

if st.button("Realizar Inferencia Completa"):
    if not api_key:
        st.error("Se requiere la API Key de OpenRouter.")
    elif not keyword:
        st.warning("Por favor, introduce un tema de interés.")
    else:
        # Prompt diseñado para forzar la estructura de Peirce
        prompt_completo = f"""
        Analiza el nicho de mercado en Amazon KDP para la palabra clave: "{keyword}".
        
        Sigue estrictamente este proceso de razonamiento abductivo de Charles Sanders Peirce:
        
        1. **EL HECHO SORPRENDENTE (C):** Imagina y describe una anomalía o fenómeno inusual en los datos actuales de Amazon para esta palabra clave. (Ej: 'Existe un alto volumen de búsqueda para X, pero los libros que aparecen son todos traducciones mediocres de otros idiomas' o 'La gente busca X mezclado con Y, pero no hay ningún libro que combine ambos').
        
        2. **LA HIPÓTESIS EXPLICATIVA (A):** Si la hipótesis 'A' fuera verdadera (un nuevo tipo de libro o nicho específico), entonces el hecho 'C' sería algo natural y esperado. Define esta hipótesis con precisión.
        
        3. **EL SALTO CUALITATIVO:** Explica por qué esta idea es una innovación y no solo una copia de lo que ya existe.
        
        4. **PRODUCTO RESULTANTE:**
           - Título sugerido impactante.
           - Subtítulo optimizado para SEO.
           - 3 Puntos clave de diferenciación (USP).
           - Público objetivo específico.

        Presenta la respuesta con un tono profesional, analítico y creativo.
        """
        
        with st.spinner(f"Analizando '{keyword}' bajo la lente de Peirce..."):
            resultado = call_openrouter(prompt_completo, api_key, model_choice)
            
            # Mostrar resultados en un diseño limpio
            st.divider()
            st.markdown(resultado)
            
            # Metadatos de la consulta
            st.caption(f"Inferencia realizada con el modelo: {model_choice}")

# --- Footer ---
st.divider()
st.info("Nota: La abducción no garantiza el éxito, sino que señala una dirección probable para la experimentación creativa.")
