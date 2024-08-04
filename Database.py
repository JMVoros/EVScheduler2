import mysql.connector
import Config

class BusStatus(object):
    def __init__(self, queryResult: tuple):
        self.busId = queryResult[0]
        self.currentCharge = queryResult[1]
        self.requiredCharge = queryResult[2]
        self.registration = queryResult[3]
        self.capacity = queryResult[4]

class ChargingSchedule(object):
    def __init__(self, busStatus: BusStatus):
        self.BusId = busStatus.busId
        self.ChargeTime = 0
        self.ChargeEndTime = 0
        self.ChargeSlot = -1
        self.ChargeDuration = 0
        self.ChargingPoint = 0
        self.BusStatus = busStatus
        self.SlotCount = 0
        self.ChargeCost = 0.0

class ChargingReportByStation(object):
    def __init__(self, queryResult: tuple):
        self.ChargingPoint = queryResult[0]
        self.ChargeTime = queryResult[1]
        self.ChargeEndTime = queryResult[2]
        self.Registration = queryResult[3]
        self.Soc = queryResult[4]
        self.CapacityRequired = queryResult[5]
        self.ChargeDuration = queryResult[6]
        self.ChargeCost = queryResult[7]

class ActivityReportItem(object):
    def __init__(self, queryResult: tuple):
        self.ChargingPoint = queryResult[0]
        self.Time = queryResult[1]
        self.Registration = queryResult[2]
        self.Connect = queryResult[3]
        
class TariffItem(object):
    def __init__(self, queryResult: tuple):
        self.startTime = queryResult[0]
        self.endTime = queryResult[1]
        self.cost = queryResult[2]

class ManagementSummary(object):
    def __init__(self, date: str):
        self.Date = date
        self.BusCount = 0
        self.ActiveChargerCount = 0
        self.UnchargedBusCount = 0
        self.ChargeCapacity = 0
        self.ChargeTimeRequired = 0
        self.TotalActualCost = 0.0
        self.TotalBaselineCost = 0.0
        self.RunTime = 0.0
        
class PreCalcData(object):
    def __init__(self, initialiser: tuple):
        self.Date = initialiser[0]
        self.BusId = initialiser[1]
        self.CurrentCharge = initialiser[2]
        self.RequiredCharge = initialiser[3]  

class PerformanceStats(object):
    def __init__(self, date: str):
        self.Date = date
        self.BusCount = 0
        self.ChargerCount = 0
        self.UnchargedBusCount = 0
        self.ElapsedTime = 0.0

