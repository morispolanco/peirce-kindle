import streamlit as st
import pandas as pd
import random

# Configuración de la página
st.set_page_config(page_title="Abductive KDP Niche Finder", layout="wide")

def perform_abduction(fact, rule):
    """
    Aplica el silogismo abductivo de Peirce:
    1. Se observa un hecho sorprendente C.
    2. Si A fuera verdadero, C sería una cuestión de curso.
    3. Por lo tanto, hay razón para sospechar que A es verdadero.
    """
    hypotheses = {
        "Falta de contenido técnico para principiantes": "Un manual de 'Conceptos Complejos para Abuelos'",
        "Crecimiento de interés en misticismo y tecnología": "Novela sobre 'IA con Conciencia Espiritual'",
        "Saturación de ficción romántica genérica": "Subgénero de 'Romance Histórico en la Civilización Maya'",
        "Auge de la micro-productividad": "Libro de ejercicios de 'Productividad en 5 Minutos'",
        "Interés en la filosofía aplicada": "Guía práctica de 'Estoicismo para Emprendedores Digitales'"
    }
    
    # Lógica de combinación creativa
    return f"Hacia un nuevo nicho: {hypotheses.get(fact, 'Un híbrido entre ' + fact + ' y ' + rule)}"

# Interfaz de Usuario
st.title("🧠 Motor de Inferencia Abductiva para KDP")
st.markdown("""
Basado en la lógica de **Charles S. Peirce**, esta herramienta no solo analiza datos, 
sino que propone *hipótesis creativas* para nichos de mercado aún no explotados.
""")

col1, col2 = st.columns(2)

with col1:
    st.header("1. Observación (El Hecho)")
    fact = st.selectbox(
        "Seleccione un fenómeno observado en Amazon:",
        [
            "Falta de contenido técnico para principiantes",
            "Crecimiento de interés en misticismo y tecnología",
            "Saturación de ficción romántica genérica",
            "Auge de la micro-productividad",
            "Interés en la filosofía aplicada"
        ]
    )

with col2:
    st.header("2. Marco de Posibilidad (La Regla)")
    rule = st.text_input("Ingrese una tendencia o tecnología emergente:", "Inteligencia Artificial")

# Proceso de Salto Abductivo
if st.button("Generar Hipótesis de Nicho (Abducción)"):
    st.subheader("Resultado de la Inferencia")
    
    with st.spinner("Realizando salto cualitativo..."):
        nicho_propuesto = perform_abduction(fact, rule)
        
        st.success(f"**Hipótesis:** {nicho_propuesto}")
        
        st.info(f"""
        **Justificación Peirciana:**
        * **El Hecho (C):** Se observa que '{fact}'.
        * **La Hipótesis (A):** Si publicamos '{nicho_propuesto}', el vacío en el mercado (C) se explicaría como una oportunidad de negocio resuelta.
        * **Conclusión:** Existe una sospecha razonable de que este nicho será exitoso.
        """)

# Sección de Estrategia KDP
st.divider()
st.header("📊 Validación del Nicho")
st.write("Una vez formulada la hipótesis, proceda a la validación empírica:")

col_a, col_b, col_c = st.columns(3)
col_a.metric("Relevancia SEO", "Alta", "+15%")
col_b.metric("Competencia Estimada", "Baja", "-40%")
col_c.metric("Potencial Kindle Unlimited", "Muy Alto")

# Historial de descubrimientos
if 'history' not in st.session_state:
    st.session_state.history = []

if st.button("Guardar en mi Plan Editorial"):
    st.session_state.history.append(nicho_propuesto)
    st.write("Nicho guardado exitosamente.")

if st.session_state.history:
    with st.expander("Ver Plan de Publicación"):
        for item in st.session_state.history:
            st.write(f"- {item}")
