-- MySQL dump 10.13  Distrib 5.5.35, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: koseki
-- ------------------------------------------------------
-- Server version	5.5.35-0+wheezy1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `fee`
--

DROP TABLE IF EXISTS `fee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fee` (
  `fid` int(11) NOT NULL AUTO_INCREMENT,
  `uid` int(11) DEFAULT NULL,
  `registered_by` int(11) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `registered` datetime DEFAULT NULL,
  `start` datetime DEFAULT NULL,
  `end` datetime DEFAULT NULL,
  PRIMARY KEY (`fid`),
  KEY `uid` (`uid`),
  KEY `registered_by` (`registered_by`)
) ENGINE=MyISAM AUTO_INCREMENT=94 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fee`
--

LOCK TABLES `fee` WRITE;
/*!40000 ALTER TABLE `fee` DISABLE KEYS */;
INSERT INTO `fee` VALUES (87,64,13,100,'2014-02-26 15:43:27','2013-12-03 00:00:00','2014-12-03 00:00:00'),(86,13,13,100,'2014-02-25 17:50:22','2014-02-01 00:00:00','2015-02-01 00:00:00'),(85,14,13,100,'2014-02-25 17:49:22','2014-02-01 00:00:00','2015-02-01 00:00:00'),(84,49,1,100,'2014-02-22 13:55:12','2013-11-13 00:00:00','2014-11-13 00:00:00'),(83,64,1,100,'2014-02-21 13:01:00','2012-12-03 00:00:00','2013-12-03 00:00:00'),(29,9,1,100,'2014-02-20 23:52:57','2014-02-07 00:00:00','2015-02-07 00:00:00'),(28,8,1,100,'2014-02-20 23:52:43','2014-02-03 00:00:00','2015-02-03 00:00:00'),(27,7,1,100,'2014-02-20 23:52:24','2014-01-30 00:00:00','2015-01-30 00:00:00'),(26,6,1,100,'2014-02-20 23:52:09','2014-01-30 00:00:00','2015-01-30 00:00:00'),(25,5,1,100,'2014-02-20 23:51:55','2014-01-29 00:00:00','2015-01-29 00:00:00'),(24,4,1,100,'2014-02-20 23:51:39','2014-01-28 00:00:00','2015-01-28 00:00:00'),(23,3,1,100,'2014-02-20 23:51:14','2014-01-24 00:00:00','2015-01-24 00:00:00'),(30,10,1,100,'2014-02-20 23:53:09','2014-02-07 00:00:00','2015-02-07 00:00:00'),(31,31,1,50,'2014-02-21 00:02:09','2013-06-06 00:00:00','2013-12-05 00:00:00'),(32,32,1,100,'2014-02-21 00:02:34','2013-06-06 00:00:00','2014-06-06 00:00:00'),(33,33,1,100,'2014-02-21 00:02:53','2013-06-13 00:00:00','2014-06-13 00:00:00'),(34,34,1,50,'2014-02-21 00:03:18','2013-06-25 00:00:00','2013-12-24 00:00:00'),(35,35,1,50,'2014-02-21 00:03:51','2013-08-26 00:00:00','2014-02-24 00:00:00'),(36,36,1,50,'2014-02-21 00:04:14','2013-08-30 00:00:00','2014-02-28 00:00:00'),(37,37,1,50,'2014-02-21 00:04:27','2013-08-30 00:00:00','2014-02-28 00:00:00'),(38,38,1,100,'2014-02-21 00:05:00','2013-08-30 00:00:00','2014-08-30 00:00:00'),(39,39,1,100,'2014-02-21 00:05:14','2013-08-30 00:00:00','2014-08-30 00:00:00'),(40,40,1,100,'2014-02-21 00:05:30','2013-09-02 00:00:00','2014-09-02 00:00:00'),(41,41,1,100,'2014-02-21 00:05:52','2013-09-04 00:00:00','2014-09-04 00:00:00'),(42,42,1,100,'2014-02-21 00:06:05','2013-09-04 00:00:00','2014-09-04 00:00:00'),(43,43,1,50,'2014-02-21 00:06:24','2013-09-05 00:00:00','2014-03-06 00:00:00'),(44,44,1,100,'2014-02-21 00:06:42','2013-09-17 00:00:00','2014-09-17 00:00:00'),(45,45,1,100,'2014-02-21 00:06:55','2013-09-27 00:00:00','2014-09-27 00:00:00'),(46,46,1,100,'2014-02-21 00:07:09','2013-10-04 00:00:00','2014-10-04 00:00:00'),(47,2,1,100,'2014-02-21 00:07:36','2013-10-16 00:00:00','2014-10-16 00:00:00'),(48,11,1,100,'2014-02-21 00:07:54','2013-10-20 00:00:00','2014-10-20 00:00:00'),(49,47,1,100,'2014-02-21 00:08:07','2013-11-13 00:00:00','2014-11-13 00:00:00'),(50,48,1,100,'2014-02-21 00:08:24','2013-11-13 00:00:00','2014-11-13 00:00:00'),(51,12,1,100,'2014-02-21 00:08:38','2013-11-13 00:00:00','2014-11-13 00:00:00'),(52,51,1,100,'2014-02-21 00:09:04','2013-11-13 00:00:00','2014-11-13 00:00:00'),(53,21,1,50,'2014-02-21 00:09:37','2013-11-13 00:00:00','2014-05-14 00:00:00'),(54,1,1,100,'2014-02-21 00:09:53','2013-11-13 00:00:00','2014-11-13 00:00:00'),(55,52,1,100,'2014-02-21 00:10:06','2013-11-15 00:00:00','2014-11-15 00:00:00'),(56,53,1,100,'2014-02-21 00:10:24','2013-11-22 00:00:00','2014-11-22 00:00:00'),(57,54,1,100,'2014-02-21 00:10:46','2013-11-25 00:00:00','2014-11-25 00:00:00'),(58,55,1,50,'2014-02-21 00:11:02','2013-11-26 00:00:00','2014-05-27 00:00:00'),(59,56,1,50,'2014-02-21 00:11:18','2013-11-26 00:00:00','2014-05-27 00:00:00'),(60,57,1,100,'2014-02-21 00:11:36','2013-11-27 00:00:00','2014-11-27 00:00:00'),(61,58,1,100,'2014-02-21 00:11:45','2013-12-03 00:00:00','2014-12-03 00:00:00'),(62,59,1,100,'2014-02-21 00:12:00','2013-12-04 00:00:00','2014-12-04 00:00:00'),(63,60,1,100,'2014-02-21 00:12:12','2013-12-06 00:00:00','2014-12-06 00:00:00'),(64,61,1,100,'2014-02-21 00:12:27','2013-12-06 00:00:00','2014-12-06 00:00:00'),(65,13,1,100,'2014-02-21 00:13:43','2013-02-01 00:00:00','2014-02-01 00:00:00'),(66,14,1,100,'2014-02-21 00:13:55','2013-02-01 00:00:00','2014-02-01 00:00:00'),(67,15,1,100,'2014-02-21 00:14:07','2013-02-20 00:00:00','2014-02-20 00:00:00'),(68,16,1,100,'2014-02-21 00:14:23','2013-03-05 00:00:00','2014-03-05 00:00:00'),(69,17,1,100,'2014-02-21 00:14:39','2013-03-20 00:00:00','2014-03-20 00:00:00'),(70,18,1,100,'2014-02-21 00:14:54','2013-04-03 00:00:00','2014-04-03 00:00:00'),(71,19,1,100,'2014-02-21 00:15:09','2013-04-08 00:00:00','2014-04-08 00:00:00'),(72,20,1,100,'2014-02-21 00:15:22','2013-04-09 00:00:00','2014-04-09 00:00:00'),(73,21,1,50,'2014-02-21 00:15:47','2013-04-10 00:00:00','2013-10-09 00:00:00'),(74,22,1,100,'2014-02-21 00:15:59','2013-04-17 00:00:00','2014-04-17 00:00:00'),(75,23,1,100,'2014-02-21 00:16:13','2013-04-17 00:00:00','2014-04-17 00:00:00'),(76,24,1,50,'2014-02-21 00:16:31','2013-04-26 00:00:00','2013-10-25 00:00:00'),(77,25,1,50,'2014-02-21 00:16:49','2013-04-26 00:00:00','2013-10-25 00:00:00'),(78,26,1,100,'2014-02-21 00:17:04','2013-04-28 00:00:00','2014-04-28 00:00:00'),(79,27,1,100,'2014-02-21 00:17:23','2013-05-10 00:00:00','2014-05-10 00:00:00'),(80,28,1,100,'2014-02-21 00:17:39','2013-05-15 00:00:00','2014-05-15 00:00:00'),(81,29,1,100,'2014-02-21 00:17:51','2013-05-15 00:00:00','2014-05-15 00:00:00'),(82,30,1,100,'2014-02-21 00:18:01','2013-05-15 00:00:00','2014-05-15 00:00:00'),(88,65,13,100,'2014-02-26 15:43:58','2014-02-26 15:43:58','2015-02-26 15:43:58'),(89,21,13,50,'2014-02-26 15:44:09','2014-05-14 00:00:00','2014-11-12 12:00:00'),(90,68,13,100,'2014-03-03 15:49:52','2014-03-03 15:49:52','2015-03-03 15:49:52'),(91,67,13,100,'2014-03-03 15:50:03','2014-03-03 15:50:03','2015-03-03 15:50:03'),(92,18,13,100,'2014-03-03 19:37:11','2014-04-03 00:00:00','2015-04-03 00:00:00'),(93,70,11,50,'2014-03-04 13:52:47','2014-03-04 13:52:47','2014-09-03 01:52:47');
/*!40000 ALTER TABLE `fee` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `group`
--

DROP TABLE IF EXISTS `group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group` (
  `gid` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) COLLATE utf8_unicode_ci DEFAULT NULL,
  `descr` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`gid`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `group`
--

LOCK TABLES `group` WRITE;
/*!40000 ALTER TABLE `group` DISABLE KEYS */;
INSERT INTO `group` VALUES (1,'admin','System Administrator'),(2,'enroll','Allow enrolling new members'),(3,'accounter','Allow registering fees'),(4,'board','Allow enrolling and browsing'),(7,'ordf','Ordforande'),(8,'vordf','Vice ordforande'),(9,'sekr','Sekreterare'),(10,'krangare','Krangare'),(11,'m3','M3'),(12,'revisor','Revisor'),(13,'ddg','DDG'),(14,'pr','PR/Webb-ansvarig');
/*!40000 ALTER TABLE `group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person`
--

DROP TABLE IF EXISTS `person`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `person` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `state` enum('pending','active','expired') COLLATE utf8_unicode_ci DEFAULT NULL,
  `fname` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `lname` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `email` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `stil` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `password` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `enrolled` datetime DEFAULT NULL,
  `lchange` datetime DEFAULT NULL,
  `enrolled_by` int(11) DEFAULT NULL,
  PRIMARY KEY (`uid`),
  KEY `enrolled_by` (`enrolled_by`)
) ENGINE=MyISAM AUTO_INCREMENT=72 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person`
--

