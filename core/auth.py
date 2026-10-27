from core.db import get_db_connection

def verificar_licencia():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT licencia_key, activa FROM configuracion_licencia WHERE id = 1")
    res = cursor.fetchone()
    conn.close()
    if res and res[1] == 1:
        return True, res[0]
    return False, ""

def activar_licencia_local(clave_ingresada):
    CLAVE_MAESTRA = "FISCAL-PRO-2026"
    if clave_ingresada.strip().upper() == CLAVE_MAESTRA or clave_ingresada.endswith("-FISCAL2026"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE configuracion_licencia SET licencia_key = ?, activa = 1 WHERE id = 1", (clave_ingresada,))
        conn.commit()
        conn.close()
        return True
    return False
