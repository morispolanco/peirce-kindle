import streamlit as st
import requests
import json

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Inferencia Abductiva KDP",
    page_icon="🧠",
    layout="centered"
)

# --- Estilos CSS Personalizados ---
st.markdown("""
    <style>
    .stAlert { border-left: 5px solid #6c5ce7; }
    .main { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# --- Barra Lateral: Configuración de API ---
with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("OpenRouter API Key", type="password", help="Obtén tu clave en openrouter.ai")
    
    model_choice = st.selectbox(
        "Selecciona el Modelo",
        options=[
            "google/gemini-pro-1.5",
            "anthropic/claude-3-haiku",
            "openai/gpt-4o-mini",
            "mistralai/mistral-7b-instruct"
        ],
        index=0
    )
    
    st.divider()
    st.info("**Lógica Abductiva:** Este sistema no solo analiza datos; genera 'hipótesis de sospecha' sobre nichos que aún no existen basándose en anomalías del mercado.")

# --- Lógica de Comunicación con OpenRouter ---
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
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- Interfaz Principal ---
st.title("🧠 KDP Niche Abductor")
st.subheader("Buscador de Nichos mediante Lógica de Peirce")

st.markdown("""
Introduce un **Hecho Sorprendente** (una observación inusual del mercado Amazon) 
y deja que la IA realice el **Salto Abductivo** hacia un nuevo nicho.
""")

with st.container():
    # Paso 1: El Hecho (C)
    observacion = st.text_area(
        "Observación (El Hecho C):", 
        placeholder="Ej: Hay muchas búsquedas de 'dieta keto' para perros, pero los libros existentes solo tienen 2 estrellas y portadas de baja calidad."
    )

    # Paso 2: Conocimiento de Fondo (Contexto)
    contexto = st.text_input(
        "Contexto de Mercado (Opcional):",
        placeholder="Ej: Tendencia creciente en humanización de mascotas y nutrición premium."
    )

if st.button("Realizar Salto Abductivo"):
    if not api_key:
        st.warning("Por favor, ingresa tu API Key de OpenRouter.")
    elif not observacion:
        st.warning("Debes describir un hecho observado en el mercado.")
    else:
        # Definición del Prompt basado en el silogismo de Peirce
        prompt_abductivo = f"""
        Actúa como un analista experto en Amazon KDP y filósofo pragmatista siguiendo la lógica de Charles Sanders Peirce.
        
        Silogismo Abductivo:
        1. Se observa un hecho sorprendente 'C': {observacion}.
        2. Pero si la hipótesis 'A' fuera verdadera, 'C' sería una cuestión de curso (explicable).
        3. Por lo tanto, hay razón para sospechar que 'A' es verdadera.
        
        Contexto adicional: {contexto}
        
        Tarea:
        - Analiza el hecho 'C'.
        - Propón la Hipótesis 'A' (Un nicho de mercado específico, innovador y sub-atendido).
        - Describe el ángulo editorial único (USP).
        - Sugiere 3 títulos potenciales para Kindle.
        - Estructura tu respuesta con secciones claras: 'La Anomalía', 'El Salto Abductivo (Nicho Hipotético)' y 'Estrategia de Ejecución'.
        """
        
        with st.spinner("Procesando inferencia..."):
            resultado = call_openrouter(prompt_abductivo, api_key, model_choice)
            st.markdown("---")
            st.markdown(resultado)

# --- Pie de página informativo ---
st.divider()
st.caption("Implementado bajo los principios de la Racionalidad Inventiva.")
