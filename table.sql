CREATE TABLE tasks (
    id VARCHAR(10) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    closed_at TIMESTAMP NULL,
    status ENUM('creada', 'en proceso', 'en espera', 'cancelado', 'terminado') DEFAULT 'creada'
);