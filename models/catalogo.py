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


def obtener_todas_habilidades_admin():
    """
    Retorna TODAS las habilidades (activas e inactivas), ordenadas por categoría y nombre.
    Para uso del panel de administración.
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT id, nombre, categoria, activo
                   FROM catalogo_habilidades
                   ORDER BY categoria ASC, nombre ASC"""
            )
            return cursor.fetchall()
    finally:
        conn.close()


def agregar_habilidad(nombre, categoria):
    """
    Inserta una nueva habilidad en el catálogo.
    Retorna True si se insertó, False si ya existe (mismo nombre + categoría) o hubo error.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            # Verificar duplicado
            cursor.execute(
                "SELECT id FROM catalogo_habilidades WHERE nombre = %s AND categoria = %s",
                (nombre.strip(), categoria)
            )
            if cursor.fetchone():
                return False
            cursor.execute(
                "INSERT INTO catalogo_habilidades (nombre, categoria, activo) VALUES (%s, %s, 1)",
                (nombre.strip(), categoria)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al agregar habilidad: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def editar_habilidad(habilidad_id, nombre, categoria):
    """
    Actualiza nombre y categoría de una habilidad existente.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE catalogo_habilidades SET nombre = %s, categoria = %s WHERE id = %s",
                (nombre.strip(), categoria, habilidad_id)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al editar habilidad: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def toggle_habilidad(habilidad_id):
    """
    Cambia el campo activo de 1 a 0 o de 0 a 1.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE catalogo_habilidades SET activo = 1 - activo WHERE id = %s",
                (habilidad_id,)
            )
            conn.commit()
            return True
    except Exception as e:
        print(f"Error al toggle habilidad: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
