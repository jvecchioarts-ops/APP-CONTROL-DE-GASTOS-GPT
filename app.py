import streamlit as st
from core.db import init_db
from core.auth import verificar_licencia, activar_licencia_local
from core.bcv import obtener_tasa_bcv

st.set_page_config(
    page_title="FISCAL APP Venezuela",
    page_icon="logo.jpg",
    layout="wide",
)

# Inicializar base de datos
init_db()

# Verificar licencia
valida, clave = verificar_licencia()

if not valida:
    st.warning("🔒 **APLICACIÓN NO ACTIVADA**")
    st.info("Por favor, ingresa tu Clave de Licencia Local para activar FISCAL APP.")
    
    c1, c2 = st.columns([3, 1])
    with c1:
        clave_input = st.text_input("Clave de Producto / Licencia:", type="password")
    with c2:
        st.write("")
        st.write("")
        if st.button("Activar Licencia", type="primary"):
            if activar_licencia_local(clave_input):
                st.success("¡Licencia activada con éxito!")
                st.rerun()
            else:
                st.error("Clave de licencia inválida.")
    st.stop()

# --- 🌐 BARRA LATERAL: TASA BCV EN VIVO ---
st.sidebar.image("logo.jpg", width=100)
st.sidebar.title("Panel de Control")
st.sidebar.divider()

tasa_actual = obtener_tasa_bcv()
st.sidebar.metric(
    label="💱 Tasa Oficial BCV (USD/VES)", 
    value=f"Bs. {tasa_actual:,.2f}",
    help="Tasa oficial obtenida directamente desde el Banco Central de Venezuela."
)
st.sidebar.success("🟢 Conectado al BCV")
st.sidebar.divider()
st.sidebar.info("Usa el menú superior o lateral de páginas para navegar a tus Movimientos y Previsión Fiscal.")

# --- CUERPO PRINCIPAL ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo.jpg", width=130)
    except:
        st.title("🇻🇪")

with col_titulo:
    st.title("FISCAL APP Venezuela")
    st.subheader("Sistema de Control Fiscal y Financiero Local")

st.divider()
st.success("¡Aplicación activada y conectada al BCV con éxito! Selecciona la página de Movimientos para registrar tus operaciones con la tasa del día.")
