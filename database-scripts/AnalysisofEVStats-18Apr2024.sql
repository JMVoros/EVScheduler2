INSERT INTO chargingstation
(Id,Available) VALUES
(20,1);
SELECT * FROM evscheduler.chargingstation order by Id desc ;

-- SELECT * FROM evscheduler.performancestats where  ElapsedTime = 0 and ChargerCount = 5;
SELECT count(*) FROM evscheduler.performancestats;
 SELECT count(*) FROM evscheduler.performancestats where  ElapsedTime >0 ;
-- SELECT count(*) FROM evscheduler.performancestats where  ChargerCount = 15 ;
-- SELECT count(*) FROM evscheduler.performancestats where  ChargerCount >15 ;
SELECT ChargerCount, count(*) FROM evscheduler.performancestats where  ElapsedTime = 0 group by ChargerCount ;
SELECT   ChargerCount ,min(ElapsedTime),avg(ElapsedTime), max(ElapsedTime) FROM evscheduler.performancestats  where  ElapsedTime > 0 group by ChargerCount ;
-- NExt one below does not make sense 
SELECT ChargerCount, min(BusCount) ,avg(BusCount) , Max(BusCount)  FROM evscheduler.performancestats where UnchargedBusCount = 0 group by ChargerCount;

-- Next one makes sense
SELECT ChargerCount, max(BusCount - UnchargedBusCount) FROM evscheduler.performancestats group by ChargerCount ;

SELECT ChargerCount, min(BusCount ) FROM evscheduler.performancestats where UnchargedBusCount > 0  group by ChargerCount ;
-- ***********
SELECT *  FROM evscheduler.performancestats where ChargerCount = 1;
-- SELECT *  FROM evscheduler.performancestats where UnchargedBusCount = 0 and ChargerCount = 5\;
-- SELECT *  FROM evscheduler.performancestats where UnchargedBusCount = 0 and ChargerCount = 5;
-- SELECT *  FROM evscheduler.performancestats where UnchargedBusCount = 0 and  BusCount > 40 ;
-- SELECT *  FROM evscheduler.performancestats where   BusCount > 40 ;
