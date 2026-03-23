from db_connection import get_db_connection
from models.perfil import _obtener_habilidades, _obtener_formacion, _obtener_idiomas


# ========================================
# FUNCIONES DE BÚSQUEDA
# ========================================

def buscar_perfiles_por_habilidad(habilidad, page=1, per_page=None):
    """
    Busca perfiles aprobados que tengan una habilidad específica.
    Si se pasa per_page, aplica paginación y retorna (perfiles, total).
    Sin per_page, retorna la lista completa (comportamiento original).
    """
    conn = get_db_connection()
    if not conn:
        return ([], 0) if per_page else []
    try:
        with conn.cursor() as cursor:
            base_query = """FROM perfiles p
                   JOIN habilidades h ON h.perfil_id = p.id
                   JOIN catalogo_habilidades ch ON ch.id = h.catalogo_id
                   WHERE ch.nombre LIKE %s AND p.estado = 'aprobado'"""

            if per_page:
                cursor.execute(
                    f"SELECT COUNT(DISTINCT p.id) AS total {base_query}",
                    (f'%{habilidad}%',)
                )
                total = cursor.fetchone()['total']

                offset = (page - 1) * per_page
                cursor.execute(
                    f"SELECT DISTINCT p.* {base_query} ORDER BY p.nombre ASC LIMIT %s OFFSET %s",
                    (f'%{habilidad}%', per_page, offset)
                )
            else:
                cursor.execute(
                    f"SELECT DISTINCT p.* {base_query} ORDER BY p.nombre ASC",
                    (f'%{habilidad}%',)
                )

            perfiles = cursor.fetchall()
            for perfil in perfiles:
                perfil['habilidades'] = _obtener_habilidades(cursor, perfil['id'])
                perfil['formacion'] = _obtener_formacion(cursor, perfil['id'])
                perfil['idiomas'] = _obtener_idiomas(cursor, perfil['id'])

        if per_page:
            return (perfiles, total)
        return perfiles
    finally:
        conn.close()


def buscar_perfiles(titulo='', habilidad='', idioma='', page=1, per_page=None):
    """
    Busca perfiles aprobados con filtro opcional por título, habilidad y/o idioma.
    - Solo titulo: WHERE p.titulo = %s
    - Solo habilidad: WHERE ch.nombre LIKE %s (con JOIN a habilidades)
    - Solo idioma: WHERE ci.nombre = %s (con JOIN a idiomas + catalogo_idiomas)
    - Combinaciones: todos los filtros activos se unen con AND
    - Ninguno: todos los aprobados
    Si se pasa per_page, aplica paginación y retorna (perfiles, total).
    Sin per_page, retorna la lista completa.
    """
    conn = get_db_connection()
    if not conn:
        return ([], 0) if per_page else []
    try:
        with conn.cursor() as cursor:
            condiciones = ["p.estado = 'aprobado'"]
            params_where = []

            # Determinar qué JOINs necesitamos
            necesita_join_hab = bool(habilidad)
            necesita_join_idioma = bool(idioma)

            if titulo:
                condiciones.append("p.titulo = %s")
                params_where.append(titulo)

            if habilidad:
                condiciones.append("ch.nombre LIKE %s")
                params_where.append(f'%{habilidad}%')

            if idioma:
                condiciones.append("ci.nombre = %s")
                params_where.append(idioma)

            where_clause = "WHERE " + " AND ".join(condiciones)

            # Construir FROM con los JOINs necesarios
            from_clause = "FROM perfiles p"
            if necesita_join_hab:
                from_clause += """
                   JOIN habilidades h ON h.perfil_id = p.id
                   JOIN catalogo_habilidades ch ON ch.id = h.catalogo_id"""
            if necesita_join_idioma:
                from_clause += """
                   JOIN idiomas id_rel ON id_rel.perfil_id = p.id
                   JOIN catalogo_idiomas ci ON ci.id = id_rel.catalogo_id"""

            # Con cualquier JOIN usamos DISTINCT para evitar duplicados
            if necesita_join_hab or necesita_join_idioma:
                select_distinct = "SELECT DISTINCT p.*"
                count_select = "SELECT COUNT(DISTINCT p.id) AS total"
            else:
                select_distinct = "SELECT p.*"
                count_select = "SELECT COUNT(*) AS total"

            if per_page:
                cursor.execute(
                    f"{count_select} {from_clause} {where_clause}",
                    params_where
                )
                total = cursor.fetchone()['total']

                offset = (page - 1) * per_page
                cursor.execute(
                    f"{select_distinct} {from_clause} {where_clause} ORDER BY p.nombre ASC LIMIT %s OFFSET %s",
                    params_where + [per_page, offset]
                )
            else:
                cursor.execute(
                    f"{select_distinct} {from_clause} {where_clause} ORDER BY p.nombre ASC",
                    params_where
                )
                total = None

            perfiles = cursor.fetchall()
            for perfil in perfiles:
                perfil['habilidades'] = _obtener_habilidades(cursor, perfil['id'])
                perfil['formacion'] = _obtener_formacion(cursor, perfil['id'])
                perfil['idiomas'] = _obtener_idiomas(cursor, perfil['id'])

        if per_page:
            return (perfiles, total)
        return perfiles
    finally:
        conn.close()


def obtener_habilidades_unicas():
    """Retorna lista de habilidades únicas de perfiles aprobados (para filtros)"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT DISTINCT ch.nombre FROM habilidades h
                   JOIN perfiles p ON p.id = h.perfil_id
                   JOIN catalogo_habilidades ch ON ch.id = h.catalogo_id
                   WHERE p.estado = 'aprobado'
                   ORDER BY ch.nombre ASC"""
            )
            return [row['nombre'] for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_titulos_unicos():
    """Retorna lista de títulos distintos de perfiles aprobados, en orden alfabético"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT DISTINCT titulo FROM perfiles
                   WHERE estado = 'aprobado' AND titulo IS NOT NULL AND titulo != ''
                   ORDER BY titulo ASC"""
            )
            return [row['titulo'] for row in cursor.fetchall()]
    finally:
        conn.close()


def obtener_idiomas_unicos():
    """Retorna lista de idiomas únicos de perfiles aprobados (para filtros)"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT DISTINCT ci.nombre FROM idiomas i
                   JOIN perfiles p ON p.id = i.perfil_id
                   JOIN catalogo_idiomas ci ON ci.id = i.catalogo_id
                   WHERE p.estado = 'aprobado'
                   ORDER BY ci.nombre ASC"""
            )
            return [row['nombre'] for row in cursor.fetchall()]
    finally:
        conn.close()
