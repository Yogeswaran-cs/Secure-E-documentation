CREATE DATABASE IF NOT EXISTS securedocs;
USE securedocs;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'verifier', 'user') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    status ENUM('Pending', 'Verified', 'Rejected', 'Tampered', 'Duplicate') DEFAULT 'Pending',
    blockchain_tx_id VARCHAR(255) DEFAULT NULL,
    blockchain_timestamp DATETIME DEFAULT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logins Table
CREATE TABLE IF NOT EXISTS logins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_identifier VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert Default Seed Users
INSERT IGNORE INTO users (username, password, role) VALUES 
('admin', 'admin123', 'admin'),
('mehul', 'verifier123', 'verifier'),
('123456789012', 'user123', 'user');