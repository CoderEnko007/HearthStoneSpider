create table `hs_cards` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mana` int(11) NOT NULL,
  `hp` int(11) NOT NULL,
  `attack` int(11) NOT NULL,
  `cname` varchar(100) NOT NULL,
  `description` varchar(300) NOT NULL,
  `ename` varchar(100) NOT NULL,
  `faction` varchar(20) NOT NULL,
  `clazz` varchar(20) NOT NULL,
  `race` varchar(20) NOT NULL,
  `img` varchar(300) NOT NULL,
  `rarity` varchar(20) NOT NULL,
  `rule` varchar(300) NOT NULL,
  `seriesAbbr` varchar(20) NOT NULL,
  `seriesName` varchar(20) NOT NULL,
  `thumbnail` varchar(300) NOT NULL,
  PRIMARY KEY (`id`)
)ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;