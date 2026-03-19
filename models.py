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


def crear_perfil(usuario_id, nombre, slug, titulo='', descripcion='',
                 email_contacto='', github='', linkedin=''):
    """Crea un nuevo perfil (estado pendiente por defecto)"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO perfiles 
                   (usuario_id, nombre, slug, titulo, descripcion, email_contacto, github, linkedin)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (usuario_id, nombre, slug, titulo, descripcion,
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
            'nombre', 'slug', 'titulo', 'descripcion', 'foto_url', 'cv_url',
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
    Reemplaza las habilidades de un perfil.
    habilidades: lista de dicts [{'nombre': '...', 'nivel': '...'}, ...]
    """
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM habilidades WHERE perfil_id = %s", (perfil_id,))
            for hab in habilidades:
                if hab.get('nombre', '').strip():
                    cursor.execute(
                        "INSERT INTO habilidades (perfil_id, nombre, nivel) VALUES (%s, %s, %s)",
                        (perfil_id, hab['nombre'].strip(), hab.get('nivel', 'intermedio'))
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
    """Reemplaza los idiomas de un perfil."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM idiomas WHERE perfil_id = %s", (perfil_id,))
            for i in idiomas_list:
                if i.get('idioma', '').strip():
                    cursor.execute(
                        "INSERT INTO idiomas (perfil_id, idioma, nivel) VALUES (%s, %s, %s)",
                        (perfil_id, i['idioma'].strip(), i.get('nivel', '').strip())
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
                   WHERE h.nombre LIKE %s AND p.estado = 'aprobado'
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
                """SELECT DISTINCT h.nombre FROM habilidades h
                   JOIN perfiles p ON p.id = h.perfil_id
                   WHERE p.estado = 'aprobado'
                   ORDER BY h.nombre ASC"""
            )
            return [row['nombre'] for row in cursor.fetchall()]
    finally:
        conn.close()


# ========================================
# HELPERS PRIVADOS
# ========================================

def _obtener_habilidades(cursor, perfil_id):
    cursor.execute(
        "SELECT nombre, nivel FROM habilidades WHERE perfil_id = %s", (perfil_id,)
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
        "SELECT idioma, nivel FROM idiomas WHERE perfil_id = %s", (perfil_id,)
    )
    return cursor.fetchall()
