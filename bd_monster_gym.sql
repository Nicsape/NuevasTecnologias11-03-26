-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: monster gym
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `distribuidor_producto`
--

DROP TABLE IF EXISTS `distribuidor_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `distribuidor_producto` (
  `FK_ID_Distribuidor` int NOT NULL,
  `FK_ID_Producto` int NOT NULL,
  PRIMARY KEY (`FK_ID_Distribuidor`,`FK_ID_Producto`),
  KEY `FK_ID_Producto` (`FK_ID_Producto`),
  CONSTRAINT `distribuidor_producto_ibfk_1` FOREIGN KEY (`FK_ID_Distribuidor`) REFERENCES `usuario` (`ID_Usuario`) ON DELETE CASCADE,
  CONSTRAINT `distribuidor_producto_ibfk_2` FOREIGN KEY (`FK_ID_Producto`) REFERENCES `producto` (`ID_Producto`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `distribuidor_producto`
--

LOCK TABLES `distribuidor_producto` WRITE;
/*!40000 ALTER TABLE `distribuidor_producto` DISABLE KEYS */;
INSERT INTO `distribuidor_producto` VALUES (6,1),(6,2);
/*!40000 ALTER TABLE `distribuidor_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `factura`
--

DROP TABLE IF EXISTS `factura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `factura` (
  `N_Factura` int NOT NULL AUTO_INCREMENT,
  `Pago` decimal(10,2) DEFAULT NULL,
  `FK_ID_Usuario` int DEFAULT NULL,
  PRIMARY KEY (`N_Factura`),
  KEY `FK_ID_Usuario` (`FK_ID_Usuario`),
  CONSTRAINT `factura_ibfk_1` FOREIGN KEY (`FK_ID_Usuario`) REFERENCES `usuario` (`ID_Usuario`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `factura`
--

LOCK TABLES `factura` WRITE;
/*!40000 ALTER TABLE `factura` DISABLE KEYS */;
INSERT INTO `factura` VALUES (1,50.00,2),(2,120.00,3);
/*!40000 ALTER TABLE `factura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario`
--

DROP TABLE IF EXISTS `inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario` (
  `CodigoInv` int NOT NULL AUTO_INCREMENT,
  `FK_ID_Producto` int DEFAULT NULL,
  `Stock` int DEFAULT NULL,
  PRIMARY KEY (`CodigoInv`),
  KEY `FK_ID_Producto` (`FK_ID_Producto`),
  CONSTRAINT `inventario_ibfk_1` FOREIGN KEY (`FK_ID_Producto`) REFERENCES `producto` (`ID_Producto`) ON DELETE CASCADE,
  CONSTRAINT `inventario_chk_1` CHECK ((`Stock` between 0 and 100))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario`
--

