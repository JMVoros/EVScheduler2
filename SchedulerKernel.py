import ElectricityPricer
import Config
import Database
import math
import time

class Iterator(object):
    def __init__(self, durations: [int], slotCount: int):
        self.__durations = durations
        self.__slotCount = slotCount
        self.__slots = [0] * len(durations)
        slot = 0
        for i in range(0, len(durations)):
            self.__slots[i] = slot
            slot = slot + durations[i]
        if slot > slotCount:
            raise Exception("there are too many slots")
        self.__eof = False

    def Next(self):
        i = len(self.__slots) - 1
        durations = 0
        while i >= 0:
            durations = durations + self.__durations[i]
            if self.__slots[i] + durations < self.__slotCount:
                break;
            i = i - 1
        if i < 0:
            self.__eof = True
            return
        self.__slots[i] = self.__slots[i] + 1
        i = i + 1
        while i < len(self.__slots):
            self.__slots[i] = self.__slots[i - 1] + self.__durations[i - 1]
            i = i + 1

    @property
    def Slots(self):
        return self.__slots

    @property
    def Eof(self):
        return self.__eof

class Orderer(object):
    def __init__(self, items: []):
        self.__i1 = 0
        self.__i2 = 0
        self.__eof = False
        self.__originalItems = items
        self.__indexes = [0] * (len(items) - 1)
        self.__result = [None] * len(items)
        self.__createResult()
        
    def Next(self):
        if len(self.__originalItems) <= 1:
            self.__eof = True
            return

        i = len(self.__indexes) - 1
        while self.__indexes[i] >= len(self.__indexes) - i:
            i = i - 1
            if (i < 0):
                self.__eof = True
                return

        self.__indexes[i] = self.__indexes[i] + 1
        for j in range(i+1, len(self.__indexes)):
           self.__indexes[j] = 0
        
        self.__createResult()    
            
    def __createResult(self):
        indexes = list(range(0, len(self.__originalItems)))
        for i in range(0, len(indexes)):
            x = 0
            target = 0 if i >= len(self.__indexes) else self.__indexes[i]
            for j in range(0, len(indexes)):
                if indexes[j] >= 0:
                    if x == target:
                        self.__result[i] = self.__originalItems[j]
                        indexes[j] = -1
                        break
                    x = x + 1

        
    @property
    def Items(self):
        return self.__result

    @property
    def Indexes(self):
        return self.__indexes

    @property
    def Eof(self):
        return self.__eof

class ChargingPointData(object):
    def __init__(self, id: int, slotCount: int):
        self.__id = id
        self.__busesAllocated = []
        self.__slotsAvailable = slotCount
        
    def Allocate(self, chargingSchedule: Database.ChargingSchedule) -> bool:
        if chargingSchedule.SlotCount == 0:
            return True
        if chargingSchedule.SlotCount <= self.__slotsAvailable:
           self.__busesAllocated.append(chargingSchedule)
           self.__slotsAvailable = self.__slotsAvailable - chargingSchedule.SlotCount
           chargingSchedule.ChargingPoint = self.__id
           return True
        return False

    @property
    def SlotsAvailable(self):
        return self.__slotsAvailable

    @property
    def BusesAllocated(self):
        return self.__busesAllocated

    @property
    def ChargingPointId(self):
        return self.__id

