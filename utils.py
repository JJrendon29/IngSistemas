import os
import json

def obtener_todos_perfiles():
    """
    Escanea la carpeta static/usuarios/ y retorna todos los perfiles
    detectados automáticamente.
    
    Returns:
        list: Lista de diccionarios con información de cada perfil
    """
    perfiles = []
    usuarios_dir = 'static/usuarios'
    
    # Verificar que la carpeta existe
    if not os.path.exists(usuarios_dir):
        os.makedirs(usuarios_dir)
        return perfiles
    
    # Recorrer cada carpeta de usuario
    for usuario_folder in os.listdir(usuarios_dir):
        # Ignorar la carpeta _template
        if usuario_folder.startswith('_'):
            continue
            
        usuario_path = os.path.join(usuarios_dir, usuario_folder)
        
        # Solo procesar si es una carpeta
        if os.path.isdir(usuario_path):
            datos_json = os.path.join(usuario_path, 'datos.json')
            
            # Verificar que existe datos.json
            if os.path.exists(datos_json):
                try:
                    with open(datos_json, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    # Agregar información de rutas y ID
                    datos['id'] = usuario_folder
                    datos['slug'] = usuario_folder
                    datos['ruta_imagen'] = f'usuarios/{usuario_folder}/{datos["archivos"]["imagen"]}'
                    datos['ruta_cv'] = f'usuarios/{usuario_folder}/{datos["archivos"]["cv"]}'
                    datos['url_perfil'] = f'/perfil/{usuario_folder}'
                    
                    perfiles.append(datos)
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Error al leer JSON en {datos_json}: {e}")
                except KeyError as e:
                    print(f"❌ Falta campo requerido en {datos_json}: {e}")
                except Exception as e:
                    print(f"❌ Error procesando {usuario_folder}: {e}")
    
    # Ordenar perfiles alfabéticamente por nombre
    perfiles.sort(key=lambda x: x.get('nombre', ''))
    
    return perfiles


def obtener_perfil_por_slug(slug):
    """
    Obtiene un perfil específico por su slug (nombre de carpeta)
    
    Args:
        slug (str): Nombre de la carpeta del usuario
        
    Returns:
        dict: Datos del perfil o None si no existe
    """
    usuario_path = os.path.join('static/usuarios', slug)
    datos_json = os.path.join(usuario_path, 'datos.json')
    
    if not os.path.exists(datos_json):
        return None
    
    try:
        with open(datos_json, 'r', encoding='utf-8') as f:
            perfil = json.load(f)
        
        # Agregar información adicional
        perfil['id'] = slug
        perfil['slug'] = slug
        perfil['ruta_imagen'] = f'usuarios/{slug}/{perfil["archivos"]["imagen"]}'
        perfil['ruta_cv'] = f'usuarios/{slug}/{perfil["archivos"]["cv"]}'
        
        return perfil
        
    except Exception as e:
        print(f"❌ Error al obtener perfil {slug}: {e}")
        return None