class Database(object):
    """description of class"""
    def __init__(self, config: Config.DatabaseConfig):
        self.mydb = mysql.connector.connect(
              host=config.server,
              user=config.user,
              password=config.password,
              database=config.database
            )

    def __del__(self):
        self.mydb.close()
        
    def GetChargePoints(self) -> [int]:
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT id FROM chargepoint WHERE Available <> 0")
        result = []
        for queryitem in mycursor.fetchall():
            result.append(queryitem[0])
        mycursor.close()
        return result

    def GetBusStatus(self, date: str) -> [BusStatus]:
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT a.BusId, a.SoC, a.RequiredCharge, b.Registration, b.ChargeCapacity FROM busstatus as a INNER JOIN Bus as b ON a.BusId = b.Id WHERE a.Date = DATE(%s)", [date])
        result = []
        for queryItem in mycursor.fetchall():
            result.append(BusStatus(queryItem))
        mycursor.close()
        return result

    def GetElectricityCost(self) -> [TariffItem]:
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT StartTime, EndTime, Cost from electricitycost")
        result = []
        for queryItem in mycursor.fetchall():
            result.append(TariffItem(queryItem))
        mycursor.close()
        return result

    def SaveChargingSchedule(self, charging: [ChargingSchedule], date: str):
        mycursor = self.mydb.cursor()
        mycursor.execute("DELETE FROM chargingschedule WHERE Date = DATE(%s)", [date])
        transformData = list([date, f.BusId, f.ChargeTime, f.ChargeDuration, f.ChargingPoint, f.ChargeCost, f.ChargeEndTime] for f in charging)
        mycursor.executemany("INSERT INTO chargingschedule (Date, BusId, ChargeTime, ChargeDuration, ChargingPoint, Cost, ChargeEndTime) VALUES (DATE(%s), %s, %s, %s, %s, %s, %s)", transformData)
        self.mydb.commit()
        mycursor.close()

    def SaveManagementSummary(self, ms: ManagementSummary):
        mycursor = self.mydb.cursor()
        mycursor.execute("DELETE FROM managementsummary WHERE Date = DATE(%s)", [ms.Date])
        mycursor.execute("INSERT INTO managementsummary (Date, BusCount, ActiveChargerCount, UnchargedBusCount, ChargeCapcity, ChargeTimeRequired, TotalActualCost, TotalBaselineCost,RunTime) VALUES(DATE(%s), %s, %s, %s, %s, %s, %s, %s, %s)", \
            [ms.Date, ms.BusCount, ms.ActiveChargerCount, ms.UnchargedBusCount, ms.ChargeCapacity, ms.ChargeTimeRequired, ms.TotalActualCost, ms.TotalBaselineCost, ms.RunTime])
        self.mydb.commit()
        mycursor.close()

    def SavePreCalcData(self, pcd: [PreCalcData], date: str):
        mycursor = self.mydb.cursor()
        mycursor.execute("DELETE FROM busstatus WHERE Date = DATE(%s)", [date])
        transformData = list([date, f.BusId,f.CurrentCharge,f.RequiredCharge] for f in pcd) 
        
        mycursor.executemany("INSERT INTO busstatus (Date,BusId,SoC,RequiredCharge) VALUES (DATE(%s), %s, %s, %s)" ,\
             transformData)
        self.mydb.commit()
        mycursor.close()
        
    def GetChargingReportByStation(self, date:str, allocated: bool) -> [ChargingReportByStation]:
        mycursor = self.mydb.cursor()
        cmd = "SELECT a.chargingPoint, a.ChargeTime, a.ChargeEndTime, b.Registration, c.Soc, c.RequiredCharge, a.ChargeDuration, a.Cost from chargingschedule as a INNER JOIN bus as b ON a.BusId = b.Id INNER JOIN busstatus as c ON a.BusId = c.BusId AND a.Date = c.Date WHERE a.chargingPoint %s 0 AND a.ChargeDuration > 0 AND a.Date = DATE(\"%s\") order by a.chargingPoint, a.ChargeTime " \
            % ('<>' if allocated else '=', date)
        mycursor.execute(cmd)
        result = []
        for queryItem in mycursor.fetchall():
            result.append(ChargingReportByStation(queryItem))
        mycursor.close()
        return result

    def GetChargingReportChargeNotNeeded(self, date:str, allocated: bool) -> [ChargingReportByStation]:
        mycursor = self.mydb.cursor()
        cmd = "SELECT a.chargingPoint, a.ChargeTime, a.ChargeEndTime, b.Registration, c.Soc, c.RequiredCharge, a.ChargeDuration, a.Cost from chargingschedule as a INNER JOIN bus as b ON a.BusId = b.Id INNER JOIN busstatus as c ON a.BusId = c.BusId AND a.Date = c.Date WHERE a.chargingPoint %s 0 AND a.ChargeDuration = 0 AND a.Date = DATE(\"%s\") order by a.chargingPoint, a.ChargeTime " \
            % ('<>' if allocated else '=', date)
        mycursor.execute(cmd)
        result = []
        for queryItem in mycursor.fetchall():
            result.append(ChargingReportByStation(queryItem))
        mycursor.close()
        return result
        
    def GetActivityReport(self, date:str) -> [ActivityReportItem]:
        mycursor = self.mydb.cursor()
        mycursor.execute("SELECT x.ChargingPoint, x.Time, y.Registration, x.Activity FROM (SELECT a.Date, a.ChargingPoint, a.ChargeTime as Time, a.BusId, true as Activity from chargingschedule as a UNION ALL SELECT a.Date, a.ChargingPoint, a.ChargeEndTime as Time, a.BusId, false as Activity from chargingschedule as a) as x INNER JOIN bus as y ON x.BusId = y.Id WHERE x.ChargingPoint <> 0 AND x.Date = DATE(%s) ORDER BY x.Time", [date])
        result = []
        for queryItem in mycursor.fetchall():
            result.append(ActivityReportItem(queryItem))
        mycursor.close()
        return result

    def SavePerformanceStats(self, pt: PerformanceStats):
        mycursor = self.mydb.cursor()
        mycursor.execute("INSERT INTO performancestats(Date, BusCount, ChargerCount,UnchargedBusCount, ElapsedTime) VALUES(DATE(%s), %s, %s, %s, %s)", \
            [pt.Date, pt.BusCount, pt.ChargerCount, pt.UnchargedBusCount, pt.ElapsedTime])
        self.mydb.commit()
        mycursor.close()


