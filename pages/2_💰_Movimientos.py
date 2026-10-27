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

# --- 📝 FORMULARIO DE REGISTRO ---
with st.expander("➕ Registrar Nueva Transacción (Ingreso / Gasto)", expanded=True):
    with st.form("form_transaccion"):
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha")
            banco = st.selectbox("Banco / Origen", BANCOS_VENEZUELA)
            tipo = st.selectbox("Tipo de Movimiento", ["Gasto", "Ingreso"])
        with col2:
            concepto = st.text_input("Concepto / Descripción")
            categoria = st.selectbox("Categoría", ["Operativo", "Inventario", "Servicios", "Impuestos", "Honorarios", "Otros"])
            tasa_bcv = st.number_input("Tasa BCV (Bs./USD)", value=36.5, format="%.2f")
        with col3:
            divisa = st.selectbox("Divisa Original", ["USD", "VES"])
            monto_original = st.number_input("Monto Original", value=0.0, format="%.2f")
            deducible = st.selectbox("¿Deducible ISLR?", ["Sí", "No"])

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            aplica_iva = st.checkbox("Calcular IVA (16%)", value=True)
        with col_f2:
            aplica_igtf = st.checkbox("Calcular IGTF (3% en Divisas)", value=True)

        submitted = st.form_submit_button("💾 Guardar Transacción", type="primary")
        if submitted:
            # Cálculos automáticos
            if divisa == "USD":
                monto_usd = monto_original
                monto_ves = monto_original * tasa_bcv
            else:
                monto_ves = monto_original
                monto_usd = monto_original / tasa_bcv if tasa_bcv > 0 else 0

            iva_ves = (monto_ves * 0.16) if (tipo == "Gasto" and aplica_iva) else 0.0
            igtf_ves = (monto_ves * 0.03) if (divisa == "USD" and aplica_igtf) else 0.0
            monto_deducible_ves = monto_ves if (tipo == "Gasto" and deducible == "Sí") else 0.0

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transacciones (
                    fecha, banco, tipo, concepto, categoria, tasa_bcv, 
                    deducible_islr, divisa, monto_original, monto_ves, monto_usd, 
                    iva_ves, igtf_ves, monto_deducible_ves, factura_ref, control
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '')
            """, (
                str(fecha), banco, tipo, concepto, categoria, tasa_bcv,
                deducible, divisa, monto_original, monto_ves, monto_usd,
                iva_ves, igtf_ves, monto_deducible_ves
            ))
            conn.commit()
            conn.close()
            st.success("¡Transacción registrada y procesada con éxito!")
            st.rerun()

st.divider()

# --- LECTURA DE DATOS PARA EL PANEL ---
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
    st.info("💡 No hay movimientos registrados todavía. Usa el formulario de arriba para agregar el primero.")
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
    col_f1.metric("Gastos Deducibles (ISLR)", f"Bs. {gastos_deducibles_ves:,.2f}")
    col_f2.metric("Base Imponible Estimada", f"Bs. {base_imponible_estimada:,.2f}")
    col_f3.metric("IGTF Total Pagado (3%)", f"Bs. {igtf_acumulado_ves:,.2f}")

    st.divider()

    # --- DETALLE Y GESTIÓN ---
    st.subheader("📋 Detalle de Transacciones Registradas")
    banco_filtro = st.selectbox("Filtrar lista por Banco:", ["Todos"] + BANCOS_VENEZUELA)
    if banco_filtro != "Todos":
        df_gestion = df[df["banco"] == banco_filtro]
    else:
        df_gestion = df

    st.dataframe(df_gestion, use_container_width=True)
    
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
