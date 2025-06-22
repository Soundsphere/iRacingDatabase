# iRacingDatabase
FIRST VERSION - STILL UNDER TESTING


This script gets the latest data from the iRacing API, converts the values and stores it in a database. It relies heavily on [iracingdataap by asondilworth56](https://github.com/jasondilworth56/iracingdataapi)

To store the data use the following table: 

```
CREATE TABLE `iRacing` (
  `subsessionId` int(15) unsigned NOT NULL,
  `SessionDate` datetime DEFAULT NULL,
  `SeriesName` varchar(255) DEFAULT NULL,
  `Car` varchar(255) DEFAULT NULL,
  `Track` varchar(255) DEFAULT NULL,
  `QualifyingTime` int(20) DEFAULT NULL,
  `RaceTime` int(20) DEFAULT NULL,
  `Incidents` int(3) DEFAULT NULL,
  `OldSafetyRating` decimal(3,2) DEFAULT NULL,
  `NewSafetyRating` decimal(3,2) DEFAULT NULL,
  `SafetyRatingGain` decimal(3,2) DEFAULT NULL,
  `StartPosition` int(3) DEFAULT NULL,
  `FinishPosition` int(3) DEFAULT NULL,
  `OldiRating` int(5) DEFAULT NULL,
  `NewiRating` int(5) DEFAULT NULL,
  `iRatingGain` int(3) DEFAULT NULL,
  `Laps` int(4) DEFAULT NULL,
  `LapsLed` int(4) DEFAULT NULL,
  `Points` int(4) DEFAULT NULL,
  `SoF` int(5) DEFAULT NULL,
  `TeamRace` char(5) DEFAULT NULL,
  `QualiSetByTeammate` char(5) DEFAULT NULL,
  `SeasonWeek` int(2) DEFAULT NULL,
  `SeasonNumber` int(2) DEFAULT NULL,
  `SeasonYear` year(4) DEFAULT NULL,
  PRIMARY KEY (`subsessionId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
```