// ========================================
// NAVEGACIÓN MÓVIL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            
            // Animar el ícono de hamburguesa
            navToggle.classList.toggle('active');
        });
        
        // Cerrar menú al hacer clic en un enlace
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
        
        // Cerrar menú al hacer clic fuera
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navMenu.contains(event.target);
            const isClickOnToggle = navToggle.contains(event.target);
            
            if (!isClickInsideNav && !isClickOnToggle && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });
    }
});

// ========================================
// CERRAR ALERTAS
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const closeButtons = document.querySelectorAll('.close-alert');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.parentElement;
            alert.style.animation = 'slideOut 0.3s ease';
            
            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    });
    
    // Auto cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
});

// Animación de salida para alertas
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ========================================
// VALIDACIÓN DE FORMULARIO
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const contactoForm = document.getElementById('contactoForm');
    
    if (contactoForm) {
        contactoForm.addEventListener('submit', function(e) {
            // Validar campos antes de enviar
            const nombre = document.getElementById('nombre').value.trim();
            const empresa = document.getElementById('empresa').value.trim();
            const correo = document.getElementById('correo').value.trim();
            const celular = document.getElementById('celular').value.trim();
            
            if (!nombre || !empresa || !correo || !celular) {
                e.preventDefault();
                showAlert('Por favor completa todos los campos obligatorios', 'error');
                return false;
            }
            
            // Validar formato de email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(correo)) {
                e.preventDefault();
                showAlert('Por favor ingresa un correo electrónico válido', 'error');
                return false;
            }
            
            // Validar teléfono (solo números)
            const phoneRegex = /^[0-9+\s()-]+$/;
            if (!phoneRegex.test(celular)) {
                e.preventDefault();
                showAlert('Por favor ingresa un número de teléfono válido', 'error');
                return false;
            }
            
            // Mostrar mensaje de carga
            const submitBtn = contactoForm.querySelector('button[type="submit"]');
            submitBtn.textContent = 'Enviando...';
            submitBtn.disabled = true;
        });
    }
});

