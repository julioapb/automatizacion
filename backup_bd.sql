/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.13-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: flaskapp
-- ------------------------------------------------------
-- Server version	10.11.13-MariaDB-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id_cliente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `no_documento` varchar(50) NOT NULL,
  `direccion` varchar(150) DEFAULT NULL,
  `ciudad` varchar(100) DEFAULT NULL,
  `cp` varchar(10) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES
(1,'kartsana ','B58295536','C/ Narcís Monturiol, 34','Sant Quirze del vallés','08192','93 715 86 72','compras@kartsana.com'),
(2,'Novolux','B84333582','C/Ramon Berenguer, 8','SANTA PEPETUA DE MOGODA','08130','93 274 52 66','info@gruponovolux.com'),
(3,'BOVER','B61219333','Avda. Catalunya, 173','CARDEDEU','08440','93 871 31 52','admin@bover.es'),
(4,'BENSENY','A58538588','PG IND PEDREGAR , 1','MONTMELO','08160','935687080','benseny@benseny.com'),
(5,'SHAD','B78180239','C/ Octavio Lecante, 2-6','MOLLET DEL VALLES','08100','93 579 58 60','maria.vela@shad.es'),
(6,'DIMASA','B65512766','C/Santa Rita, nº 19','Sant Fost de Campsentelles','08105','93 462 06 04','vgarcia@dimasa.es'),
(7,'CAFOR','A58084781','Passeig de la Riera, 35 E','TEIÀ','08329','93 555 33 06','qualitat@cafor.com'),
(8,'INMESA','B64367162','C/Torrent d\'Estadella,  56-58','BARCELONA','08030','93 345 59 60','aosma@inmesa.com'),
(9,'FERROMER','B63018535','C/Anoia 1 Pol.Ind.Bernades-Subira','SANTA PERPETUA DE MOGODA','08130','93 713 33 80','patri@ferromer.com');
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `color`
--