class SchedulerKernel(object):
    """description of class"""
    def __init__(self, config: Config.ChargingConfig, db : Database.Database, date: str):
        self.__helper = ElectricityPricer.TimeSlotHelper(config)
        self.__pricer = ElectricityPricer.ElectricityPricer(config, db.GetElectricityCost())
        self.__config = config
        self.__database = db
        self.__date = date
        self.__startTime = time.time()
        self.__chargingSchedule = list(Database.ChargingSchedule(f) for f in db.GetBusStatus(date))
        self.__chargingPoints = list(ChargingPointData(f, self.__helper.SlotCount) for f in db.GetChargePoints())
        self.__managementSummary = Database.ManagementSummary(date)
        self.__managementSummary.ActiveChargerCount = len(self.__chargingPoints)
        self.__managementSummary.BusCount = len(self.__chargingSchedule)
        self.__managementSummary.ChargeCapacity = self.__helper.SlotCount * self.__helper.SlotDuration * self.__managementSummary.ActiveChargerCount
        self.__performanceStats = Database.PerformanceStats(date)
        self.__performanceStats.ChargerCount = len(self.__chargingPoints)
        self.__performanceStats.BusCount = len(self.__chargingSchedule)
        
    def CalculateSchedule(self):
        self.CalculateChargingDurations()
        self.__managementSummary.TotalBaselineCost = self.CalculateBaselineCost()
        self.__managementSummary.UnchargedBusCount = self.AllocateChargingPoints()
        self.FindBestChargingTimes()
        self.__database.SaveChargingSchedule(self.__chargingSchedule, self.__date)
        self.__endTime = time.time()
        self.__managementSummary.RunTime = self.__endTime - self.__startTime 
        self.__database.SaveManagementSummary(self.__managementSummary)
        self.__performanceStats.ElapsedTime = self.__managementSummary.RunTime 
        self.__performanceStats.UnchargedBusCount = self.__managementSummary.UnchargedBusCount
        self.__database.SavePerformanceStats(self.__performanceStats)
        
    def CalculateChargingDurations(self):
        for schedule in self.__chargingSchedule:
            schedule.ChargeDuration = self.__calculateDuration(schedule)
            self.__managementSummary.ChargeTimeRequired = self.__managementSummary.ChargeTimeRequired + schedule.ChargeDuration
            schedule.SlotCount = self.__helper.DurationToSlotCount(schedule.ChargeDuration)[0]
        self.__chargingSchedule.sort(key=lambda x: x.ChargeDuration, reverse=True)

    def __calculateDuration(self, schedule: Database.ChargingSchedule):
        kwRequired = max((min(schedule.BusStatus.requiredCharge + 0.1, 1.0) - schedule.BusStatus.currentCharge) * schedule.BusStatus.capacity, 0.0)
        return round(kwRequired / self.__config.rate * 60)
        
    # needed for unit testing
    def RetrieveChargingSchedule(self) -> [Database.ChargingSchedule]:
        return self.__chargingSchedule

    def RetrieveChargingPoints(self) -> [ChargingPointData]:
        return self.__chargingPoints

    def AllocateChargingPoints(self) -> int:
        busCount = len(self.__chargingSchedule)
        if busCount == 0:
            return 0
        failCount = 0
        nextBus = 0
        while True:
            busallocated = False
            for i in range(0, len(self.__chargingPoints)):
                if self.__chargingPoints[i].Allocate(self.__chargingSchedule[nextBus]):
                    nextBus = nextBus + 1
                    if nextBus >= busCount:
                       return failCount # all the buses have been processed
                    busallocated = True
            if not busallocated:
                failCount = failCount + 1
                nextBus = nextBus + 1
                if nextBus >= busCount:
                   return failCount # all the buses have been processed

            # the aim is to try and even out the use of the chargers as much as possible
            # this will ensure that all chargers are able to make use of the cheaper tariffs and avoid the expensive tariffs
            # to do this we sort the charging points by how much they have available
            self.__chargingPoints.sort(key=lambda x: x.SlotsAvailable, reverse=True)

    def FindBestChargingTimes(self):
        for point in self.__chargingPoints:
            self.__findBestChargingTimesForPoint(point)

    def __findBestChargingTimesForPoint(self, point: ChargingPointData):
        bestCost = 1e99
        oit = Orderer(point.BusesAllocated)
        while not oit.Eof:
           durations = list(f.SlotCount for f in oit.Items)
           it = Iterator(durations, self.__helper.SlotCount)
           while not it.Eof:
              candidateCost = self.__calculateChargeCost(oit.Items, it.Slots)
              if candidateCost < bestCost:
                 bestCost = candidateCost
                 for i in range(0, len(oit.Items)):
                    oit.Items[i].ChargeSlot = it.Slots[i]
              it.Next()
           oit.Next()

        # job done. now calculate the charging time from the flow
        for bus in point.BusesAllocated:
            bus.ChargeTime = bus.ChargeSlot * self.__helper.SlotDuration
            bus.ChargeEndTime = bus.ChargeTime + bus.ChargeDuration
            bus.ChargeCost = self.__pricer.GetCost(bus.ChargeSlot, bus.ChargeDuration)
            self.__managementSummary.TotalActualCost = self.__managementSummary.TotalActualCost + bus.ChargeCost
        return                                                                                                                                                       
    def __calculateChargeCost(self, chargePoint: [Database.ChargingSchedule], startpoints: [int]) -> float:
        cost = 0.0
        for i in range(0, len(startpoints)):
            cost = cost + self.__pricer.GetCost(startpoints[i], chargePoint[i].ChargeDuration)
        return cost

    def CalculateBaselineCost(self) -> float:
        result = 0.0
        nextslot = [0] * len(self.__chargingPoints)
        for bus in self.__chargingSchedule:
            index = nextslot.index(min(nextslot))
            slot = nextslot[index]
            if slot + bus.SlotCount > self.__helper.SlotCount:
                continue # failed to allocate this bus. hope we have better luck with the next bus
            result = result + self.__pricer.GetCost(slot, bus.ChargeDuration)
            slot = slot + bus.SlotCount
            nextslot[index] = slot
        return result