// ========================================
// FUNCIÓN PARA MOSTRAR ALERTAS
// ========================================
function showAlert(message, type = 'success') {
    // Crear contenedor de alertas si no existe
    let flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) {
        flashContainer = document.createElement('div');
        flashContainer.className = 'flash-messages';
        document.body.appendChild(flashContainer);
    }
    
    // Crear alerta
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        ${message}
        <button class="close-alert">&times;</button>
    `;
    
    flashContainer.appendChild(alert);
    
    // Agregar evento de cierre
    const closeBtn = alert.querySelector('.close-alert');
    closeBtn.addEventListener('click', function() {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    });
    
    // Auto cerrar después de 5 segundos
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// ========================================
// SMOOTH SCROLL PARA ANCLAS
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Ignorar # solo
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                
                const offsetTop = target.offsetTop - 80; // 80px para el navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// ========================================
// ANIMACIONES AL HACER SCROLL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Elementos a animar
    const animatedElements = document.querySelectorAll(
        '.unidad-card, .team-member, .perfil-card, .topic-card, .resource-item'
    );
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// ========================================
// VALIDACIÓN EN TIEMPO REAL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.getElementById('correo');
    const phoneInput = document.getElementById('celular');
    
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.style.borderColor = '#ef4444';
                showFieldError(this, 'Correo electrónico inválido');
            } else {
                this.style.borderColor = '#10b981';
                removeFieldError(this);
            }
        });
    }
    
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            // Permitir solo números, +, espacios, paréntesis y guiones
            this.value = this.value.replace(/[^0-9+\s()-]/g, '');
        });
        
        phoneInput.addEventListener('blur', function() {
            const phone = this.value.trim();
            
            if (phone.length < 7) {
                this.style.borderColor = '#ef4444';
                showFieldError(this, 'Número de teléfono muy corto');
            } else {
                this.style.borderColor = '#10b981';
                removeFieldError(this);
            }
        });
    }
});

function showFieldError(input, message) {
    removeFieldError(input);
    
    const error = document.createElement('span');
    error.className = 'field-error';
    error.style.color = '#ef4444';
    error.style.fontSize = '0.875rem';
    error.style.marginTop = '0.25rem';
    error.textContent = message;
    
    input.parentElement.appendChild(error);
}

function removeFieldError(input) {
    const error = input.parentElement.querySelector('.field-error');
    if (error) {
        error.remove();
    }
}

// ========================================
// CONTADOR DE CARACTERES PARA TEXTAREA
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('mensaje');
    
    if (textarea) {
        const maxLength = textarea.getAttribute('maxlength') || 1000;
        
        // Crear contador
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.style.textAlign = 'right';
        counter.style.fontSize = '0.875rem';
        counter.style.color = '#64748b';
        counter.style.marginTop = '0.25rem';
        counter.textContent = `0 / ${maxLength}`;
        
        textarea.parentElement.appendChild(counter);
        
        // Actualizar contador
        textarea.addEventListener('input', function() {
            const length = this.value.length;
            counter.textContent = `${length} / ${maxLength}`;
            
            if (length >= maxLength * 0.9) {
                counter.style.color = '#ef4444';
            } else {
                counter.style.color = '#64748b';
            }
        });
    }
});

// ========================================
// PREVENIR ENVÍO DUPLICADO DEL FORMULARIO
// ========================================
let formSubmitting = false;

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (formSubmitting) {
                e.preventDefault();
                return false;
            }
            
            formSubmitting = true;
            
            // Restablecer después de 3 segundos (por si hay error)
            setTimeout(() => {
                formSubmitting = false;
            }, 3000);
        });
    });
});

// ========================================
// DESTACAR SECCIÓN ACTIVA EN NAVBAR
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link, .dropdown-menu a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        if (href && currentPath.includes(href) && href !== '/') {
            link.style.color = '#3b82f6';
            link.style.fontWeight = '600';
        }
    });
});

// ========================================
// SCROLL TO TOP BUTTON (OPCIONAL)
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    // Crear botón
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.innerHTML = '↑';
    scrollTopBtn.className = 'scroll-to-top';
    scrollTopBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: #2563eb;
        color: white;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 999;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    
    document.body.appendChild(scrollTopBtn);
    
    // Mostrar/ocultar botón según scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollTopBtn.style.opacity = '1';
            scrollTopBtn.style.visibility = 'visible';
        } else {
            scrollTopBtn.style.opacity = '0';
            scrollTopBtn.style.visibility = 'hidden';
        }
    });
    
    // Scroll al hacer clic
    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // Hover effect
    scrollTopBtn.addEventListener('mouseenter', function() {
        this.style.backgroundColor = '#1e40af';
        this.style.transform = 'scale(1.1)';
    });
    
    scrollTopBtn.addEventListener('mouseleave', function() {
        this.style.backgroundColor = '#2563eb';
        this.style.transform = 'scale(1)';
    });
});

// ========================================
// LAZY LOADING PARA IMÁGENES
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// ========================================
// MANEJO DE ERRORES DE IMÁGENES
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            // Si la imagen no carga, usar placeholder
            if (!this.src.includes('placeholder')) {
                const alt = this.alt || 'Imagen no disponible';
                this.src = `https://via.placeholder.com/400x400?text=${encodeURIComponent(alt)}`;
            }
        });
    });
});

// ========================================
// MODO OSCURO (OPCIONAL - BONUS)
// ========================================
// Descomenta esto si quieres agregar modo oscuro

document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.createElement('button');
    darkModeToggle.innerHTML = '🌓';
    darkModeToggle.style.cssText = `
        position: fixed;
        top: 80px;
        right: 30px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: white;
        border: 2px solid #2563eb;
        font-size: 1.2rem;
        cursor: pointer;
        z-index: 999;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    `;
    
    document.body.appendChild(darkModeToggle);
    
    darkModeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });
    
    // Cargar preferencia guardada
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
});

// ========================================
// SISTEMA DE PESTAÑAS
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            
            // Remover active de todos
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Agregar active al seleccionado
            this.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Si es la pestaña de gestionar, cargar contactos
            if (tabName === 'gestionar') {
                cargarContactos();
            }
        });
    });
});

