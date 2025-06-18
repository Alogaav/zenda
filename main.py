
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random
from PIL import Image
import io
import base64
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Cargar dataset simulado
df = pd.read_excel("customer_records.xlsx")
df_filtrado = df[["Edad","Antigüedad","Balance","ProductosContratados","BalancePromedio","CreditoOtorgado"]]
scaler = StandardScaler()

X = df_filtrado[["Edad","Antigüedad","Balance","ProductosContratados","BalancePromedio"]]
scaler.fit(X)
X = scaler.transform(X)
y = df_filtrado["CreditoOtorgado"]

# Separamos el set de datos para entrenar y probar los modelos
X_train, X_test = X[:1500], X[5000:]
y_train, y_test = y[:1500], y[5000:]


random_forest = RandomForestClassifier(n_estimators=100).fit(X_train, y_train)
# Configuración de la página
st.set_page_config(
    page_title="Zenda PoC - Sistema de Scoring Crediticio Alternativo",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: linear-gradient(145deg, #f0f2f6, #ffffff);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Datos simulados
@st.cache_data
def get_sample_data():
    return [
        {
            "country": "Cualquiera", 
            "currency": "EUR",
            "bank_name": "BBVA",
            "balance": 38000,
            "balance_promedio": 28000,
            "anomalous_transactions": 0,
            "risk_country": False,
            "income_stability": 0.92,
            "account_age_months": 18
        }
    ]

def calculate_credit_score(data):
    # "Edad","Antigüedad","Balance","ProductosContratados","BalancePromedio"
    y_pred = random_forest.predict([
        data["edad"],
        data["antiguedad"],
        data["balance"],
        data["productos"],
        data["balance_promedio"]
    ])
    
    approved = y_pred
    return {
        "approved": approved,
        "factors": "",
        "recommendation": "APROBADO ✅" if approved else "RECHAZADO ❌",
        "confidence": round(85 + random.random() * 10, 1),
        "credit_limit": 2000
    }

def format_currency(amount, currency):
    """Formatea moneda según el país"""
    symbols = {
        "EUR": "€"
    }
    symbol = symbols.get(currency, "$")
    return f"{symbol} {amount:,.0f}"



# Header principal
st.markdown("""
<div class="main-header">
    <h1>🏦 Zenda PoC</h1>
    <h3>Sistema de Scoring Crediticio Alternativo para Extranjeros</h3>
    <p>Neobanco digital para expatriados, estudiantes internacionales y extranjeros en España</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("## ⚙️ Solicitar Crédito")

# Selector de país para simular
selected_country = st.sidebar.selectbox(
    "Simular usuario de:",
    [f"{data['country']} ({data['currency']})" for data in get_sample_data()]
)
edad = st.sidebar.text_input(
    "Edad:"
)
antiguedad = st.sidebar.text_input(
    "Antigüedad:"
)
balance = st.sidebar.text_input(
    "Balance:"
)
productos = st.sidebar.text_input(
    "Productos contratados:"
)
promedio = st.sidebar.text_input(
    "Balance promedio:"
)


# Botón principal para iniciar simulación
if st.sidebar.button("🚀 Iniciar Simulación", type="primary", use_container_width=True):
    st.session_state.start_simulation = True

# Layout principal
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("## 📄 Simulación de Onboarding")
    
    if not hasattr(st.session_state, 'start_simulation'):
        st.info("👆 Haz clic en 'Iniciar Simulación' en el sidebar para comenzar")
        st.markdown("""
        ### 🎯 ¿Qué hace este sistema?
        
        **Zenda** resuelve el problema de acceso al sistema financiero español para extranjeros:
        
        - ✅ **Sin NIE requerido**: Solo necesitas tu pasaporte
        - ✅ **Sin historial crediticio español**: Analizamos tus extractos del país de origen
        - ✅ **Decisión instantánea**: Algoritmo de ML en tiempo real
        - ✅ **100% digital**: Todo el proceso online
        
        ### 🔄 Flujo del Sistema:
        1. **Subida de documentos** (Pasaporte + Extractos bancarios)
        2. **Document AI** extrae y estructura la información
        3. **Motor de riesgo** analiza múltiples factores
        4. **Decisión automática** de aprobación/rechazo
        """)

if hasattr(st.session_state, 'start_simulation') and st.session_state.start_simulation:
    
    with col1:
        # Paso 1: Selección/generación de datos
        st.markdown("### 📋 Paso 1: Procesamiento de Documentos")
        
        with st.spinner("🔍 Analizando documentos con Document AI..."):
            time.sleep(2)
        
        # Seleccionar datos según la opción del usuario
        sample_data = get_sample_data()
        country_name = selected_country.split(" (")[0]
        user_data = next(data for data in sample_data if data["country"] == country_name)
        user_data["edad"] = edad
        user_data["antiguedad"] = antiguedad
        user_data["balance"] = float(balance)
        user_data["productos"] = productos
        user_data["balance_promedio"] = float(promedio)
        
        st.success("✅ ¡Documentos procesados exitosamente!")
        
        # Mostrar datos extraídos
        st.markdown("#### 📊 Información Extraída:")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("Moneda", user_data["currency"])
            st.metric("Edad", user_data["edad"])
        
        with info_col2:
            st.metric("Productos Contratados", user_data["productos"])
            st.metric("Antigüedad Cuenta", f"{user_data['antiguedad']} meses")
        
        with info_col3:
            st.metric("Balance actual", format_currency(user_data["balance"], user_data["currency"]))
            st.metric("Balance promedio", format_currency(user_data["balance_promedio"], user_data["currency"]))
        
        
        with st.spinner("🧠 Calculando score crediticio..."):
            time.sleep(1.5)

        scoring_result = calculate_credit_score(user_data)
        
        st.session_state.scoring_result = scoring_result
        
        st.session_state.user_data = user_data

with col2:
    st.markdown("## 🎯 Análisis de Riesgo Crediticio")
    
    if hasattr(st.session_state, 'scoring_result'):
        result = st.session_state.scoring_result
        data = st.session_state.user_data
        
        # Resultado principal
        if result["approved"]:
            st.markdown(f"""
            <div class="success-box">
                <h2 style="margin: 0; text-align: center;">✅ {result["recommendation"]}</h2>
                <p style="text-align: center; margin: 10px 0;">Confianza: {result["confidence"]}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="danger-box">
                <h2 style="margin: 0; text-align: center;">❌ {result["recommendation"]}</h2>
                <p style="text-align: center; margin: 10px 0;">Confianza: {result["confidence"]}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Límite de crédito
        if result["approved"]:
            st.markdown(f"""
            <div class="success-box">
                <h3 style="text-align: center; margin: 0;">💳 Límite de Crédito Propuesto</h3>
                <h2 style="text-align: center; margin: 10px 0; color: #28a745;">€{result["credit_limit"]:,}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("👈 Los resultados del análisis aparecerán aquí una vez iniciada la simulación")
        
        st.markdown("""
        ### 🎯 Factores que Analizamos:
        
        - **📈 Estabilidad de Ingresos**: Consistencia en los ingresos mensuales
        - **💰 Tendencia de Saldos**: Si los saldos aumentan o disminuyen
        - **🚨 Transacciones Sospechosas**: Actividad inusual o fraudulenta
        - **🌍 Riesgo País**: Estabilidad económica del país de origen
        - **💳 Capacidad de Ahorro**: Relación entre ingresos y saldos
        - **⏰ Antigüedad de Cuenta**: Tiempo de relación bancaria
        
        ### 🎲 Criterios de Aprobación:
        - **Score mínimo**: 600 puntos
        - **Transacciones sospechosas**: Máximo 2
        - **Documentos**: Válidos y recientes
        """)

# Footer con información del proyecto
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p><strong>Zenda PoC</strong> - Sistema de Scoring Crediticio Alternativo</p>
    <p>Máster en Fintech, Blockchain y Mercados Financieros - Universidad de Barcelona</p>
    <p>Desarrollado por: Alondra García Ávila, Lucía Santandreu y Camila Díaz Lafourcade</p>
</div>
""", unsafe_allow_html=True)

# Botón para reiniciar
if hasattr(st.session_state, 'start_simulation'):
    if st.button("🔄 Nueva Simulación", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
