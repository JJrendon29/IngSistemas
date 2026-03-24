from db_connection import get_db_connection


# ========================================
# FUNCIONES DE REVISIÓN CAMPO POR CAMPO
# ========================================

CAMPOS_REVISABLES = [
    'foto', 'cv', 'nombre', 'titulo', 'descripcion',
    'habilidades', 'formacion_actual', 'formacion', 'idiomas', 'github', 'linkedin', 'email_contacto'
]


def obtener_revisiones_perfil(perfil_id):
    """
    Retorna un dict {campo: {'estado': '...', 'comentario': '...'}}
    con las revisiones actuales de la tabla revisiones_campo.
    Solo incluye los campos que tienen registro en la BD.
    """
    conn = get_db_connection()
    if not conn:
        return {}
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT campo, estado, comentario FROM revisiones_campo WHERE perfil_id = %s",
                (perfil_id,)
            )
            filas = cursor.fetchall()
        return {
            fila['campo']: {
                'estado': fila['estado'],
                'comentario': fila['comentario'] or ''
            }
            for fila in filas
        }
    finally:
        conn.close()


def guardar_revisiones(perfil_id, revisiones_dict, comentario_general):
    """
    Guarda las revisiones campo por campo para un perfil.
    revisiones_dict: {campo: {'estado': 'aprobado'|'rechazado', 'comentario': '...'}}
    Actualiza perfiles.comentario_admin con comentario_general.
    Calcula el estado global del perfil según los resultados.
    """
    estados_validos = {'aprobado', 'rechazado'}
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            for campo, datos in revisiones_dict.items():
                if campo not in CAMPOS_REVISABLES:
                    continue
                estado = datos.get('estado', 'pendiente')
                if estado not in estados_validos:
                    continue
                comentario = datos.get('comentario', '') or ''
                cursor.execute(
                    """INSERT INTO revisiones_campo (perfil_id, campo, estado, comentario)
                       VALUES (%s, %s, %s, %s)
                       ON DUPLICATE KEY UPDATE
                           estado = VALUES(estado),
                           comentario = VALUES(comentario),
                           updated_at = CURRENT_TIMESTAMP""",
                    (perfil_id, campo, estado, comentario)
                )

            # Determinar el estado global del perfil
            cursor.execute(
                "SELECT estado FROM revisiones_campo WHERE perfil_id = %s",
                (perfil_id,)
            )
            todas = cursor.fetchall()
            estados = [r['estado'] for r in todas]

            if not estados:
                nuevo_estado = 'pendiente'
            elif all(e == 'aprobado' for e in estados):
                nuevo_estado = 'aprobado'
            elif any(e == 'rechazado' for e in estados):
                nuevo_estado = 'en_revision'
            else:
                nuevo_estado = 'en_revision'

            cursor.execute(
                "UPDATE perfiles SET estado = %s, comentario_admin = %s WHERE id = %s",
                (nuevo_estado, comentario_general or '', perfil_id)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar revisiones: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def resetear_revisiones_pendientes(perfil_id):
    """
    Pone en estado 'pendiente' los campos que estaban 'rechazado'
    (el estudiante los corrigió y volvió a enviar).
    También cambia perfiles.estado de 'en_revision' a 'pendiente'.
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """UPDATE revisiones_campo SET estado = 'pendiente',
                       comentario = NULL,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE perfil_id = %s AND estado = 'rechazado'""",
                (perfil_id,)
            )
            cursor.execute(
                """UPDATE perfiles SET estado = 'pendiente'
                   WHERE id = %s AND estado = 'en_revision'""",
                (perfil_id,)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error al resetear revisiones: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
