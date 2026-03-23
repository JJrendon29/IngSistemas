// editar_perfil.js
// Lee configuración inyectada por Jinja2 desde window.PERFIL_CONFIG

(function () {
    var cfg = window.PERFIL_CONFIG || {};
    var catalogoIdiomas = cfg.catalogoIdiomas || [];
    var nivelesIdioma = cfg.nivelesIdioma || ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Nativo'];
    var formCount = cfg.formCount !== undefined ? cfg.formCount : 1;
    var idiomaCount = cfg.idiomaCount !== undefined ? cfg.idiomaCount : 1;

    // ---- Toggle campo "Otro" para título ----
    window.toggleTituloOtro = function (valor) {
        var contenedor = document.getElementById('titulo-otro-container');
        var input = document.getElementById('titulo_otro');
        if (valor === 'otro') {
            contenedor.style.display = '';
            input.required = true;
        } else {
            contenedor.style.display = 'none';
            input.required = false;
            input.value = '';
        }
    };

    // Ejecutar al cargar por si el select ya tiene "otro" seleccionado
    (function () {
        var sel = document.getElementById('titulo_catalogo');
        if (sel && sel.value === 'otro') {
            document.getElementById('titulo-otro-container').style.display = '';
            document.getElementById('titulo_otro').required = true;
        }
    })();

    // ---- Toggle nivel de habilidad al marcar/desmarcar checkbox ----
    window.toggleNivelHabilidad = function (checkbox, habId) {
        var selectNivel = document.getElementById('hab-nivel-' + habId);
        var row = document.getElementById('hab-row-' + habId);
        if (checkbox.checked) {
            selectNivel.disabled = false;
            row.classList.add('activa');
        } else {
            selectNivel.disabled = true;
            row.classList.remove('activa');
        }
    };

    // ---- Toggle año fin según checkbox "en curso" ----
    window.toggleAnioFin = function (checkbox, selectId, textoId) {
        var select = document.getElementById(selectId);
        var texto = document.getElementById(textoId);
        if (checkbox.checked) {
            select.style.display = 'none';
            select.value = '';
            texto.style.display = '';
        } else {
            select.style.display = '';
            texto.style.display = 'none';
        }
    };

    // ---- Generar opciones de año para campos dinámicos ----
    function generarOpcionesAnio(nombre, selectedVal) {
        var html = '<option value="">Año ' + (nombre === 'inicio' ? 'inicio' : 'fin') + '</option>';
        for (var y = 2026; y >= 1990; y--) {
            html += '<option value="' + y + '"' + (selectedVal == y ? ' selected' : '') + '>' + y + '</option>';
        }
        return html;
    }

    // ---- Agregar fila de formación ----
    window.agregarFormacion = function () {
        var container = document.getElementById('formacion-container');
        var div = document.createElement('div');
        div.className = 'dynamic-block';
        var idx = formCount;
        div.innerHTML =
            '<div class="form-row">' +
                '<div class="form-group">' +
                    '<input type="text" name="form_titulo_' + idx + '" placeholder="Título obtenido">' +
                '</div>' +
                '<div class="form-group">' +
                    '<div class="institucion-wrapper">' +
                        '<input type="text" name="form_institucion_' + idx + '" placeholder="Institución"' +
                               ' class="institucion-input" autocomplete="off">' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div class="form-row formacion-anios-row">' +
                '<div class="form-group">' +
                    '<label class="form-label-sm">Año inicio</label>' +
                    '<select name="form_anio_inicio_' + idx + '" class="form-select-anio">' +
                        generarOpcionesAnio('inicio', '') +
                    '</select>' +
                '</div>' +
                '<div class="form-group formacion-encurso-group">' +
                    '<label class="form-label-sm">&nbsp;</label>' +
                    '<label class="encurso-label">' +
                        '<input type="checkbox"' +
                               ' name="form_en_curso_' + idx + '"' +
                               ' id="en_curso_' + idx + '"' +
                               ' onchange="toggleAnioFin(this, \'anio_fin_' + idx + '\', \'presente_txt_' + idx + '\')">' +
                        ' En curso' +
                    '</label>' +
                '</div>' +
                '<div class="form-group">' +
                    '<label class="form-label-sm">Año fin</label>' +
                    '<select name="form_anio_fin_' + idx + '" id="anio_fin_' + idx + '" class="form-select-anio">' +
                        generarOpcionesAnio('fin', '') +
                    '</select>' +
                    '<span id="presente_txt_' + idx + '" class="presente-texto" style="display:none">Presente</span>' +
                '</div>' +
                '<div class="form-group" style="display:flex;align-items:flex-end;">' +
                    '<button type="button" class="btn btn-sm btn-delete"' +
                            ' onclick="this.closest(\'.dynamic-block\').remove()">Eliminar</button>' +
                '</div>' +
            '</div>';
        container.appendChild(div);
        formCount++;
    };

    // ---- Agregar fila de idioma ----
    window.agregarIdioma = function () {
        var container = document.getElementById('idiomas-container');
        var div = document.createElement('div');
        div.className = 'dynamic-row';

        var opcionesIdioma = catalogoIdiomas.map(function (op) {
            return '<option value="' + op.id + '">' + op.nombre + '</option>';
        }).join('');

        var opcionesNivel = nivelesIdioma.map(function (nv) {
            return '<option value="' + nv + '">' + nv + '</option>';
        }).join('');

        div.innerHTML =
            '<select name="idioma_catalogo_id_' + idiomaCount + '" class="idioma-select">' +
                '<option value="">-- Selecciona un idioma --</option>' +
                opcionesIdioma +
            '</select>' +
            '<select name="idioma_nivel_' + idiomaCount + '">' +
                opcionesNivel +
            '</select>' +
            '<button type="button" class="btn-remove"' +
                    ' onclick="this.parentElement.remove()">&#x2715;</button>';
        container.appendChild(div);
        idiomaCount++;
    };

    // ============================================================
    // ---- Autocompletado de instituciones (event delegation) ----
    // ============================================================

    var debounceTimer = null;
    var dropdownActivo = null;
    var inputActivo = null;
    var idxResaltado = -1;

    function crearDropdown() {
        var ul = document.createElement('ul');
        ul.className = 'institucion-dropdown';
        return ul;
    }

    function cerrarDropdown() {
        if (dropdownActivo) {
            dropdownActivo.remove();
            dropdownActivo = null;
        }
        inputActivo = null;
        idxResaltado = -1;
    }

    function renderDropdown(input, nombres) {
        var wrapper = input.closest('.institucion-wrapper');
        var viejo = wrapper.querySelector('.institucion-dropdown');
        if (viejo) viejo.remove();

        if (!nombres.length) {
            var ul = crearDropdown();
            var li = document.createElement('li');
            li.className = 'sin-resultados';
            li.textContent = 'Sin resultados';
            ul.appendChild(li);
            wrapper.appendChild(ul);
            dropdownActivo = ul;
            inputActivo = input;
            idxResaltado = -1;
            return;
        }

        var ul = crearDropdown();
        nombres.forEach(function (nombre) {
            var li = document.createElement('li');
            li.textContent = nombre;
            li.addEventListener('mousedown', function (e) {
                e.preventDefault();
                input.value = nombre;
                cerrarDropdown();
            });
            ul.appendChild(li);
        });
        wrapper.appendChild(ul);
        dropdownActivo = ul;
        inputActivo = input;
        idxResaltado = -1;
    }

    function moverResaltado(direccion) {
        if (!dropdownActivo) return;
        var items = dropdownActivo.querySelectorAll('li:not(.sin-resultados)');
        if (!items.length) return;
        if (idxResaltado >= 0 && idxResaltado < items.length) {
            items[idxResaltado].classList.remove('activo');
        }
        idxResaltado += direccion;
        if (idxResaltado < 0) idxResaltado = items.length - 1;
        if (idxResaltado >= items.length) idxResaltado = 0;
        items[idxResaltado].classList.add('activo');
        items[idxResaltado].scrollIntoView({ block: 'nearest' });
    }

    function consultarApi(input, q) {
        fetch('/api/instituciones?q=' + encodeURIComponent(q))
            .then(function (r) { return r.json(); })
            .then(function (nombres) {
                if (input.value.trim() === q) {
                    renderDropdown(input, nombres);
                }
            })
            .catch(function () {
                cerrarDropdown();
            });
    }

    var formContainer = document.querySelector('.perfil-form');
    if (!formContainer) return;

    formContainer.addEventListener('input', function (e) {
        if (!e.target.classList.contains('institucion-input')) return;
        var input = e.target;
        var q = input.value.trim();

        clearTimeout(debounceTimer);

        if (q.length < 2) {
            cerrarDropdown();
            return;
        }

        debounceTimer = setTimeout(function () {
            consultarApi(input, q);
        }, 300);
    });

    formContainer.addEventListener('keydown', function (e) {
        if (!e.target.classList.contains('institucion-input')) return;
        if (!dropdownActivo) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            moverResaltado(1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            moverResaltado(-1);
        } else if (e.key === 'Enter') {
            if (idxResaltado >= 0) {
                e.preventDefault();
                var items = dropdownActivo.querySelectorAll('li:not(.sin-resultados)');
                if (items[idxResaltado]) {
                    e.target.value = items[idxResaltado].textContent;
                    cerrarDropdown();
                }
            }
        } else if (e.key === 'Escape') {
            cerrarDropdown();
        }
    });

    formContainer.addEventListener('blur', function (e) {
        if (!e.target.classList.contains('institucion-input')) return;
        setTimeout(cerrarDropdown, 150);
    }, true);

    document.addEventListener('click', function (e) {
        if (dropdownActivo && !e.target.closest('.institucion-wrapper')) {
            cerrarDropdown();
        }
    });
})();
