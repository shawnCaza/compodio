# ************************************************************
# Sequel Ace SQL dump
# Version 20039
#
# https://sequel-ace.com/
# https://github.com/Sequel-Ace/Sequel-Ace
#
# Host: localhost (MySQL 8.0.23)
# Database: community_radio
# Generation Time: 2023-01-16 03:37:28 +0000
# ************************************************************


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
SET NAMES utf8mb4;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE='NO_AUTO_VALUE_ON_ZERO', SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


# Dump of table all_tags
# ------------------------------------------------------------

CREATE TABLE `all_tags` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `tag` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `frequency` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag` (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



# Dump of table episodes
# ------------------------------------------------------------

CREATE TABLE `episodes` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `show_id` int DEFAULT NULL,
  `mp3` varchar(300) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ep_date` datetime DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `show_id` (`show_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



# Dump of table show_images
# ------------------------------------------------------------

CREATE TABLE `show_images` (
  `show_id` varchar(48) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `sizes` json NOT NULL,
  `last_updt` datetime DEFAULT NULL,
  `dom_colours` json DEFAULT NULL,
  PRIMARY KEY (`show_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;



# Dump of table show_tags
# ------------------------------------------------------------

CREATE TABLE `show_tags` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `show_id` int DEFAULT NULL,
  `tag_id` int DEFAULT NULL,
  `frequency` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tag_show_group` (`show_id`,`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



# Dump of table shows
# ------------------------------------------------------------

CREATE TABLE `shows` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `showName` varchar(250) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `source` varchar(40) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `img` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `desc` varchar(4000) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `host` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `internal_link` varchar(250) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `ext_link` varchar(250) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email` varchar(150) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `slug` varchar(300) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `show_source` (`showName`,`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;




/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
