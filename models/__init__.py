# Re-exportar todo lo público para que los imports existentes sigan funcionando:
# from models import Usuario, obtener_todos_perfiles, ...

from models.usuario import (
    Usuario,
    obtener_todos_usuarios,
    resetear_password,
)

from models.catalogo import (
    obtener_catalogo_titulos,
    obtener_catalogo_habilidades,
    obtener_catalogo_idiomas,
    obtener_catalogo_programas,
    obtener_todas_habilidades_admin,
    agregar_habilidad,
    editar_habilidad,
    toggle_habilidad,
)

from models.perfil import (
    obtener_todos_perfiles,
    obtener_perfil_por_slug,
    obtener_perfil_por_usuario,
    crear_perfil,
    actualizar_perfil,
    guardar_habilidades,
    guardar_formacion,
    guardar_idiomas,
    _obtener_habilidades,
    _obtener_formacion,
    _obtener_idiomas,
)

from models.busqueda import (
    buscar_perfiles,
    buscar_perfiles_por_habilidad,
    obtener_habilidades_unicas,
    obtener_titulos_unicos,
    obtener_idiomas_unicos,
)

from models.revision import (
    CAMPOS_REVISABLES,
    obtener_revisiones_perfil,
    guardar_revisiones,
    resetear_revisiones_pendientes,
)

__all__ = [
    # usuario
    'Usuario',
    'obtener_todos_usuarios',
    'resetear_password',
    # catalogo
    'obtener_catalogo_titulos',
    'obtener_catalogo_habilidades',
    'obtener_catalogo_idiomas',
    'obtener_catalogo_programas',
    'obtener_todas_habilidades_admin',
    'agregar_habilidad',
    'editar_habilidad',
    'toggle_habilidad',
    # perfil
    'obtener_todos_perfiles',
    'obtener_perfil_por_slug',
    'obtener_perfil_por_usuario',
    'crear_perfil',
    'actualizar_perfil',
    'guardar_habilidades',
    'guardar_formacion',
    'guardar_idiomas',
    '_obtener_habilidades',
    '_obtener_formacion',
    '_obtener_idiomas',
    # busqueda
    'buscar_perfiles',
    'buscar_perfiles_por_habilidad',
    'obtener_habilidades_unicas',
    'obtener_titulos_unicos',
    'obtener_idiomas_unicos',
    # revision
    'CAMPOS_REVISABLES',
    'obtener_revisiones_perfil',
    'guardar_revisiones',
    'resetear_revisiones_pendientes',
]