LOCK TABLES `person` WRITE;
/*!40000 ALTER TABLE `person` DISABLE KEYS */;
INSERT INTO `person` VALUES (1,'active','Fredrik','Ahlberg','fredrik@z80.se','ael09fah','10e21d1b794002ca4113540e3605a8c461d61474','2013-11-13 15:43:05','2013-11-13 15:43:05',NULL),(2,'active','Christoffer','Lundgren','mail@christofferlundgren.se','atf10clu',NULL,'2014-02-20 13:58:09','2014-02-20 13:58:09',1),(3,'active','Viktor','Petersson','elt11vpe@student.lu.se','elt11vpe',NULL,'2014-02-20 14:27:58','2014-02-20 14:27:58',2),(4,'active','Filip','Svensson','adi10fsv@student.lu.se','adi10fsv',NULL,'2014-02-20 14:29:02','2014-02-20 14:29:02',2),(5,'active','Isak','Monrad-Aas','elt13imo@student.lu.se','elt13imo',NULL,'2014-02-20 14:29:29','2014-02-20 14:29:29',2),(6,'active','Alexander','Johansson','alex@neco.eu.com','',NULL,'2014-02-20 14:29:52','2014-02-20 14:29:52',2),(7,'active','Emil','RosÃ©n','emil@neco.eu.com','',NULL,'2014-02-20 14:30:18','2014-02-20 14:30:18',2),(8,'active','Housam','Elfeituri','elfeituri@gmail.com','awi10hel',NULL,'2014-02-20 14:30:47','2014-02-20 14:30:47',2),(9,'active','Christoffer','Cederberg','christoffer.ceder@gmail.com','cie06cce',NULL,'2014-02-20 14:31:09','2014-02-20 14:31:09',2),(10,'active','BjÃ¶rn','Wictorin','bjorn.wictorin@gmail.com','lak12bwi',NULL,'2014-02-20 14:31:29','2014-02-20 14:31:29',2),(11,'active','Ludvig','NybogÃ¥rd','ludvig@nybogard.nu','elt11lny',NULL,'2014-02-20 14:37:16','2014-02-20 14:37:16',2),(12,'active','Hampus','Paulsson','paulsson.hampus@gmail.com','elt11hpa',NULL,'2014-02-20 14:38:59','2014-02-20 14:38:59',2),(13,'active','Oskar','Persson','oskar.nh.persson@gmail.com','ama09ope',NULL,'2014-02-20 14:39:36','2014-02-20 14:39:36',2),(14,'active','Jesper','Hasselquist','psy08jh2@gmail.com','psy08jh2',NULL,'2014-02-20 15:10:19','2014-02-20 15:10:19',2),(15,'expired','Mats','Granholm','mats_granholm@hotmail.com','elt12mgr',NULL,'2014-02-20 15:10:38','2014-02-20 15:10:38',2),(16,'expired','Peter','Polfeldt','peter@ehuset.lth.se','',NULL,'2014-02-20 15:10:56','2014-02-20 15:10:56',2),(17,'active','Gabriel','JÃ¶nsson','joenssongabriel@gmail.com','ael10gjo',NULL,'2014-02-20 15:11:21','2014-02-20 15:11:21',2),(18,'active','Andreas','IrestÃ¥l','andreas@irestal.se','dt07ac9',NULL,'2014-02-20 15:11:40','2014-02-20 15:11:40',2),(19,'active','David','Pettersson','davi_d102@hotmail.com','ael10dpe',NULL,'2014-02-20 15:12:22','2014-02-20 15:12:22',2),(20,'active','John','Kroon','john.e.kroon@gmail.com','mat10jk1',NULL,'2014-02-20 15:12:35','2014-02-20 15:12:35',2),(21,'active','Per','Johnsson','per.johnsson@hotmail.com','ael10pjo',NULL,'2014-02-20 15:12:49','2014-02-20 15:12:49',2),(22,'active','Kajsa','Eriksson Rosenqvist','zba09ker@student.lu.se','zba09ker',NULL,'2014-02-20 15:13:02','2014-02-20 15:13:02',2),(23,'active','Alexander','Karlsson','dat11aka@student.lu.se','dat11aka',NULL,'2014-02-20 15:13:15','2014-02-20 15:13:15',2),(24,'expired','Joakim','Brorsson','b.joakim@gmail.com','ada10jbr',NULL,'2014-02-20 15:13:29','2014-02-20 15:13:29',2),(25,'expired','Jakob','Folkesson','jakob.folkesson.89@gmail.com','ada10jfo',NULL,'2014-02-20 15:13:48','2014-02-20 15:13:48',2),(26,'active','Axel','Andersson','ax.andersson@gmail.com','elt11aan',NULL,'2014-02-20 15:14:00','2014-02-20 15:14:00',2),(27,'active','Jonatan','Ferm','jonatan.ferm@gmail.com','pi08jf6',NULL,'2014-02-20 15:14:14','2014-02-20 15:14:14',2),(28,'active','Gunnar','Rolander','gunnar.rolander@gmail.com','lan11gro',NULL,'2014-02-20 15:14:30','2014-02-20 15:14:30',2),(29,'active','Micaela','Bortas','ael10mbo@student.lu.se','ael10mbo',NULL,'2014-02-20 15:14:45','2014-02-20 15:14:45',2),(30,'active','Niklas','AldÃ©n','niklas.alden1@gmail.com','ael10nal',NULL,'2014-02-20 15:15:00','2014-02-20 15:15:00',2),(31,'expired','Lars','Gustafsson','mezz@dsek.lth.se','ada10lgu',NULL,'2014-02-20 15:16:09','2014-02-20 15:16:09',2),(32,'active','Carl Cristian','Arlock','ccw@df.lth.se','dt07ca7',NULL,'2014-02-20 15:16:22','2014-02-20 15:16:22',2),(33,'active','MÃ¥rten','Kjellsson','maarten.kjellsson@gmail.com','cie04mkj',NULL,'2014-02-20 15:16:34','2014-02-20 15:16:34',2),(34,'expired','Henrik','Ã…lund','hk.alund@gmail.com','aar08hal',NULL,'2014-02-20 15:16:49','2014-02-20 15:16:49',2),(35,'expired','Christian','Daniel','christianrdaniel@gmail.com','',NULL,'2014-02-20 15:17:06','2014-02-20 15:17:06',2),(36,'expired','Christian','SÃ¶derberg','christian.soderberg@cs.lth.se','cs-cso',NULL,'2014-02-20 15:18:42','2014-02-20 15:18:42',2),(37,'expired','Emma','SÃ¶derberg','emma.soderberg@cs.lth.se','csz-enm',NULL,'2014-02-20 15:18:57','2014-02-20 15:18:57',2),(38,'active','Mattias','SÃ¶nnerup','undeadmattias@hotmail.com','elt13mso',NULL,'2014-02-20 15:19:13','2014-02-20 15:19:13',2),(39,'active','David','Etienne','ddetienne@gmail.com','int13det',NULL,'2014-02-20 15:19:24','2014-02-20 15:19:24',2),(40,'active','Samir','Rawashdeh','samir.rawashdeh@outlook.com','elt13sra',NULL,'2014-02-20 15:19:37','2014-02-20 15:19:37',2),(41,'active','Einar','Vading','ael09eva@student.lu.se','ael09eva',NULL,'2014-02-20 15:19:51','2014-02-20 15:19:51',2),(42,'active','Martin','Gunnarsson','dat11mgu@student.lu.se','dat11mgu',NULL,'2014-02-20 15:20:11','2014-02-20 15:20:11',2),(43,'active','Erik','Wilstermann','erik.wilstermann@hotmail.com','elt13ewi',NULL,'2014-02-20 15:20:34','2014-02-20 15:20:34',2),(44,'active','Filippa','De Laval','af.delaval@gmail.com','dat13fde',NULL,'2014-02-20 15:20:47','2014-02-20 15:20:47',2),(45,'active','Julian','Rath','julian.rath@gmail.com','int13jra',NULL,'2014-02-20 15:21:00','2014-02-20 15:21:00',2),(46,'active','Henrik','Wahlgren','mail@henrikwahlgren.se','elt13hwa',NULL,'2014-02-20 15:21:11','2014-02-20 15:21:11',2),(47,'active','Viktor','Nybom','viktor@nybom.dk','ped08vny',NULL,'2014-02-20 15:21:26','2014-02-20 15:21:26',2),(48,'active','Alex','BjÃ¶rklund','alex.m.bjorklund@gmail.com','',NULL,'2014-02-20 15:21:46','2014-02-20 15:21:46',2),(49,'active','Morgan','Persson','morgan.persson@kansli.lth.se','cie96mpe',NULL,'2014-02-20 15:22:10','2014-02-20 15:22:10',2),(64,'active','Niklas','Hallberg','niklas.hallberg.014@student.lu.se','ael10nha',NULL,'2014-02-21 12:58:56','2014-02-21 12:58:56',1),(51,'active','Martin','Holmstrand','martinbholmstrand@gmail.com','',NULL,'2014-02-20 15:24:08','2014-02-20 15:24:08',2),(52,'active','Anton','Landberg','bitter@eta.chalmers.se','',NULL,'2014-02-20 15:24:24','2014-02-20 15:24:24',2),(53,'active','Marcus','Andersson','info@marcusandersson.se','ael09man',NULL,'2014-02-20 15:24:37','2014-02-20 15:24:37',2),(54,'active','Ã–rs-Barna','BlÃ©nessy','bas12obl@student.lu.se','bas12obl',NULL,'2014-02-20 15:24:52','2014-02-20 15:24:52',2),(55,'active','David','Bondesson','zba08dbo@student.lu.se','zba08dbo',NULL,'2014-02-20 15:25:06','2014-02-20 15:25:06',2),(56,'active','Amitoj','Deo','amitoj.deo@gmail.com','ael08ade',NULL,'2014-02-20 15:25:21','2014-02-20 15:25:21',2),(57,'active','Jonatan','Atles','elt13jat@student.lu.se','elt13jat',NULL,'2014-02-20 15:25:35','2014-02-20 15:25:35',2),(58,'active','Patrik','Persson','patrik.persson@live.com','elt12ppe',NULL,'2014-02-20 15:25:47','2014-02-20 15:25:47',2),(59,'active','MÃ¥ns','FÃ¤llman','mans.fallman.648@student.lu.se','elt11mfa',NULL,'2014-02-20 15:25:58','2014-02-20 15:25:58',2),(60,'active','Robin','Hedlund','hedlund.robin@gmail.com','elt11rhe',NULL,'2014-02-20 15:26:11','2014-02-20 15:26:11',2),(61,'active','Marcus','Romner','elt11mro@student.lu.se','elt11mro',NULL,'2014-02-20 15:26:27','2014-02-20 15:26:27',2),(62,'expired','Joakim','Arnsby','joakim.arnsby@gmail.com','cie04jar',NULL,'2014-02-20 16:04:37','2014-02-20 16:04:37',2),(63,'expired','Lukas','Arnsby','lukas.arnsby@gmail.com','cid05lar',NULL,'2014-02-20 16:04:50','2014-02-20 16:04:50',2),(65,'active','Christer','Vestermark','crallian@gmail.com','ama10cve',NULL,'2014-02-25 17:47:28','2014-02-25 17:47:28',13),(66,'pending','Erik','Lundh','erik.lundh@gmail.com','',NULL,'2014-02-27 02:29:53','2014-02-27 02:29:53',2),(67,'active','Gustav','Persson','gustav.persson90@gmail.com','ama09gpe',NULL,'2014-02-27 17:59:23','2014-02-27 17:59:23',13),(68,'active','Oscar','Linde','oscar.j.linde@gmail.com','ama09oli',NULL,'2014-02-27 18:01:11','2014-02-27 18:01:11',13),(69,'pending','Daniel','Jaghobi','pourshalmani@gmail.com','tna13dja',NULL,'2014-03-04 13:06:29','2014-03-04 13:06:29',14),(70,'active','Oscar','SÃ¶nnergren','osonnergren@gmail.com','elt11oso',NULL,'2014-03-04 13:51:22','2014-03-04 13:51:22',11),(71,'pending','Pontus','Lundberg','lundberg.pontus.vastra@gmail.com','bas11pl1',NULL,'2014-04-04 11:06:35','2014-04-04 11:06:35',12);
/*!40000 ALTER TABLE `person` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `person_group`
--

DROP TABLE IF EXISTS `person_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `person_group` (
  `uid` int(11) NOT NULL,
  `gid` int(11) NOT NULL,
  PRIMARY KEY (`uid`,`gid`),
  KEY `gid` (`gid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `person_group`
--

LOCK TABLES `person_group` WRITE;
/*!40000 ALTER TABLE `person_group` DISABLE KEYS */;
INSERT INTO `person_group` VALUES (1,1),(1,13),(2,3),(2,4),(2,7),(11,3),(11,4),(11,8),(12,3),(12,4),(12,9),(13,3),(13,4),(14,2),(14,10),(21,12),(47,11),(49,13),(51,12),(62,2),(64,14);
/*!40000 ALTER TABLE `person_group` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-04-04 11:12:28
