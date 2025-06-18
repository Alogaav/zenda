
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
            "country": "Colombia",
            "currency": "COP",
            "bank_name": "Banco de Bogotá",
            "balances": [2500000, 2200000, 1800000],
            "avg_income": 1500000,
            "anomalous_transactions": 1,
            "risk_country": False,
            "income_stability": 0.85,
            "account_age_months": 24
        },
        {
            "country": "México", 
            "currency": "MXN",
            "bank_name": "BBVA México",
            "balances": [45000, 42000, 38000],
            "avg_income": 28000,
            "anomalous_transactions": 0,
            "risk_country": False,
            "income_stability": 0.92,
            "account_age_months": 18
        },
        {
            "country": "Argentina",
            "currency": "ARS",
            "bank_name": "Banco Santander",
            "balances": [850000, 720000, 650000],
            "avg_income": 480000,
            "anomalous_transactions": 3,
            "risk_country": True,
            "income_stability": 0.65,
            "account_age_months": 12
        },
        {
            "country": "Brasil",
            "currency": "BRL",
            "bank_name": "Itaú Unibanco",
            "balances": [8500, 9200, 8800],
            "avg_income": 5500,
            "anomalous_transactions": 0,
            "risk_country": False,
            "income_stability": 0.88,
            "account_age_months": 36
        },
        {
            "country": "Perú",
            "currency": "PEN",
            "bank_name": "BCP",
            "balances": [12000, 11500, 10800],
            "avg_income": 3200,
            "anomalous_transactions": 2,
            "risk_country": False,
            "income_stability": 0.75,
            "account_age_months": 15
        }
    ]

def calculate_credit_score(data):
    """Calcula el score crediticio basado en múltiples factores"""
    score = 500  # Score base
    factors = []
    
    # Factor: Estabilidad de ingresos (0-200 puntos)
    income_stability_score = data["income_stability"] * 200
    score += income_stability_score
    factors.append({
        "factor": "Estabilidad de Ingresos",
        "impact": round(income_stability_score, 2),
        "positive": data["income_stability"] > 0.7
    })
    
    # Factor: Tendencia de saldos (±50 puntos)
    balance_trend = 30 if data["balances"][0] > data["balances"][-1] else -50
    score += balance_trend
    factors.append({
        "factor": "Tendencia de Saldos",
        "impact": balance_trend,
        "positive": balance_trend > 0
    })
    
    # Factor: Transacciones anómalas (±100 puntos)
    anomaly_score = max(-100, -data["anomalous_transactions"] * 30)
    score += anomaly_score
    factors.append({
        "factor": "Transacciones Sospechosas",
        "impact": anomaly_score,
        "positive": data["anomalous_transactions"] <= 1
    })
    
    # Factor: Riesgo país (±40 puntos)
    country_score = -40 if data["risk_country"] else 20
    score += country_score
    factors.append({
        "factor": "Riesgo País",
        "impact": country_score,
        "positive": not data["risk_country"]
    })
    
    # Factor: Capacidad de ahorro (±40 puntos)
    avg_balance = sum(data["balances"]) / len(data["balances"])
    if avg_balance > data["avg_income"] * 2:
        ratio_score = 40
    elif avg_balance > data["avg_income"]:
        ratio_score = 20
    else:
        ratio_score = -20
    score += ratio_score
    factors.append({
        "factor": "Capacidad de Ahorro",
        "impact": ratio_score,
        "positive": ratio_score > 0
    })
    
    # Factor: Antigüedad de cuenta (±30 puntos)
    age_score = min(30, data["account_age_months"] * 2)
    score += age_score
    factors.append({
        "factor": "Antigüedad de Cuenta",
        "impact": age_score,
        "positive": data["account_age_months"] >= 12
    })
    
    final_score = max(300, min(850, round(score)))
    approved = final_score >= 600 and data["anomalous_transactions"] <= 2
    
    # Calcular límite de crédito
    if approved:
        base_limit = (final_score - 500) * 2
        income_multiplier = min(data["avg_income"] * 0.3, 5000)  # Convertido a EUR aprox
        credit_limit = round(base_limit + income_multiplier)
    else:
        credit_limit = 0
    
    return {
        "approved": approved,
        "factors": factors,
        "recommendation": "APROBADO ✅" if approved else "RECHAZADO ❌",
        "confidence": round(85 + random.random() * 10, 1),
        "credit_limit": credit_limit
    }

def format_currency(amount, currency):
    """Formatea moneda según el país"""
    symbols = {
        "COP": "$",
        "MXN": "$", 
        "ARS": "$",
        "BRL": "R$",
        "PEN": "S/",
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
    ["🎲 Aleatorio"] + [f"{data['country']} ({data['currency']})" for data in get_sample_data()]
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
        if selected_country == "🎲 Aleatorio":
            user_data = random.choice(sample_data)
        else:
            country_name = selected_country.split(" (")[0]
            user_data = next(data for data in sample_data if data["country"] == country_name)
        
        st.success("✅ ¡Documentos procesados exitosamente!")
        
        # Mostrar datos extraídos
        st.markdown("#### 📊 Información Extraída:")
        
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("País", user_data["country"])
            st.metric("Banco", user_data["bank_name"])
        
        with info_col2:
            st.metric("Moneda", user_data["currency"])
            st.metric("Antigüedad Cuenta", f"{user_data['account_age_months']} meses")
        
        with info_col3:
            st.metric("Ingresos Promedio", format_currency(user_data["avg_income"], user_data["currency"]))
            st.metric("Transacciones Sospechosas", user_data["anomalous_transactions"])
        
        # Paso 2: Análisis de riesgo
        st.markdown("### 🎯 Paso 2: Análisis de Riesgo")
        
        with st.spinner("🧠 Calculando score crediticio..."):
            time.sleep(1.5)
        
        # Calcular score
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
        
        # Factores de decisión
        st.markdown("### 📋 Factores de Decisión")
        
        for factor in result["factors"]:
            icon = "✅" if factor["positive"] else "❌"
            color = "#28a745" if factor["positive"] else "#dc3545"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                        padding: 10px; margin: 5px 0; background-color: #f8f9fa; border-radius: 5px;">
                <span>{icon} {factor["factor"]}</span>
                <span style="color: {color}; font-weight: bold;">
                    {'+' if factor["impact"] > 0 else ''}{factor["impact"]:.0f} pts
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Alertas y warnings
        if data["anomalous_transactions"] > 2:
            st.markdown(f"""
            <div class="warning-box">
                <h4>⚠️ Alerta de Seguridad</h4>
                <p>Se detectaron <strong>{data["anomalous_transactions"]} transacciones anómalas</strong>. 
                Se requiere revisión manual adicional.</p>
            </div>
            """, unsafe_allow_html=True)
        
        if data["risk_country"]:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ País de Alto Riesgo</h4>
                <p>El país de origen está clasificado como de alto riesgo. Se aplicaron penalizaciones en el scoring.</p>
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
