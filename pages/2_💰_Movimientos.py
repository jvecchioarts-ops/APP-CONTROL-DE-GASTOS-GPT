import streamlit as st
import pandas as pd
from core.db import get_db_connection
from core.auth import verificar_licencia

st.set_page_config(page_title="Gestión de Movimientos y Previsión Fiscal", page_icon="💰", layout="wide")

# Validar licencia en la página secundaria
valida, _ = verificar_licencia()
if not valida:
    st.error("⚠️ Acceso denegado. Por favor active la aplicación desde la página principal.")
    st.stop()

st.title("💰 Control de Movimientos y Previsión Fiscal")

# --- LECTURA DE DATOS ---
conn = get_db_connection()
try:
    df = pd.read_sql("SELECT * FROM transacciones", conn)
except Exception:
    df = pd.DataFrame()
finally:
    conn.close()

# --- 📊 PANEL DE IMPACTO FISCAL PREVENTIVO ---
st.subheader("📊 Panel de Previsión y Control Preventivo")

if df.empty:
    st.info("💡 No hay movimientos registrados. Utiliza el formulario o carga tus datos para ver las métricas preventivas.")
else:
    total_ingresos_ves = df[df["tipo"] == "Ingreso"]["monto_ves"].sum()
    total_gastos_ves = df[df["tipo"] == "Gasto"]["monto_ves"].sum()

    gastos_deducibles_ves = df[df["tipo"] == "Gasto"]["monto_deducible_ves"].sum()
    iva_acumulado_ves = df["iva_ves"].sum()
    igtf_acumulado_ves = df["igtf_ves"].sum()

    base_imponible_estimada = max(0.0, total_ingresos_ves - gastos_deducibles_ves)

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Ingresos", f"Bs. {total_ingresos_ves:,.2f}")
    col_m2.metric("Total Gastos", f"Bs. {total_gastos_ves:,.2f}")
    col_m3.metric("Resultado Operativo", f"Bs. {(total_ingresos_ves - total_gastos_ves):,.2f}")

    st.divider()

    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("Gastos Deducibles (ISLR)", f"Bs. {gastos_deducibles_ves:,.2f}", help="Monto de gastos vinculados a la actividad económica (Art. 27 LISLR)")
    col_f2.metric("Base Imponible Estimada", f"Bs. {base_imponible_estimada:,.2f}", help="Ingresos menos gastos deducibles sobre los que se estimará el ISLR")
    col_f3.metric("IGTF Total Pagado (3%)", f"Bs. {igtf_acumulado_ves:,.2f}", help="Impuesto pagado en transacciones en divisas/efectivo")

    st.info("🤝 **Nota de Coordinación Contable:** Este panel refleja cifras orientativas para tu planificación de flujo de caja. Comparte tus reportes exportados en Excel con tu contador de confianza para la elaboración formal de las declaraciones de ISLR e IVA.")

st.divider()

# --- DETALLE Y GESTIÓN DE REGISTROS ---
st.subheader("📋 Detalle de Transacciones Registradas")

BANCOS_VENEZUELA = [
    "Banco de Venezuela (BDV)",
    "Banesco Banco Universal",
    "Banco Mercantil",
    "BBVA Provincial",
    "Banco Nacional de Crédito (BNC)",
    "Bancamiga",
    "Banplus",
    "Efectivo / Divisas en Mano",
]

if df.empty:
    st.info("No hay transacciones registradas todavía.")
else:
    banco_filtro = st.selectbox("Filtrar lista por Banco:", ["Todos"] + BANCOS_VENEZUELA + ["Otro (Especificar)"])
    if banco_filtro != "Todos":
        df_gestion = df[df["banco"] == banco_filtro]
    else:
        df_gestion = df

    st.dataframe(df_gestion, use_container_width=True)
    
    st.divider()
    st.write("### 🗑️ Eliminar Registro")
    ids_disponibles = df_gestion["id"].tolist()
    if ids_disponibles:
        id_a_eliminar = st.selectbox("Selecciona el ID a eliminar:", ids_disponibles)
        confirmar = st.checkbox(f"⚠️ Confirmar eliminación permanente del ID #{id_a_eliminar}")
        if st.button("🔴 Eliminar Registro", type="primary"):
            if confirmar:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transacciones WHERE id = ?", (id_a_eliminar,))
                conn.commit()
                conn.close()
                st.success(f"Registro #{id_a_eliminar} eliminado correctamente.")
                st.rerun()
