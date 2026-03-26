// ========================================
// NAVEGACIÓN MÓVIL
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
        
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            });
        });
        
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
            setTimeout(() => alert.remove(), 300);
        });
    });
    
    // Auto cerrar después de 5 segundos
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// ========================================
// VALIDACIÓN DE FORMULARIO DE CONTACTO
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const contactoForm = document.getElementById('contactoForm');
    
    if (contactoForm) {
        contactoForm.addEventListener('submit', function(e) {
            const nombre = document.getElementById('nombre').value.trim();
            const empresa = document.getElementById('empresa').value.trim();
            const correo = document.getElementById('correo').value.trim();
            const celular = document.getElementById('celular').value.trim();
            
            if (!nombre || !empresa || !correo || !celular) {
                e.preventDefault();
                showAlert('Por favor completa todos los campos obligatorios', 'error');
                return false;
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(correo)) {
                e.preventDefault();
                showAlert('Por favor ingresa un correo electrónico válido', 'error');
                return false;
            }
            
            const phoneRegex = /^[0-9+\s()-]+$/;
            if (!phoneRegex.test(celular)) {
                e.preventDefault();
                showAlert('Por favor ingresa un número de teléfono válido', 'error');
                return false;
            }
            
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
    let flashContainer = document.querySelector('.flash-messages');
    if (!flashContainer) {
        flashContainer = document.createElement('div');
        flashContainer.className = 'flash-messages';
        document.body.appendChild(flashContainer);
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        ${message}
        <button class="close-alert">&times;</button>
    `;
    
    flashContainer.appendChild(alert);
    
    const closeBtn = alert.querySelector('.close-alert');
    closeBtn.addEventListener('click', function() {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    });
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

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
            } else if (email) {
                this.style.borderColor = '#10b981';
            }
        });
    }
    
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9+\s()-]/g, '');
        });
    }
});

// ========================================
// PREVENIR ENVÍO DUPLICADO
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
            setTimeout(() => { formSubmitting = false; }, 3000);
        });
    });
});

// ========================================
// SCROLL TO TOP
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const scrollTopBtn = document.createElement('button');
    scrollTopBtn.innerHTML = '<i data-lucide="arrow-up"></i>';
    scrollTopBtn.className = 'scroll-to-top';
    scrollTopBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: var(--primary-color, #007b99);
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
    if (window.lucide) { lucide.createIcons(); }

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollTopBtn.style.opacity = '1';
            scrollTopBtn.style.visibility = 'visible';
        } else {
            scrollTopBtn.style.opacity = '0';
            scrollTopBtn.style.visibility = 'hidden';
        }
    });
    
    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});

// ========================================
// MODO OSCURO
// ========================================
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
        border: 2px solid var(--primary-color, #007b99);
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
    
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
    }
});

console.log('✅ JavaScript cargado correctamente');
