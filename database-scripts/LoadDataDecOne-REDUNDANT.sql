USE evscheduler;
DELETE FROM busstatus WHERE Date = DATE("2023-12-1");
INSERT INTO busstatus
(Date,BusId,SoC,RequiredCharge)
VALUES
(DATE("2023-12-1"), 1, 0.25, 0.8),
(DATE("2023-12-1"), 2, 0.25, 0.8),
(DATE("2023-12-1"), 3, 0.35, 0.7),
(DATE("2023-12-1"), 4, 0.25, 0.8),
(DATE("2023-12-1"), 5, 0.25, 0.7),
(DATE("2023-12-1"), 6, 0.25, 0.8),
(DATE("2023-12-1"), 7, 0.3, 0.7),
(DATE("2023-12-1"), 8, 0.25, 0.8),
(DATE("2023-12-1"), 9, 0.2, 0.7),
(DATE("2023-12-1"), 10, 0.25, 0.8);
