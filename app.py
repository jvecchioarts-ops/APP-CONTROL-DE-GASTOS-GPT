import streamlit as st
from core.db import init_db
from core.auth import verificar_licencia, activar_licencia_local

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

# Cabecera principal si está activo
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
st.success("¡Aplicación activada con éxito! Utiliza el menú lateral izquierdo para navegar entre las páginas disponibles (como Movimientos, Registros y Cierres).")
