-- ========================================
-- SCHEMA: Sistema de Perfiles de Practicantes
-- Universidad Católica Luis Amigó
-- ========================================

CREATE DATABASE IF NOT EXISTS practicantes_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE practicantes_db;

-- ========================================
-- TABLA: usuarios (autenticación y roles)
-- ========================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('estudiante', 'admin') NOT NULL DEFAULT 'estudiante',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ========================================
-- TABLA: perfiles (información del practicante)
-- ========================================
CREATE TABLE IF NOT EXISTS perfiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    slug VARCHAR(150) NOT NULL UNIQUE,
    titulo VARCHAR(200) DEFAULT NULL,
    descripcion TEXT DEFAULT NULL,
    foto_url VARCHAR(300) DEFAULT NULL,
    cv_url VARCHAR(300) DEFAULT NULL,
    email_contacto VARCHAR(150) DEFAULT NULL,
    github VARCHAR(255) DEFAULT NULL,
    linkedin VARCHAR(255) DEFAULT NULL,
    estado ENUM('pendiente', 'aprobado', 'rechazado') NOT NULL DEFAULT 'pendiente',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: habilidades (texto libre por perfil)
-- Cada estudiante agrega las suyas propias.
-- El campo nombre sirve para filtrar búsquedas.
-- ========================================
CREATE TABLE IF NOT EXISTS habilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    perfil_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    nivel ENUM('basico', 'intermedio', 'avanzado') NOT NULL DEFAULT 'intermedio',
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Índice para búsqueda/filtro por habilidad
CREATE INDEX idx_habilidades_nombre ON habilidades(nombre);

-- ========================================
-- TABLA: formacion (formación académica)
-- ========================================
CREATE TABLE IF NOT EXISTS formacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    perfil_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    institucion VARCHAR(200) NOT NULL,
    anio VARCHAR(20) DEFAULT NULL,
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: idiomas
-- ========================================
CREATE TABLE IF NOT EXISTS idiomas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    perfil_id INT NOT NULL,
    idioma VARCHAR(100) NOT NULL,
    nivel VARCHAR(100) NOT NULL,
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: contactos (formulario público)
-- ========================================
CREATE TABLE IF NOT EXISTS contactos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    celular VARCHAR(20) NOT NULL,
    mensaje TEXT DEFAULT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ========================================
-- USUARIO ADMIN POR DEFECTO
-- password: admin123 (bcrypt hash)
-- ¡CAMBIAR EN PRODUCCIÓN!
-- ========================================
INSERT INTO usuarios (email, password_hash, rol) VALUES
('admin@amigo.edu.co', '$2b$12$LJ3m4ys2Ot0ZrKEaUGMGOeKXHzRkOE8pRnKJYq7GvFv8T6N5x1eG', 'admin');