DROP TABLE IF EXISTS `color`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `color` (
  `id_color` int(11) NOT NULL AUTO_INCREMENT,
  `codigo_color` varchar(20) NOT NULL,
  `codigo_html` varchar(11) NOT NULL,
  `nombre_color` varchar(50) NOT NULL,
  PRIMARY KEY (`id_color`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `color`
--

LOCK TABLES `color` WRITE;
/*!40000 ALTER TABLE `color` DISABLE KEYS */;
INSERT INTO `color` VALUES
(1,'prb','#c52020','rojo'),
(2,'LIMA','#a3ff1a','LIMA'),
(3,'ROJO','#ff0000','ROJO'),
(4,'NOIR 100','#474343','NOIR 100'),
(5,'NEGRO','#000000','NEGRO'),
(6,'GRIS 9006','#a7a8b9','GRIS 9006'),
(7,'AZUL 5002','#2059df','AZUL 5002'),
(8,'GRIS METAL','#b3b1c8','GRIS METAL'),
(9,'NOIR 2 CAP','#7d7878','NOIR 2 CAP'),
(10,'BLANCO LAC','#ffffff','BLANCO LAC');
/*!40000 ALTER TABLE `color` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `colores`
--

DROP TABLE IF EXISTS `colores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `colores` (
  `id_color` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `codigo_color` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `colores`
--

LOCK TABLES `colores` WRITE;
/*!40000 ALTER TABLE `colores` DISABLE KEYS */;
/*!40000 ALTER TABLE `colores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_servicio`
--

DROP TABLE IF EXISTS `pedido_servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_servicio` (
  `id_pedido_servicio` int(11) NOT NULL AUTO_INCREMENT,
  `id_pedido` int(11) NOT NULL,
  `id_servicio` int(11) NOT NULL,
  `id_color` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `descuento` decimal(10,2) DEFAULT 0.00,
  `neto` decimal(10,2) GENERATED ALWAYS AS (`cantidad` * `precio_unitario` - `descuento`) STORED,
  `fecha_recepcion` date NOT NULL,
  PRIMARY KEY (`id_pedido_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_servicio`
--

LOCK TABLES `pedido_servicio` WRITE;
/*!40000 ALTER TABLE `pedido_servicio` DISABLE KEYS */;
INSERT INTO `pedido_servicio` VALUES
(1,1,2,1,1,1.00,0.00,1.00,'2025-11-17'),
(2,2,3,1,1,0.01,0.00,0.01,'2025-11-19'),
(3,2,11,2,1,0.01,0.00,0.01,'2025-11-06'),
(4,2,20,9,1,0.01,0.00,0.01,'2025-11-26');
/*!40000 ALTER TABLE `pedido_servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `id_pedido` int(11) NOT NULL AUTO_INCREMENT,
  `numero_pedido` varchar(50) NOT NULL,
  `id_cliente` int(11) NOT NULL,
  `fecha_pedido` date NOT NULL,
  `fecha_entrega` date NOT NULL,
  `usuario` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_pedido`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES
(1,'123',1,'2025-11-17','1111-12-12','admin'),
(2,'25-6057',1,'2025-11-19','2025-11-04','admin');
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `servicio`
--

DROP TABLE IF EXISTS `servicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `servicio` (
  `id_servicio` int(11) NOT NULL AUTO_INCREMENT,
  `referencia` varchar(50) NOT NULL,
  `descripcion` varchar(255) NOT NULL,
  `articulos_por_caja` int(10) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `id_cliente` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_servicio`),
  KEY `idx_id_cliente` (`id_cliente`),
  CONSTRAINT `fk_servicio_cliente` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=259 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `servicio`
--

LOCK TABLES `servicio` WRITE;
/*!40000 ALTER TABLE `servicio` DISABLE KEYS */;
INSERT INTO `servicio` VALUES
(3,'50-1540','50-1540',1,1.00,NULL),
(4,'50-1542','50-1542',1,1.00,NULL),
(5,'50-1543','50-1543',1,1.00,NULL),
(6,'50-1545','50-1545',1,1.00,NULL),
(7,'50-1557','50-1557',1,1.00,NULL),
(8,'50-1561','50-1561',1,1.00,NULL),
(9,'50-1563','50-1563',1,1.00,NULL),
(10,'50-1564','50-1564',1,1.00,NULL),
(11,'52-0328','52-0328',1,1.00,NULL),
(12,'52-0457','52-0457',1,1.00,NULL),
(13,'52-0473','52-0473',1,1.00,NULL),
(14,'52-1131','52-1131',1,1.00,NULL),
(15,'52-1132','52-1132',1,1.00,NULL),
(16,'52-1133','52-1133',1,1.00,NULL),
(17,'52-1219','52-1219',1,1.00,NULL),
(18,'52-1240','52-1240',1,1.00,NULL),
(19,'50-0559','50-0559',1,1.00,NULL),
(20,'50-0561','50-0561',1,1.00,NULL),
(21,'50-0562','50-0562',1,1.00,NULL),
(22,'50-0565','50-0565',1,1.00,NULL),
(23,'50-0590','50-0590',1,1.00,NULL),
(24,'50-0593','50-0593',1,1.00,NULL),
(25,'50-0595','50-0595',1,1.00,NULL),
(26,'50-0606','50-0606',1,1.00,NULL),
(27,'50-0607','50-0607',1,1.00,NULL),
(28,'50-0608','50-0608',1,1.00,NULL),
(29,'50-0613','50-0613',1,1.00,NULL),
(30,'50-0615','50-0615',1,1.00,NULL),
(31,'50-0616','50-0616',1,1.00,NULL),
(32,'50-0617','50-0617',1,1.00,NULL),
(33,'50-0618','50-0618',1,1.00,NULL),
(34,'50-0619','50-0619',1,1.00,NULL),
(35,'50-0620','50-0620',1,1.00,NULL),
(36,'50-0622','50-0622',1,1.00,NULL),
(37,'50-0651','50-0651',1,1.00,NULL),
(38,'50-0652','50-0652',1,1.00,NULL),
(39,'50-0653','50-0653',1,1.00,NULL),
(40,'50-0660','50-0660',1,1.00,NULL),
(41,'50-0685','50-0685',1,1.00,NULL),
(42,'50-0695','50-0695',1,1.00,NULL),
(43,'50-0697','50-0697',1,1.00,NULL),
(44,'50-0699','50-0699',1,1.00,NULL),
(45,'50-0705','50-0705',1,1.00,NULL),
(46,'50-0712','50-0712',1,1.00,NULL),
(47,'50-0735','50-0735',1,1.00,NULL),
(48,'50-0736','50-0736',1,1.00,NULL),
(49,'50-0738','50-0738',1,1.00,NULL),
(50,'50-0756','50-0756',1,1.00,NULL),
(51,'50-0798','50-0798',1,1.00,NULL),
(52,'50-0803','50-0803',1,1.00,NULL),
(53,'50-0808','50-0808',1,1.00,NULL),
(54,'50-0859','50-0859',1,1.00,NULL),
(55,'50-0860','50-0860',1,1.00,NULL),
(56,'50-0862','50-0862',1,1.00,NULL),
(57,'50-0865','50-0865',1,1.00,NULL),
(58,'50-0870','50-0870',1,1.00,NULL),
(61,'50-0871','50-0871',1,1.00,NULL),
(62,'50-0878','50-0878',1,1.00,NULL),
(63,'50-0881','50-0881',1,1.00,NULL),
(64,'50-0883','50-0883',1,1.00,NULL),
(65,'50-0884','50-0884',1,1.00,NULL),
(66,'50-0885','50-0885',1,1.00,NULL),
(67,'50-0887','50-0887',1,1.00,NULL),
(68,'50-0888','50-0888',1,1.00,NULL),
(69,'50-0903','50-0903',1,1.00,NULL),
(70,'50-0915','50-0915',1,1.00,NULL),
(71,'50-0916','50-0916',1,1.00,NULL),
(72,'50-1067','50-1067',1,1.00,NULL),
(73,'50-1074','50-1074',1,1.00,NULL),
(74,'50-1075','50-1075',1,1.00,NULL),
(75,'50-1529','50-1529',1,1.00,NULL),
(76,'50-1530','50-1530',1,1.00,NULL),
(77,'01-0003','01-0003',1,1.00,NULL),
(78,'01-0104','01-0104',1,1.00,NULL),
(79,'01-0125','01-0125',1,1.00,NULL),
(80,'01-0129','01-0129',1,1.00,NULL),
(81,'01-0132','01-0132',1,1.00,NULL),
(82,'01-0159','01-0159',1,1.00,NULL),
(83,'01-0185','01-0185',1,1.00,NULL),
(84,'01-0242','01-0242',1,1.00,NULL),
(85,'01-0254','01-0254',1,1.00,NULL),
(86,'01-0259','01-0259',1,1.00,NULL),
(87,'01-0269','01-0269',1,1.00,NULL),
(88,'01-0292','01-0292',1,1.00,NULL),
(89,'01-0293','01-0293',1,1.00,NULL),
(90,'01-0294','01-0294',1,1.00,NULL),
(91,'01-0295','01-0295',1,1.00,NULL),
(92,'01-0337','01-0337',1,1.00,NULL),
(93,'01-0400','01-0400',1,1.00,NULL),
(94,'01-0406','01-0406',1,1.00,NULL),
(95,'01-0407','01-0407',1,1.00,NULL),
(96,'01-0408','01-0408',1,1.00,NULL),
(97,'01-0415','01-0415',1,1.00,NULL),
(98,'01-0419','01-0419',1,1.00,NULL),
(99,'01-0918','01-0918',1,1.00,NULL),
(100,'01-1263','01-1263',1,1.00,NULL),
(101,'03-0119','03-0119',1,1.00,NULL),
(102,'03-0619','03-0619',1,1.00,NULL),
(103,'03-0627','03-0627',1,1.00,NULL),
(104,'03-0750','03-0750',1,1.00,NULL),
(105,'03-0817','03-0817',1,1.00,NULL),
(106,'03-0922','03-0922',1,1.00,NULL),
(107,'03-1061','03-1061',1,1.00,NULL),
(108,'03-1182','03-1882',1,1.00,NULL),
(109,'03-1223','03-1223',1,1.00,NULL),
(110,'03-1224','03-1224',1,1.00,NULL),
(111,'03-1309','03-1309',1,1.00,NULL),
(112,'03-1310','03-1310',1,1.00,NULL),
(113,'03-1311','03-1311',1,1.00,NULL),
(114,'03-1330','03-1330',1,1.00,NULL),
(115,'03-1331','03-1331',1,1.00,NULL),
(116,'03-1339','03-1339',1,1.00,NULL),
(117,'03-1336','03-1336',1,1.00,NULL),
(118,'03-1367','03-1367',1,1.00,NULL),
(119,'03-1393','03-1393',1,1.00,NULL),
(120,'03-1413','03-1413',1,1.00,NULL),
(121,'03-1414','03-1414',1,1.00,NULL),
(122,'03-1418','03-1418',1,1.00,NULL),
(123,'03-1419','03-1419',1,1.00,NULL),
(124,'11-0042','11-0042',1,1.00,NULL),
(125,'11-0129','11-0129',1,1.00,NULL),
(126,'11-0155','11-0155',1,1.00,NULL),
(127,'11-210','11-210',1,1.00,NULL),
(128,'11-0276','11-0276',1,1.00,NULL),
(129,'11-0363','11-0363',1,1.00,NULL),
(130,'11-0408','11-0408',1,1.00,NULL),
(131,'11-0414','11-0414',1,1.00,NULL),
(132,'11-0650','11-0650',1,1.00,NULL),
(133,'11-0661','11-0661',1,1.00,NULL),
(134,'11-0666','11-0666',1,1.00,NULL),
(135,'11-0671','11-0671',1,1.00,NULL),
(136,'11-0688','11-0688',1,1.00,NULL),
(137,'11-0689','11-0689',1,1.00,NULL),
(138,'11-0703','11-0703',1,1.00,NULL),
(139,'11-0705','11-0705',1,1.00,NULL),
(140,'11-0713','11-0713',1,1.00,NULL),
(141,'11-0734','11-0734',1,1.00,NULL),
(142,'11-0913','11-0913',1,1.00,NULL),
(143,'11-0918','11-0918',1,1.00,NULL),
(144,'11-1038','11-1038',1,1.00,NULL),
(145,'11-1076','11-1076',1,1.00,NULL),
(146,'11-1262','11-1262',1,1.00,NULL),
(147,'11-1264','11-1264',1,1.00,NULL),
(148,'11-1314','11-1314',1,1.00,NULL),
(149,'11-1366','11-1366',1,1.00,NULL),
(150,'11-1414','11-1414',1,1.00,NULL),
(151,'11-1483','11-1483',1,1.00,NULL),
(152,'11-1487','11-1487',1,1.00,NULL),
(153,'11-1540','11-1540',1,1.00,NULL),
(154,'11-1577','11-1577',1,1.00,NULL),
(155,'11-1580','11-1580',1,1.00,NULL),
(156,'11-1581','11-1581',1,1.00,NULL),
(157,'11-1663','11-1663',1,1.00,NULL),
(158,'11-1664','11-1664',1,1.00,NULL),
(159,'11-1676','11-1676',1,1.00,NULL),
(160,'11-1709','11-1709',1,1.00,NULL),
(161,'11-1800','11-1800',1,1.00,NULL),
(162,'11-1821','11-1821',1,1.00,NULL),
(163,'11-1824','11-1824',1,1.00,NULL),
(164,'11-1831','11-1831',1,1.00,NULL),
(165,'11-1904','11-1904',1,1.00,NULL),
(166,'11-1913','11-1913',1,1.00,NULL),
(167,'11-1922','11-1922',1,1.00,NULL),
(168,'11-1926','11-1926',1,1.00,NULL),
(169,'11-1940','11-1940',1,1.00,NULL),
(170,'11-1941','11-1941',1,1.00,NULL),
(171,'11-1961','11-1961',1,1.00,NULL),
(172,'11-1963','11-1963',1,1.00,NULL),
(173,'11-1964','11-1964',1,1.00,NULL),
(174,'11-1965','11-1965',1,1.00,NULL),
(175,'11-1970','11-1970',1,1.00,NULL),
(176,'11-2007','11-2007',1,1.00,NULL),
(177,'11-2019','11-2019',1,1.00,NULL),
(178,'11-2028','11-2028',1,1.00,NULL),
(179,'12-0720','12-0720',1,1.00,NULL),
(180,'12-0910','12-0910',1,1.00,NULL),
(181,'12-0911','12-0911',1,1.00,NULL),
(182,'30-0003','30-0003',1,1.00,NULL),
(183,'30-0449','30-0449',1,1.00,NULL),
(184,'30-0620','30-0620',1,1.00,NULL),
(185,'30-0627','30-0627',1,1.00,NULL),
(186,'50-0017','50-0017',1,1.00,NULL),
(187,'50-0039','50-0039',1,1.00,NULL),
(188,'50-0040','50-0040',1,1.00,NULL),
(189,'50-0121','50-0121',1,1.00,NULL),
(190,'50-0125','50-0125',1,1.00,NULL),
(191,'50-0126','50-0126',1,1.00,NULL),
(192,'50-0127','50-0127',1,1.00,NULL),
(193,'50-0129','50-0129',1,1.00,NULL),
(194,'50-0130','50-0130',1,1.00,NULL),
(195,'50-0268','50-0268',1,1.00,NULL),
(196,'50-0331','50-0331',1,1.00,NULL),
(197,'50-0334','50-0334',1,1.00,NULL),
(198,'50-0335','50-0335',1,1.00,NULL),
(199,'50-0336','50-0336',1,1.00,NULL),
(200,'50-0337','50-0337',1,1.00,NULL),
(201,'50-0339','50-0339',1,1.00,NULL),
(217,'50-0392','50-0392',1,1.00,NULL),
(218,'50-0417','50-0417',1,1.00,NULL),
(219,'50-0418','50-0418',1,1.00,NULL),
(220,'50-0419','50-0419',1,1.00,NULL),
(221,'50-0420','50-0420',1,1.00,NULL),
(222,'50-0435','50-0435',1,1.00,NULL),
(223,'50-0442','50-0442',1,1.00,NULL),
(224,'50-0452','50-0452',1,1.00,NULL),
(225,'50-0456','50-0456',1,1.00,NULL),
(226,'50-0490','50-0490',1,1.00,NULL),
(227,'50-0492','50-0492',1,1.00,NULL),
(228,'50-0352','50-0352',1,1.00,NULL),
(229,'50-0537','50-0357',1,1.00,NULL),
(230,'50-0557','50-0557',1,1.00,NULL),
(231,'50-0392','50-0392',1,1.00,NULL),
(232,'50-0417','50-0417',1,1.00,NULL),
(233,'50-0418','50-0418',1,1.00,NULL),
(234,'50-0419','50-0419',1,1.00,NULL),
(235,'50-0420','50-0420',1,1.00,NULL),
(236,'50-0435','50-0435',1,1.00,NULL),
(237,'50-0442','50-0442',1,1.00,NULL),
(238,'50-0452','50-0452',1,1.00,NULL),
(239,'50-0456','50-0456',1,1.00,NULL),
(240,'50-0490','50-0490',1,1.00,NULL),
(241,'50-0492','50-0492',1,1.00,NULL),
(242,'50-0532','50-0532',1,1.00,NULL),
(243,'50-0537','50-0537',1,1.00,NULL),
(244,'50-0557','50-0557',1,1.00,NULL),
(245,'01-0102','01-0102',1,1.00,NULL),
(246,'01-0103','01-0103',1,1.00,NULL),
(247,'50-0661','50-0661',1,1.00,NULL),
(248,'50-0663','50-0663',1,1.00,NULL),
(249,'50-0662','50-0662',1,1.00,NULL),
(250,'50-0692','50-0692',1,1.00,NULL),
(251,'50-0713','50-0713',1,1.00,NULL),
(252,'50-0785','50-0785',1,1.00,NULL),
(253,'50-0863','50-0863',1,1.00,NULL),
(254,'50-0864','50-0864',1,1.00,NULL),
(255,'50-0866','50-0866',1,1.00,NULL),
(256,'50-1547','50-1547',1,1.00,NULL),
(257,'52-0032','52-0032',1,1.00,NULL),
(258,'52-0397','52-0397',1,1.00,NULL);
/*!40000 ALTER TABLE `servicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `usuario` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_spanish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,'admin','S3g5rid4d++','2025-09-20 10:37:19');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-09 17:01:46
