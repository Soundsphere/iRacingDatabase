# ⚠️FIRST VERSION - STILL UNDER DEVELOPMENT⚠️

I consider this already usable, though minor changes and stability upgrades will come in the future


![iRacingLogo](https://s100.iracing.com/wp-content/uploads/2016/07/iRacing-Logo-White-Horizontal-R-1024x189.png "iRacingLogo")

***

This script gets the latest data from the iRacing API, converts the values and stores it in a database. It relies heavily on [iracingdataapi by asondilworth56](https://github.com/jasondilworth56/iracingdataapi) though the python package does not need to be installed as the funcionality needed for this is loaded direclty from irdata_client.py

***

To log into iRacing and use the script, enter your credentials and timezone into the config_shared.ini and rename it to config.ini

***

Car information is stored locally for one less API call. On first run of irmain.py this file gets created, but since cars get added or updated with every season, 
run update_carlist.py every now and then to keep this list up to date

***

To store the data use the following table: 

```
CREATE TABLE `iRacing` (
  `subsessionId` int(15) unsigned NOT NULL,
  `SessionDate` datetime DEFAULT NULL,
  `SeriesName` varchar(255) DEFAULT NULL,
  `Car` varchar(255) DEFAULT NULL,
  `Track` varchar(255) DEFAULT NULL,
  `TrackConfiguration` varchar(255) DEFAULT NULL,
  `QualifyingTime` int(20) DEFAULT NULL,
  `RaceTime` int(20) DEFAULT NULL,
  `AverageLapTime` int(20) DEFAULT NULL,
  `Incidents` int(3) DEFAULT NULL,
  `OldSafetyRating` decimal(3,2) DEFAULT NULL,
  `NewSafetyRating` decimal(3,2) DEFAULT NULL,
  `SafetyRatingGain` decimal(3,2) DEFAULT NULL,
  `Licence` char(2) DEFAULT NULL,
  `StartPosition` int(3) DEFAULT NULL,
  `FinishPosition` int(3) DEFAULT NULL,
  `OldiRating` int(5) DEFAULT NULL,
  `NewiRating` int(5) DEFAULT NULL,
  `iRatingGain` int(3) DEFAULT NULL,
  `Laps` int(4) DEFAULT NULL,
  `LapsLed` int(4) DEFAULT NULL,
  `Points` int(4) DEFAULT NULL,
  `SoF` int(5) DEFAULT NULL,
  `RaceType` varchar(25) DEFAULT NULL,
  `TeamRace` char(5) DEFAULT NULL,
  `QualiSetByTeammate` char(5) DEFAULT NULL,
  `FastestLapSetByTeammate` char(5) DEFAULT NULL,
  `SeasonWeek` int(2) DEFAULT NULL,
  `SeasonNumber` int(2) DEFAULT NULL,
  `SeasonYear` year(4) DEFAULT NULL,
  PRIMARY KEY (`subsessionId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
```