USE evscheduler;
DROP TABLE IF EXISTS busstatus;
DROP TABLE IF EXISTS chargingschedule;
DROP TABLE IF EXISTS bus;
DROP TABLE IF EXISTS chargepoint;
DROP TABLE IF EXISTS electricitycost;
DROP TABLE IF EXISTS managementsummary;
DROP TABLE IF EXISTS performancestats;

CREATE TABLE bus (
  Id int NOT NULL COMMENT 'Unique identifier of this bus',
  Registration varchar(50) NOT NULL COMMENT 'The bus license number plate',
  ChargeCapacity double DEFAULT NULL COMMENT 'The capacity of the bus (kW)',
  PRIMARY KEY (Id,Registration)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE chargepoint (
  Id int NOT NULL COMMENT 'unique identifier of this charge point',
  Available tinyint DEFAULT NULL COMMENT 'Whether this charge point is available. 0 means no, non-zero means yes',
  PRIMARY KEY (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE electricitycost (
  EndTime datetime DEFAULT NULL COMMENT 'The ending time for this price bracket',
  StartTime datetime DEFAULT NULL COMMENT 'The starting time for this price bracket',
  Cost float DEFAULT NULL COMMENT 'The date of this schedule'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE busstatus (
  Date date NOT NULL COMMENT 'The date of this schedule',
  BusId int NOT NULL COMMENT 'The Identifier of the bus being charged (foreign key).',
  SoC double DEFAULT NULL COMMENT 'The amount of charge (expressed as a percentage) left in the bus upon entry to the depot.',
  RequiredCharge double DEFAULT NULL COMMENT 'The amount of change (expressed as a percentage) required for the next day, as specified by the scheduler. We add 10% to this figure for safety when we are calculating scheduling times.',
  PRIMARY KEY (Date,BusId),
  KEY StatusBusId_idx (BusId),
  CONSTRAINT BusId FOREIGN KEY (BusId) REFERENCES bus (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE chargingschedule (
  Date date NOT NULL COMMENT 'The date of this schedule',
  BusId int NOT NULL COMMENT 'The Identifier of the bus being charged (foreign key).',
  ChargeTime int DEFAULT NULL COMMENT 'the selected appropriate time to charge the bus. Units of minutes since the charge window',
  ChargeDuration int DEFAULT NULL COMMENT 'The amount of time (in minutes) required to charge the vehicle.',
  ChargeEndTime int DEFAULT NULL COMMENT 'The time of completion of the charge time. Unit of minutes since the charge window',
  ChargingPoint int DEFAULT NULL COMMENT 'The charging point ID (foreign key) selected for charging this bus.',
  Cost double DEFAULT NULL COMMENT 'The cost of charging this bus',
  PRIMARY KEY (Date,BusId),
  KEY ScheduleBusId_idx (BusId),
  KEY ScheduleChargingId_idx (ChargingPoint),
  CONSTRAINT ScheduleBusId_fk FOREIGN KEY (BusId) REFERENCES bus (Id),
  CONSTRAINT ScheduleChargeId_fk FOREIGN KEY (ChargingPoint) REFERENCES chargepoint (Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE managementsummary (
  Date date NOT NULL COMMENT 'The date of this summary',
  BusCount int NOT NULL COMMENT 'The number of buses in the fleet',
  ActiveChargerCount int DEFAULT NULL COMMENT 'The number of active chargers',
  UnchargedBusCount int DEFAULT NULL COMMENT 'The number of buses that failed to be scheduled',
  ChargeCapcity int DEFAULT NULL COMMENT 'The total amount in minutes of charge capacity (charger count * window size in minutes)',
  ChargeTimeRequired int DEFAULT NULL COMMENT 'The total amount of minutes of charge required to charge the entire fleet',
  TotalActualCost double DEFAULT NULL COMMENT 'The total cost of charging the fleet with the created schedule',
  TotalBaselineCost double DEFAULT NULL COMMENT 'The baseline cost of charging the fleet using a simple first come first serve basis',
  RunTime  decimal(19,10) NOT NULL COMMENT 'The time taken to generate the schedule',
  PRIMARY KEY (Date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE performancestats (
  Date date NOT NULL COMMENT 'The date of this performance',
  BusCount int NOT NULL COMMENT 'The number of buses in the fleet',
  ChargerCount int DEFAULT NULL COMMENT 'The number of active chargers',
  UnchargedBusCount int DEFAULT NULL COMMENT 'The number of buses that failed to be scheduled',
  ElapsedTime  decimal(19,15) NOT NULL COMMENT 'The time taken to generate the schedule'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;




