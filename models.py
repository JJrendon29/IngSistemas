from flask_login import UserMixin
from db_connection import get_db_connection
import bcrypt


# ========================================
# MODELO DE USUARIO (Flask-Login)
# ========================================

class Usuario(UserMixin):
    def __init__(self, id, email, password_hash, rol, activo):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.rol = rol
        self.activo = activo

    def es_admin(self):
        return self.rol == 'admin'

    def verificar_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    @staticmethod
    def obtener_por_id(user_id):
        conn = get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
                row = cursor.fetchone()
            if row:
                return Usuario(
                    id=row['id'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    rol=row['rol'],
                    activo=row['activo']
                )
            return None
        finally:
            conn.close()

    @staticmethod
    def obtener_por_email(email):
        conn = get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                row = cursor.fetchone()
            if row:
                return Usuario(
                    id=row['id'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    rol=row['rol'],
                    activo=row['activo']
                )
            return None
        finally:
            conn.close()

    @staticmethod
    def crear(email, password, rol='estudiante'):
        conn = get_db_connection()
        if not conn:
            return None
        try:
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (email, password_hash, rol) VALUES (%s, %s, %s)",
                    (email, password_hash, rol)
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()


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


# ========================================
# FUNCIONES DE PERFILES
# ========================================

def obtener_todos_perfiles(solo_aprobados=True):
    """Obtiene todos los perfiles (opcionalmente solo los aprobados)"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            if solo_aprobados:
                cursor.execute(
                    "SELECT * FROM perfiles WHERE estado = 'aprobado' ORDER BY nombre ASC"
                )
            else:
                cursor.execute("SELECT * FROM perfiles ORDER BY nombre ASC")
            perfiles = cursor.fetchall()

            for perfil in perfiles:
                perfil['habilidades'] = _obtener_habilidades(cursor, perfil['id'])
                perfil['formacion'] = _obtener_formacion(cursor, perfil['id'])
                perfil['idiomas'] = _obtener_idiomas(cursor, perfil['id'])

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
            'email_contacto', 'github', 'linkedin', 'estado'
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
                        "INSERT INTO formacion (perfil_id, titulo, institucion, anio) VALUES (%s, %s, %s, %s)",
                        (perfil_id, f['titulo'].strip(),
                         f.get('institucion', '').strip(),
                         f.get('anio', '').strip())
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


# ========================================
# FUNCIONES DE BÚSQUEDA
# ========================================

def buscar_perfiles_por_habilidad(habilidad):
    """Busca perfiles aprobados que tengan una habilidad específica"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT DISTINCT p.* FROM perfiles p
                   JOIN habilidades h ON h.perfil_id = p.id
                   JOIN catalogo_habilidades ch ON ch.id = h.catalogo_id
                   WHERE ch.nombre LIKE %s AND p.estado = 'aprobado'
                   ORDER BY p.nombre ASC""",
                (f'%{habilidad}%',)
            )
            perfiles = cursor.fetchall()
            for perfil in perfiles:
                perfil['habilidades'] = _obtener_habilidades(cursor, perfil['id'])
                perfil['formacion'] = _obtener_formacion(cursor, perfil['id'])
                perfil['idiomas'] = _obtener_idiomas(cursor, perfil['id'])
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


# ========================================
# FUNCIONES DE REVISIÓN CAMPO POR CAMPO
# ========================================

CAMPOS_REVISABLES = [
    'foto', 'cv', 'nombre', 'titulo', 'descripcion',
    'habilidades', 'formacion', 'idiomas', 'github', 'linkedin', 'email_contacto'
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
        "SELECT titulo, institucion, anio FROM formacion WHERE perfil_id = %s",
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