LOCK TABLES `inventario` WRITE;
/*!40000 ALTER TABLE `inventario` DISABLE KEYS */;
INSERT INTO `inventario` VALUES (1,1,12),(2,2,6),(3,3,17);
/*!40000 ALTER TABLE `inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maquinas`
--

DROP TABLE IF EXISTS `maquinas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maquinas` (
  `CodigoMaq` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) DEFAULT NULL,
  `Categoria` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`CodigoMaq`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maquinas`
--

LOCK TABLES `maquinas` WRITE;
/*!40000 ALTER TABLE `maquinas` DISABLE KEYS */;
INSERT INTO `maquinas` VALUES (1,'Press Banca','Pecho'),(2,'Sentadilla Libre','Pierna'),(3,'Jalon en Polea','Espalda'),(4,'Curl Predicador','Brazo');
/*!40000 ALTER TABLE `maquinas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `membresia_usuario`
--

DROP TABLE IF EXISTS `membresia_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membresia_usuario` (
  `ID_Membresia` int NOT NULL AUTO_INCREMENT,
  `FK_ID_Usuario` int DEFAULT NULL,
  `FK_ID_Tipo` int DEFAULT NULL,
  `FK_ID_Entrenador` int DEFAULT NULL,
  `Fecha_Inicio` date DEFAULT NULL,
  `Fecha_Fin` date DEFAULT NULL,
  PRIMARY KEY (`ID_Membresia`),
  KEY `FK_ID_Usuario` (`FK_ID_Usuario`),
  KEY `FK_ID_Tipo` (`FK_ID_Tipo`),
  KEY `FK_ID_Entrenador` (`FK_ID_Entrenador`),
  CONSTRAINT `membresia_usuario_ibfk_1` FOREIGN KEY (`FK_ID_Usuario`) REFERENCES `usuario` (`ID_Usuario`) ON DELETE CASCADE,
  CONSTRAINT `membresia_usuario_ibfk_2` FOREIGN KEY (`FK_ID_Tipo`) REFERENCES `tipo_membresia` (`ID_Tipo`) ON DELETE CASCADE,
  CONSTRAINT `membresia_usuario_ibfk_3` FOREIGN KEY (`FK_ID_Entrenador`) REFERENCES `usuario` (`ID_Usuario`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membresia_usuario`
--

LOCK TABLES `membresia_usuario` WRITE;
/*!40000 ALTER TABLE `membresia_usuario` DISABLE KEYS */;
INSERT INTO `membresia_usuario` VALUES (1,2,1,4,'2026-01-01','2026-04-01'),(2,3,2,4,'2026-02-01','2026-08-01');
/*!40000 ALTER TABLE `membresia_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto`
--

DROP TABLE IF EXISTS `producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `producto` (
  `ID_Producto` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) DEFAULT NULL,
  `Categoria` varchar(50) DEFAULT NULL,
  `Precio` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID_Producto`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto`
--

LOCK TABLES `producto` WRITE;
/*!40000 ALTER TABLE `producto` DISABLE KEYS */;
INSERT INTO `producto` VALUES (1,'Proteina','Suplementos',96.00),(2,'Creatina','Suplementos',50.00),(3,'Guantes','Implementos',15.00);
/*!40000 ALTER TABLE `producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rol`
--

DROP TABLE IF EXISTS `rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `rol` (
  `ID_Rol` int NOT NULL AUTO_INCREMENT,
  `Nombre_Rol` varchar(50) NOT NULL,
  PRIMARY KEY (`ID_Rol`),
  UNIQUE KEY `Nombre_Rol` (`Nombre_Rol`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rol`
--

LOCK TABLES `rol` WRITE;
/*!40000 ALTER TABLE `rol` DISABLE KEYS */;
INSERT INTO `rol` VALUES (1,'ADMIN'),(2,'CLIENTE'),(5,'DISTRIBUIDOR'),(3,'ENTRENADOR'),(4,'RECEPCIONISTA');
/*!40000 ALTER TABLE `rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_membresia`
--

DROP TABLE IF EXISTS `tipo_membresia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_membresia` (
  `ID_Tipo` int NOT NULL AUTO_INCREMENT,
  `Plan` varchar(50) DEFAULT NULL,
  `Costo` decimal(10,2) DEFAULT NULL,
  `Duracion_Meses` int DEFAULT NULL,
  PRIMARY KEY (`ID_Tipo`),
  CONSTRAINT `tipo_membresia_chk_1` CHECK ((`Duracion_Meses` between 1 and 12))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_membresia`
--

LOCK TABLES `tipo_membresia` WRITE;
/*!40000 ALTER TABLE `tipo_membresia` DISABLE KEYS */;
INSERT INTO `tipo_membresia` VALUES (1,'Basico',50.00,3),(2,'Premium',120.00,6),(3,'Anual',200.00,12);
/*!40000 ALTER TABLE `tipo_membresia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `ID_Usuario` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Apellido` varchar(50) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Username` varchar(50) NOT NULL,
  `Password_Hash` varchar(255) NOT NULL,
  `Telefono` varchar(15) DEFAULT NULL,
  `Direccion` varchar(100) DEFAULT NULL,
  `Edad` int DEFAULT NULL,
  `Seguro` varchar(50) DEFAULT NULL,
  `Salario` decimal(10,2) DEFAULT NULL,
  `Categoria_Distribuidor` varchar(50) DEFAULT NULL,
  `Fecha_Registro` date DEFAULT NULL,
  `Fecha_Contratacion` date DEFAULT NULL,
  `Activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`ID_Usuario`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `Username` (`Username`),
  CONSTRAINT `usuario_chk_1` CHECK ((`Edad` between 16 and 75))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'Admin','Sistema','admin@gmail.com','admin','$2a$10$DowJonesExampleHash123456789','3001112233','Gym Principal',30,'Sura',NULL,NULL,'2026-01-01',NULL,1),(2,'Carlos','Ramirez','carlos@gmail.com','carlos','$2a$10$DowJonesExampleHash123456789','5551234','Av. Los Pinos 123',25,'Mapfre',NULL,NULL,'2026-01-10',NULL,1),(3,'Maria','Gonzalez','maria@gmail.com','maria','$2a$10$DowJonesExampleHash123456789','5555678','Calle Sol 456',34,'Rimac',NULL,NULL,'2026-01-15',NULL,1),(4,'Diego','Vivas','diego@gmail.com','diego','$2a$10$DowJonesExampleHash123456789','3004445566','Calle 10',32,NULL,2500.00,NULL,NULL,'2022-10-21',1),(5,'Ana','Torres','ana@gmail.com','ana','$2a$10$DowJonesExampleHash123456789','3008889999','Calle 20',28,NULL,1800.00,NULL,NULL,'2023-11-10',1),(6,'Roberto','Gonzales','roberto@gmail.com','roberto','$2a$10$DowJonesExampleHash123456789','3108038760','Zona Industrial',40,NULL,NULL,'Alimentos',NULL,NULL,1);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_inventario`
--

DROP TABLE IF EXISTS `usuario_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_inventario` (
  `FK_ID_Usuario` int NOT NULL,
  `FK_Codigo_Inv` int NOT NULL,
  PRIMARY KEY (`FK_ID_Usuario`,`FK_Codigo_Inv`),
  KEY `FK_Codigo_Inv` (`FK_Codigo_Inv`),
  CONSTRAINT `usuario_inventario_ibfk_1` FOREIGN KEY (`FK_ID_Usuario`) REFERENCES `usuario` (`ID_Usuario`) ON DELETE CASCADE,
  CONSTRAINT `usuario_inventario_ibfk_2` FOREIGN KEY (`FK_Codigo_Inv`) REFERENCES `inventario` (`CodigoInv`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_inventario`
--

LOCK TABLES `usuario_inventario` WRITE;
/*!40000 ALTER TABLE `usuario_inventario` DISABLE KEYS */;
INSERT INTO `usuario_inventario` VALUES (5,1),(5,2),(5,3);
/*!40000 ALTER TABLE `usuario_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_maquina`
--

DROP TABLE IF EXISTS `usuario_maquina`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_maquina` (
  `FK_ID_Usuario` int NOT NULL,
  `FK_Codigo_Maq` int NOT NULL,
  PRIMARY KEY (`FK_ID_Usuario`,`FK_Codigo_Maq`),
  KEY `FK_Codigo_Maq` (`FK_Codigo_Maq`),
  CONSTRAINT `usuario_maquina_ibfk_1` FOREIGN KEY (`FK_ID_Usuario`) REFERENCES `usuario` (`ID_Usuario`) ON DELETE CASCADE,
  CONSTRAINT `usuario_maquina_ibfk_2` FOREIGN KEY (`FK_Codigo_Maq`) REFERENCES `maquinas` (`CodigoMaq`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_maquina`
--

LOCK TABLES `usuario_maquina` WRITE;
/*!40000 ALTER TABLE `usuario_maquina` DISABLE KEYS */;
INSERT INTO `usuario_maquina` VALUES (2,1),(2,2),(3,3);
/*!40000 ALTER TABLE `usuario_maquina` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario_rol`
--

DROP TABLE IF EXISTS `usuario_rol`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario_rol` (
  `FK_ID_Usuario` int NOT NULL,
  `FK_ID_Rol` int NOT NULL,
  PRIMARY KEY (`FK_ID_Usuario`,`FK_ID_Rol`),
  KEY `FK_ID_Rol` (`FK_ID_Rol`),
  CONSTRAINT `usuario_rol_ibfk_1` FOREIGN KEY (`FK_ID_Usuario`) REFERENCES `usuario` (`ID_Usuario`) ON DELETE CASCADE,
  CONSTRAINT `usuario_rol_ibfk_2` FOREIGN KEY (`FK_ID_Rol`) REFERENCES `rol` (`ID_Rol`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario_rol`
--

LOCK TABLES `usuario_rol` WRITE;
/*!40000 ALTER TABLE `usuario_rol` DISABLE KEYS */;
INSERT INTO `usuario_rol` VALUES (1,1),(2,2),(3,2),(4,3),(5,4),(6,5);
/*!40000 ALTER TABLE `usuario_rol` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'monster gym'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-12 19:22:19
