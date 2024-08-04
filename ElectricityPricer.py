import datetime
import math
import Config
import Database

class TimeSlotHelper(object):
    def __init__(self, chargingConfig: Config.ChargingConfig):
        self.__startHour = chargingConfig.chargewindowstart.hour
        self.__startMinute = chargingConfig.chargewindowstart.minute
        self.__endHour = chargingConfig.chargewindowend.hour
        self.__endMinute = chargingConfig.chargewindowend.minute
        self.__slotDuration = chargingConfig.slotduration
        windowHours = self.__endHour - self.__startHour
        if windowHours < 0:
            windowHours = windowHours + 24
        windowMinutes = windowHours * 60 + self.__endMinute - self.__startMinute
        self.__slotCount = math.ceil(windowMinutes / self.__slotDuration)

    def TimeToSlot(self, candidateTime: datetime.time) -> int:
        hour = candidateTime.hour
        minute = candidateTime.minute
        if hour < self.__startHour:
            hour = hour + 24
        minutes = 60 * (hour - self.__startHour) + minute - self.__startMinute
        return math.floor(minutes / self.__slotDuration)

    def SlotToTime(self, slot: int) -> datetime.time:
        minutes = slot * self.__slotDuration
        hours = math.floor(minutes / 60)
        hr = self.__startHour + hours
        min = self.__startMinute + minutes - (hours * 60)
        if min >= 60:
            min = min - 60
            hr = hr + 1
        if hr >= 24:
            hr = hr - 24
        return datetime.time(hour=hr, minute=min)

    def OffsetToTime(self, offset: int) -> datetime.time:
        hours = math.floor(offset / 60)
        hr = self.__startHour + hours
        min = self.__startMinute + offset - (hours * 60)
        if min >= 60:
            min = min - 60
            hr = hr + 1
        if hr >= 24:
            hr = hr - 24
        return datetime.time(hour=hr, minute=min)

    def DurationToSlotCount(self, duration: int) -> (int, float):
        if duration <= 0:
            return (0, 0.0)
        count = math.floor(duration / self.__slotDuration)
        minutesLeft = duration - count * self.__slotDuration
        if minutesLeft == 0:
            return (count, 1.0)
        return (count + 1, minutesLeft / self.__slotDuration)

    def GetEndTime(self, slot: int, duration: int) -> datetime.time:
        startTime = self.SlotToTime(slot)
        hour = startTime.hour + math.floor(duration / 60)
        minute = startTime.minute + duration % 60
        if minute >= 60:
            minute = minute - 60
            hour = hour + 1
        if hour >= 24:
            hour = hour - 24
        return datetime.time(hour=hour, minute=minute)

    @property
    def SlotDuration(self) -> int:
        return self.__slotDuration

    @property
    def SlotCount(self) -> int:
        return self.__slotCount

class ElectricityPricer(object):
    """description of class"""
    def __init__(self, chargingConfig: Config.ChargingConfig, costPoints: [Database.TariffItem]):
        self.__timeSlotHelper = TimeSlotHelper(chargingConfig)
        self.__costs = [0.0] * self.__timeSlotHelper.SlotCount
        for costPoint in costPoints:
            startSlot = self.__timeSlotHelper.TimeToSlot(costPoint.startTime)
            endSlot = self.__timeSlotHelper.TimeToSlot(costPoint.endTime)
            thisCost = costPoint.cost * self.__timeSlotHelper.SlotDuration / 60 * chargingConfig.rate / 100
            if startSlot >= self.__timeSlotHelper.SlotCount:
                continue
            for i in range(startSlot, min(endSlot, self.__timeSlotHelper.SlotCount)):
                self.__costs[i] = thisCost

    def GetCost(self, slot: int, duration: int) -> float:
        count = self.__timeSlotHelper.DurationToSlotCount(duration)
        if (count == 0):
            return 0.0
        cost = 0.0
        for i in range(0, count[0]):
            thisslot = (slot + i)
            if thisslot >= self.__timeSlotHelper.SlotCount:
                raise Exception("candidate charging schedule is outside the charging window range")
            cost = cost + self.__costs[thisslot] * (count[1] if i == count[0] - 1 else 1.0)
        return cost