// ========================================
// CRUD - CARGAR CONTACTOS
// ========================================
function cargarContactos() {
    const container = document.getElementById('contactos-list');
    container.innerHTML = '<p style="text-align: center; padding: 2rem;">Cargando...</p>';
    
    fetch('/api/contactos')
        .then(response => response.json())
        .then(data => {
            if (data.contactos && data.contactos.length > 0) {
                mostrarContactos(data.contactos);
            } else {
                container.innerHTML = `
                    <div class="empty-state">
                        <p>📭 No hay contactos registrados aún</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <p style="color: var(--error-color);">❌ Error al cargar contactos</p>
                </div>
            `;
        });
}

function mostrarContactos(contactos) {
    const container = document.getElementById('contactos-list');
    
    let html = `
        <table class="contactos-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Empresa</th>
                    <th>Correo</th>
                    <th>Celular</th>
                    <th>Fecha</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    contactos.forEach(contacto => {
        const fecha = new Date(contacto.fecha_registro).toLocaleDateString('es-CO');
        html += `
            <tr>
                <td>${contacto.id}</td>
                <td>${contacto.nombre}</td>
                <td>${contacto.empresa}</td>
                <td>${contacto.correo}</td>
                <td>${contacto.celular}</td>
                <td>${fecha}</td>
                <td class="contacto-actions">
                    <button class="btn-edit" onclick="editarContacto(${contacto.id})">✏️ Editar</button>
                    <button class="btn-delete" onclick="eliminarContacto(${contacto.id})">🗑️ Eliminar</button>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

// ========================================
// CRUD - ELIMINAR CONTACTO (MEJORADO)
// ========================================
function eliminarContacto(id) {
    // Buscar el nombre del contacto para mostrarlo en la confirmación
    fetch(`/api/contactos`)
        .then(response => response.json())
        .then(data => {
            const contacto = data.contactos.find(c => c.id === id);
            const nombre = contacto ? contacto.nombre : 'este contacto';
            
            if (confirm(`¿Estás seguro de eliminar a "${nombre}"?\n\nEsta acción no se puede deshacer.`)) {
                eliminarContactoConfirmado(id);
            }
        });
}

function eliminarContactoConfirmado(id) {
    fetch(`/api/contactos/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        showAlert('🗑️ Contacto eliminado exitosamente', 'success');
        cargarContactos();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('❌ Error al eliminar contacto', 'error');
    });
}

// ========================================
// CRUD - EDITAR CONTACTO (COMPLETO)
// ========================================
let contactoActual = null;

function editarContacto(id) {
    // Buscar el contacto en la lista actual
    fetch(`/api/contactos`)
        .then(response => response.json())
        .then(data => {
            const contacto = data.contactos.find(c => c.id === id);
            if (contacto) {
                mostrarModalEdicion(contacto);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar el contacto', 'error');
        });
}

function mostrarModalEdicion(contacto) {
    contactoActual = contacto;
    
    // Llenar el formulario con los datos actuales
    document.getElementById('edit_id').value = contacto.id;
    document.getElementById('edit_nombre').value = contacto.nombre;
    document.getElementById('edit_empresa').value = contacto.empresa;
    document.getElementById('edit_correo').value = contacto.correo;
    document.getElementById('edit_celular').value = contacto.celular;
    document.getElementById('edit_mensaje').value = contacto.mensaje || '';
    
    // Mostrar el modal
    const modal = document.getElementById('editModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevenir scroll del fondo
}

function cerrarModal() {
    const modal = document.getElementById('editModal');
    modal.classList.remove('active');
    document.body.style.overflow = ''; // Restaurar scroll
    contactoActual = null;
}

// Cerrar modal al hacer clic fuera
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('editModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                cerrarModal();
            }
        });
    }
});

// Cerrar modal con tecla ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        cerrarModal();
    }
});

// ========================================
// GUARDAR CAMBIOS DEL CONTACTO
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('editForm');
    
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const id = document.getElementById('edit_id').value;
            const datosActualizados = {
                nombre: document.getElementById('edit_nombre').value,
                empresa: document.getElementById('edit_empresa').value,
                correo: document.getElementById('edit_correo').value,
                celular: document.getElementById('edit_celular').value,
                mensaje: document.getElementById('edit_mensaje').value
            };
            
            // Mostrar indicador de carga
            const submitBtn = editForm.querySelector('button[type="submit"]');
            const textoOriginal = submitBtn.textContent;
            submitBtn.textContent = 'Guardando...';
            submitBtn.disabled = true;
            
            // Enviar actualización al servidor
            fetch(`/api/contactos/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(datosActualizados)
            })
            .then(response => response.json())
            .then(data => {
                showAlert('✅ Contacto actualizado exitosamente', 'success');
                cerrarModal();
                cargarContactos();
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('❌ Error al actualizar el contacto', 'error');
            })
            .finally(() => {
                submitBtn.textContent = textoOriginal;
                submitBtn.disabled = false;
            });
        });
    }
});

// ========================================
// VALIDACIÓN EN TIEMPO REAL EN MODAL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const editCorreo = document.getElementById('edit_correo');
    const editCelular = document.getElementById('edit_celular');
    
    if (editCorreo) {
        editCorreo.addEventListener('blur', function() {
            const email = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.style.borderColor = '#ef4444';
            } else {
                this.style.borderColor = '#10b981';
            }
        });
    }
    
    if (editCelular) {
        editCelular.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9+\s()-]/g, '');
        });
    }
});

console.log('✅ JavaScript cargado correctamente');