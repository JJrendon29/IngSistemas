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
# FUNCIONES DE USUARIOS (ADMIN)
# ========================================

def obtener_todos_usuarios():
    """Retorna lista de usuarios con id, email, rol, activo, created_at (sin password_hash)"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, rol, activo, created_at FROM usuarios ORDER BY created_at DESC"
            )
            return cursor.fetchall()
    finally:
        conn.close()


def resetear_password(user_id, nueva_password):
    """Hashea nueva_password con bcrypt y la actualiza en BD para el usuario dado."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        nuevo_hash = bcrypt.hashpw(
            nueva_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE usuarios SET password_hash = %s WHERE id = %s",
                (nuevo_hash, user_id)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Error al resetear password: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
