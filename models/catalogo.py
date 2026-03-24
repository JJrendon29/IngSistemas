from db_connection import get_db_connection


# ========================================
# FUNCIONES DE CATÁLOGOS
# ========================================

def obtener_catalogo_titulos():
    """Retorna lista de {id, nombre} de títulos activos"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre FROM catalogo_titulos WHERE activo = 1 ORDER BY nombre ASC"
            )
            return cursor.fetchall()
    finally:
        conn.close()


def obtener_catalogo_habilidades():
    """
    Retorna dict agrupado por categoría con habilidades activas.
    {'lenguaje': [...], 'framework': [...], 'base_datos': [...], 'herramienta': [...]}
    """
    conn = get_db_connection()
    if not conn:
        return {}
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT id, nombre, categoria FROM catalogo_habilidades
                   WHERE activo = 1 ORDER BY categoria ASC, nombre ASC"""
            )
            filas = cursor.fetchall()
        resultado = {'lenguaje': [], 'framework': [], 'base_datos': [], 'herramienta': []}
        for fila in filas:
            cat = fila['categoria']
            if cat in resultado:
                resultado[cat].append({'id': fila['id'], 'nombre': fila['nombre']})
        return resultado
    finally:
        conn.close()


def obtener_catalogo_idiomas():
    """Retorna lista de {id, nombre} de idiomas activos"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre FROM catalogo_idiomas WHERE activo = 1 ORDER BY nombre ASC"
            )
            return cursor.fetchall()
    finally:
        conn.close()


def obtener_catalogo_programas():
    """Retorna lista de {id, nombre} de programas académicos activos"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre FROM catalogo_programas WHERE activo = 1 ORDER BY nombre ASC"
            )
            return cursor.fetchall()
    finally:
        conn.close()
