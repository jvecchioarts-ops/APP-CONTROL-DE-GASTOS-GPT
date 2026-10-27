import sqlite3
import os

DB_NAME = "control_fiscal.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT, banco TEXT, tipo TEXT, concepto TEXT, categoria TEXT,
            tasa_bcv REAL, deducible_islr TEXT, divisa TEXT, monto_original REAL,
            monto_ves REAL, monto_usd REAL, iva_ves REAL, igtf_ves REAL,
            monto_deducible_ves REAL, factura_ref TEXT, control TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracion_licencia (
            id INTEGER PRIMARY KEY,
            licencia_key TEXT,
            activa INTEGER
        )
    """)
    cursor.execute("INSERT OR IGNORE INTO configuracion_licencia (id, licencia_key, activa) VALUES (1, '', 0)")
    conn.commit()
    conn.close()
