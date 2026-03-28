-- ========================================
-- SCHEMA COMPLETO: Sistema de Perfiles de Practicantes
-- Universidad Católica Luis Amigó
--
-- IMPORTANTE: Este script crea la BD desde cero.
-- Para poblar los catálogos (habilidades, idiomas, títulos),
-- ejecutar también catalogos.sql después de este script.
-- ========================================

CREATE DATABASE IF NOT EXISTS practicantes_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE practicantes_db;

-- ========================================
-- TABLA: catalogo_titulos
-- ========================================
CREATE TABLE IF NOT EXISTS catalogo_titulos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: catalogo_habilidades
-- ========================================
CREATE TABLE IF NOT EXISTS catalogo_habilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria ENUM('lenguaje', 'framework', 'base_datos', 'herramienta') NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (nombre, categoria)
) ENGINE=InnoDB;

-- ========================================
-- TABLA: catalogo_idiomas
-- ========================================
CREATE TABLE IF NOT EXISTS catalogo_idiomas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: catalogo_programas (programas académicos de la universidad)
-- Se incluye aquí porque perfiles depende de esta tabla.
-- ========================================
CREATE TABLE IF NOT EXISTS catalogo_programas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL UNIQUE,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

INSERT INTO catalogo_programas (nombre) VALUES
('Ingeniería de Sistemas'),
('Tecnología en Desarrollo de Software');

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
    titulo_otro VARCHAR(200) DEFAULT NULL,
    descripcion TEXT DEFAULT NULL,
    foto_url VARCHAR(300) DEFAULT NULL,
    cv_url VARCHAR(300) DEFAULT NULL,
    email_contacto VARCHAR(150) DEFAULT NULL,
    github VARCHAR(255) DEFAULT NULL,
    linkedin VARCHAR(255) DEFAULT NULL,
    estado ENUM('pendiente', 'aprobado', 'rechazado', 'en_revision') NOT NULL DEFAULT 'pendiente',
    comentario_admin TEXT DEFAULT NULL,
    github_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    linkedin_verificado BOOLEAN NOT NULL DEFAULT FALSE,
    programa_id INT DEFAULT NULL,
    semestre_actual TINYINT DEFAULT NULL,
    visitas INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (programa_id) REFERENCES catalogo_programas(id)
) ENGINE=InnoDB;

-- ========================================
-- TABLA: habilidades (vinculadas al catálogo)
-- catalogo_id es la referencia al catálogo dinámico.
-- nombre se mantiene nullable como campo legacy.
-- ========================================
CREATE TABLE IF NOT EXISTS habilidades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    perfil_id INT NOT NULL,
    catalogo_id INT DEFAULT NULL,
    nombre VARCHAR(100) DEFAULT NULL,
    nivel ENUM('basico', 'intermedio', 'avanzado') NOT NULL DEFAULT 'intermedio',
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE,
    FOREIGN KEY (catalogo_id) REFERENCES catalogo_habilidades(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_habilidades_catalogo_id ON habilidades(catalogo_id);

-- ========================================
-- TABLA: formacion (formación académica)
-- ========================================
CREATE TABLE IF NOT EXISTS formacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    perfil_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    institucion VARCHAR(200) NOT NULL,
    anio VARCHAR(20) DEFAULT NULL,
    anio_inicio INT DEFAULT NULL,
    anio_fin INT DEFAULT NULL,
    en_curso BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: idiomas (vinculados al catálogo)
-- catalogo_id es la referencia al catálogo dinámico.
-- idioma se mantiene nullable como campo legacy.
-- ========================================
CREATE TABLE IF NOT EXISTS idiomas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    perfil_id INT NOT NULL,
    catalogo_id INT DEFAULT NULL,
    idioma VARCHAR(100) DEFAULT NULL,
    nivel VARCHAR(100) NOT NULL,
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE,
    FOREIGN KEY (catalogo_id) REFERENCES catalogo_idiomas(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ========================================
-- TABLA: contactos (formulario público de empresas)
-- ========================================
CREATE TABLE IF NOT EXISTS contactos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    empresa VARCHAR(100) NOT NULL,
    correo VARCHAR(100) NOT NULL,
    celular VARCHAR(20) NOT NULL,
    mensaje TEXT DEFAULT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado_contacto ENUM('nuevo', 'contactado', 'en_proceso', 'cerrado') NOT NULL DEFAULT 'nuevo',
    notas_admin TEXT DEFAULT NULL
) ENGINE=InnoDB;

-- ========================================
-- TABLA: contacto_practicantes (relación contacto ↔ perfiles de interés)
-- ========================================
CREATE TABLE IF NOT EXISTS contacto_practicantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contacto_id INT NOT NULL,
    perfil_id INT NOT NULL,
    UNIQUE (contacto_id, perfil_id),
    FOREIGN KEY (contacto_id) REFERENCES contactos(id) ON DELETE CASCADE,
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA: revisiones_campo (revisión campo por campo del perfil)
-- ========================================
CREATE TABLE IF NOT EXISTS revisiones_campo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    perfil_id INT NOT NULL,
    campo VARCHAR(50) NOT NULL,
    estado ENUM('pendiente', 'aprobado', 'rechazado') NOT NULL DEFAULT 'pendiente',
    comentario TEXT DEFAULT NULL,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (perfil_id, campo),
    FOREIGN KEY (perfil_id) REFERENCES perfiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- USUARIO ADMIN POR DEFECTO
-- password: admin123 (bcrypt hash)
-- ¡CAMBIAR EN PRODUCCIÓN!
-- ========================================
INSERT INTO usuarios (email, password_hash, rol) VALUES
('admin@amigo.edu.co', '$2b$12$LJ3m4ys2Ot0ZrKEaUGMGOeKXHzRkOE8pRnKJYq7GvFv8T6N5x1eG', 'admin');
