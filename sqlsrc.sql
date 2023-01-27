CREATE DATABASE ece1779;

USE ece1779;

CREATE TABLE `backend_config` (
  `capacity` int NOT NULL,
  `policy` varchar(45) NOT NULL,
  PRIMARY KEY (`capacity`),
  UNIQUE KEY `capacity_UNIQUE` (`capacity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `backend_statistic` (
  `timestamp` DATETIME NOT NULL,
  `hit` int unsigned DEFAULT NULL,
  `miss` int unsigned DEFAULT NULL,
  `size` int unsigned DEFAULT NULL,
  `picture_count` int unsigned DEFAULT NULL,
  `request_count` int unsigned DEFAULT NULL,
  PRIMARY KEY (`timestamp`),
  UNIQUE KEY `timestamp_UNIQUE` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `key_picture` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(45) DEFAULT NULL,
  `path` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `key_UNIQUE` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;