INSERT INTO chargepoint
(Id,Available) VALUES
(20,1);
SELECT * FROM evscheduler.chargepoint order by Id desc ;


-- Some useful SQL Queries for Analysis
SELECT count(*) FROM evscheduler.performancestats;
SELECT count(*) FROM evscheduler.performancestats where  ElapsedTime > 0 ;
SELECT ChargerCount, count(*) FROM evscheduler.performancestats where  ElapsedTime = 0 group by ChargerCount ;
SELECT   ChargerCount ,min(ElapsedTime),avg(ElapsedTime), max(ElapsedTime) FROM evscheduler.performancestats  where  ElapsedTime > 0 group by ChargerCount ;
SELECT ChargerCount, min(BusCount) ,avg(BusCount) , Max(BusCount)  FROM evscheduler.performancestats where UnchargedBusCount = 0 group by ChargerCount;

SELECT ChargerCount, max(BusCount - UnchargedBusCount) FROM evscheduler.performancestats group by ChargerCount ;
SELECT ChargerCount, min(BusCount ) FROM evscheduler.performancestats where UnchargedBusCount > 0  group by ChargerCount ;
SELECT BusCount, min(BusCount) ,avg(BusCount) , Max(BusCount)  FROM evscheduler.performancestats where UnchargedBusCount = 0 group by BusCount;
-- ***********
SELECT *  FROM evscheduler.performancestats where ChargerCount = 1;
-- SELECT *  FROM evscheduler.performancestats where UnchargedBusCount = 0 and ChargerCount = 5\;
-- SELECT *  FROM evscheduler.performancestats where UnchargedBusCount = 0 and ChargerCount = 5;
-- SELECT *  FROM evscheduler.performancestats where UnchargedBusCount = 0 and  BusCount > 40 ;
-- SELECT *  FROM evscheduler.performancestats where   BusCount > 40 ;
-- ***********
-- SELECT * FROM evscheduler.performancestats where  ElapsedTime = 0 and ChargerCount = 5;
-- SELECT count(*) FROM evscheduler.performancestats where  ChargerCount = 15 ;
-- SELECT count(*) FROM evscheduler.performancestats where  ChargerCount >15 ;

