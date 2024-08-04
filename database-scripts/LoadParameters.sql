USE evscheduler;
SET SQL_SAFE_UPDATES = 0;

DELETE FROM bus;
DELETE FROM chargepoint;
DELETE FROM electricitycost;

SET SQL_SAFE_UPDATES = 1;

INSERT INTO bus
(Id,Registration,ChargeCapacity) VALUES 
(1, "LE18OCV", 200.0 ),         
(2, "LE18ABC", 200.0 ),
(3, "LE18DEF", 200.0 ),
(4, "LE18GHI", 200.0 ),
(5, "LE18TTR", 200.0 ),
(6, "LE18YUV", 200.0 ),
(7, "LE18POQ", 200.0 ),
(8, "LE18MMN", 200.0 ),
(9, "LE18RRS", 200.0 ),
(10, "LE18WOT", 200.0 );

INSERT INTO chargepoint
(Id,Available) VALUES
(0, 0),
(1, 1),
(2, 1),
(3, 1),
(4, 1),
(5, 1);


INSERT INTO electricitycost
(StartTime,EndTime,Cost) VALUES
(TIME("00:00"), TIME("03:00"), 25.0),
(TIME("03:00"), TIME("06:00"), 20.0),
(TIME("18:00"), TIME("21:00"), 35.0),
(TIME("21:00"), TIME("00:00"), 30.0);
