from db_connection import get_db_connection


# ========================================
# HELPERS PRIVADOS
# ========================================

def _obtener_habilidades(cursor, perfil_id):
    cursor.execute(
        """SELECT h.id, ch.nombre, h.nivel, ch.categoria, h.catalogo_id
           FROM habilidades h
           JOIN catalogo_habilidades ch ON ch.id = h.catalogo_id
           WHERE h.perfil_id = %s
           ORDER BY ch.categoria ASC, ch.nombre ASC""",
        (perfil_id,)
    )
    return cursor.fetchall()


def _obtener_formacion(cursor, perfil_id):
    cursor.execute(
        """SELECT titulo, institucion, anio, anio_inicio, anio_fin, en_curso
           FROM formacion WHERE perfil_id = %s""",
        (perfil_id,)
    )
    return cursor.fetchall()


def _obtener_idiomas(cursor, perfil_id):
    cursor.execute(
        """SELECT i.id, ci.nombre AS idioma, i.nivel, i.catalogo_id
           FROM idiomas i
           JOIN catalogo_idiomas ci ON ci.id = i.catalogo_id
           WHERE i.perfil_id = %s
           ORDER BY ci.nombre ASC""",
        (perfil_id,)
    )
    return cursor.fetchall()


# ========================================
# FUNCIONES DE PERFILES
# ========================================

def obtener_todos_perfiles(solo_aprobados=True, page=1, per_page=None):
    """
    Obtiene perfiles (opcionalmente solo los aprobados).
    Si se pasa per_page, aplica paginación y retorna (perfiles, total).
    Sin per_page, retorna la lista completa (comportamiento original).
    """
    conn = get_db_connection()
    if not conn:
        return ([], 0) if per_page else []
    try:
        with conn.cursor() as cursor:
            condicion = "WHERE estado = 'aprobado'" if solo_aprobados else ""

            if per_page:
                # Contar total
                cursor.execute(f"SELECT COUNT(*) AS total FROM perfiles {condicion}")
                total = cursor.fetchone()['total']

                # Obtener página
                offset = (page - 1) * per_page
                cursor.execute(
                    f"SELECT * FROM perfiles {condicion} ORDER BY nombre ASC LIMIT %s OFFSET %s",
                    (per_page, offset)
                )
            else:
                cursor.execute(
                    f"SELECT * FROM perfiles {condicion} ORDER BY nombre ASC"
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


def obtener_perfil_por_slug(slug, solo_aprobados=True):
    """Obtiene un perfil por su slug"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            if solo_aprobados:
                cursor.execute(
                    "SELECT * FROM perfiles WHERE slug = %s AND estado = 'aprobado'",
                    (slug,)
                )
            else:
                cursor.execute("SELECT * FROM perfiles WHERE slug = %s", (slug,))
            perfil = cursor.fetchone()

            if perfil:
                perfil['habilidades'] = _obtener_habilidades(cursor, perfil['id'])
                perfil['formacion'] = _obtener_formacion(cursor, perfil['id'])
                perfil['idiomas'] = _obtener_idiomas(cursor, perfil['id'])

        return perfil
    finally:
        conn.close()


def obtener_perfil_por_usuario(usuario_id):
    """Obtiene el perfil de un usuario específico"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM perfiles WHERE usuario_id = %s", (usuario_id,)
            )
            perfil = cursor.fetchone()

            if perfil:
                perfil['habilidades'] = _obtener_habilidades(cursor, perfil['id'])
                perfil['formacion'] = _obtener_formacion(cursor, perfil['id'])
                perfil['idiomas'] = _obtener_idiomas(cursor, perfil['id'])

        return perfil
    finally:
        conn.close()


def crear_perfil(usuario_id, nombre, slug, titulo='', titulo_otro='',
                 descripcion='', email_contacto='', github='', linkedin=''):
    """Crea un nuevo perfil (estado pendiente por defecto)"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO perfiles
                   (usuario_id, nombre, slug, titulo, titulo_otro, descripcion,
                    email_contacto, github, linkedin)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (usuario_id, nombre, slug, titulo, titulo_otro, descripcion,
                 email_contacto, github, linkedin)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Error al crear perfil: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def actualizar_perfil(perfil_id, **campos):
    """Actualiza campos de un perfil. Al editar, vuelve a estado pendiente."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        campos_permitidos = [
            'nombre', 'slug', 'titulo', 'titulo_otro', 'descripcion', 'foto_url', 'cv_url',
            'email_contacto', 'github', 'linkedin', 'estado',
            'github_verificado', 'linkedin_verificado'
        ]
        campos_sql = []
        valores = []
        for campo, valor in campos.items():
            if campo in campos_permitidos:
                campos_sql.append(f"{campo} = %s")
                valores.append(valor)

        if not campos_sql:
            return False

        # Si no se está cambiando el estado explícitamente, poner en pendiente
        if 'estado' not in campos:
            campos_sql.append("estado = 'pendiente'")

        valores.append(perfil_id)
        sql = f"UPDATE perfiles SET {', '.join(campos_sql)} WHERE id = %s"

        with conn.cursor() as cursor:
            cursor.execute(sql, valores)
            conn.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar perfil: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def guardar_habilidades(perfil_id, habilidades):
    """
    Reemplaza las habilidades de un perfil usando catálogo.
    habilidades: lista de dicts [{'catalogo_id': int, 'nivel': str}, ...]
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM habilidades WHERE perfil_id = %s", (perfil_id,))
            for hab in habilidades:
                catalogo_id = hab.get('catalogo_id')
                if catalogo_id:
                    cursor.execute(
                        "INSERT INTO habilidades (perfil_id, catalogo_id, nivel) VALUES (%s, %s, %s)",
                        (perfil_id, int(catalogo_id), hab.get('nivel', 'intermedio'))
                    )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar habilidades: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def guardar_formacion(perfil_id, formaciones):
    """Reemplaza la formación académica de un perfil."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM formacion WHERE perfil_id = %s", (perfil_id,))
            for f in formaciones:
                if f.get('titulo', '').strip():
                    cursor.execute(
                        """INSERT INTO formacion
                           (perfil_id, titulo, institucion, anio_inicio, anio_fin, en_curso)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (perfil_id,
                         f['titulo'].strip(),
                         f.get('institucion', '').strip(),
                         f.get('anio_inicio'),
                         f.get('anio_fin'),
                         bool(f.get('en_curso', False)))
                    )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar formación: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def guardar_idiomas(perfil_id, idiomas_list):
    """
    Reemplaza los idiomas de un perfil usando catálogo.
    idiomas_list: lista de dicts [{'catalogo_id': int, 'nivel': 'A1'|'A2'|...|'Nativo'}, ...]
    """
    niveles_validos = {'A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Nativo'}
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM idiomas WHERE perfil_id = %s", (perfil_id,))
            for i in idiomas_list:
                catalogo_id = i.get('catalogo_id')
                nivel = i.get('nivel', '').strip()
                if catalogo_id and nivel in niveles_validos:
                    cursor.execute(
                        "INSERT INTO idiomas (perfil_id, catalogo_id, nivel) VALUES (%s, %s, %s)",
                        (perfil_id, int(catalogo_id), nivel)
                    )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error al guardar idiomas: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
