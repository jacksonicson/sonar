delimiter $$

CREATE TABLE `host2sensors` (
  `HOST_ID` int(11) DEFAULT NULL,
  `SENSOR_ID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8$$

delimiter $$

CREATE TABLE `hosts` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `extends` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=87 DEFAULT CHARSET=utf8$$

delimiter $$

CREATE TABLE `params` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `SENSOR_ID` int(11) DEFAULT NULL,
  `param` varchar(45) DEFAULT NULL,
  `value` varchar(45) DEFAULT NULL,
  `extend` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8$$

delimiter $$

CREATE TABLE `sensors` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `zip` longblob,
  `md5` varchar(80) DEFAULT NULL,
  `interv` int(11) DEFAULT NULL,
  `type` int(1) DEFAULT NULL,
  `extends` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `name_UNIQUE` (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8$$

