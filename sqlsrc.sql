CREATE DATABASE IF NOT EXISTS ece1779;
USE ece1779;

CREATE TABLE IF NOT EXISTS `backend_config` (
   `id` int NOT NULL AUTO_INCREMENT,
  `capacity` int NOT NULL,
  `policy` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `key_picture` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(45) DEFAULT NULL,
  `path` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `key_UNIQUE` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;