import datetime
import SchedulerKernel
import Reporting
import Database
import ElectricityPricer
import unittest
import parameterized

class TestEVScheduler(unittest.TestCase):
   def setUp(self):
       self.configCharging = self.__createChargeConfig()
       self.costAdjust = self.configCharging.rate / 100.0
       self.tariffItems = [ \
            Database.TariffItem((datetime.time(0, 0), datetime.time(3, 0), 25.0)), \
            Database.TariffItem((datetime.time(3, 0), datetime.time(6, 0), 20.0)), \
            Database.TariffItem((datetime.time(18, 0), datetime.time(21, 0), 35.0)), \
            Database.TariffItem((datetime.time(21, 0), datetime.time(0, 0), 30.0)), \
            ]
       self.__nextBus = 1

   def __createChargeConfig(self):
       mockCharger = unittest.mock.Mock()
       mockCharger.chargewindowstart = datetime.time(18, 0)
       mockCharger.chargewindowend = datetime.time(6, 0)
       mockCharger.slotduration = 30
       mockCharger.rate = 44.0
       return mockCharger
 
   def __getChargePoints(self, count: int) -> [int]:
       return range(1, count + 1)

   def __bus(self, soc: float, required: float) -> Database.BusStatus:
       id = self.__nextBus
       self.__nextBus = self.__nextBus + 1
       return Database.BusStatus((id, soc, required, "LE%02dOCV".format((id)), 200.0))

   def __createDatabase(self, chargingCount: int, buses: [Database.BusStatus]):
       mockDatabase = unittest.mock.Mock()
       mockDatabase.GetChargePoints = unittest.mock.Mock(return_value = self.__getChargePoints(chargingCount))
       mockDatabase.GetBusStatus = unittest.mock.Mock(return_value = buses)
       mockDatabase.GetElectricityCost = unittest.mock.Mock(return_value = self.tariffItems)
       return mockDatabase

   def __createChargingSchedule(self, slotCount: int, soc: float = 0.25, required: float = 0.75) -> Database.ChargingSchedule:
       result = Database.ChargingSchedule(self.__bus(soc, required))
       result.SlotCount = slotCount
       return result

   # the purpose of this routine it to reduce a set of slots to a single integer, so they can be 
   # compared
   def __reduceSlotList(self, slots: [int]) -> int:
       result = 0
       multiplier = 1
       for item in slots:
           result = result + item * multiplier
           multiplier = multiplier * 100
       return result

   def __createSceduler(self, chargePointCount: int, durations: [int]) -> SchedulerKernel.SchedulerKernel:
       helper = ElectricityPricer.TimeSlotHelper(self.configCharging)
       buses = list(self.__bus(.25, .75) for f in durations)
       database = self.__createDatabase(chargePointCount, buses)
       target = SchedulerKernel.SchedulerKernel(self.configCharging, database, "2023-12-01")
       schedule = target.RetrieveChargingSchedule()
       for i in range(0, len(schedule)):
           schedule[i].ChargeDuration = durations[i]
           schedule[i].SlotCount = helper.DurationToSlotCount(durations[i])[0]
       return target

   @parameterized.parameterized.expand([
        (0, 10, 35/6), 
        (1, 10, 35/6), 
        (5, 10, 35/6), 
        (6, 10, 30/6), 
        (9, 10, 30/6),
        (11, 10, 30/6),
        (12, 10, 25/6), 
        (14, 10, 25/6), 
        (17, 10, 25/6), 
        (18, 10, 20/6), 
        (22, 10, 20/6), 
        (23, 10, 20/6),
        (0, 45, 105/4),
        (3, 45, 105/4),
        (5, 45, 35/2 + 30/4),
        (6, 45, 90/4),
        (8, 45, 90/4),
        (11, 45, 15 + 25/4),
        (12, 45, 75/4), 
        (13, 45, 75/4),
        (17, 45, 25/2 + 5),
        (18, 45, 15.0),
        (20, 45, 15.0),
        (22, 45, 15.0),
        (0, 60, 35),
        (4, 60, 35), 
        (5, 60, 32.5), 
        (6, 60, 30), 
        (9, 60, 30), 
        (11, 60, 27.5), 
        (12, 60, 25), 
        (14, 60, 25), 
        (17, 60, 22.5), 
        (18, 60, 20), 
        (21, 60, 20), 
        (22, 60, 20),
        (0, 95, 95*35/60),
        (1, 95, 95*35/60),
        (2, 95, 95*35/60),
        (3, 95, 90*35/60 + 5 * 30/60), 
        (4, 95, 60*35/60 + 35 * 30/60), 
        (5, 95, 30 * 35/60 + 65*30/60),
        (6, 95, 95*30/60),
        (7, 95, 95*30/60),
        (8, 95, 95*30/60),
        (9, 95, 90*30/60 + 5 * 25/60),
        (10, 95, 60*30/60 + 35 * 25/60),
        (11, 95, 30 * 30/60 + 65*25/60),
        (12, 95, 95*25/60),
        (13, 95, 95*25/60), 
        (14, 95, 95*25/60), 
        (15, 95, 90*25/60 + 5 * 20/60), 
        (16, 95, 60*25/60 + 35 * 20/60), 
        (17, 95, 30 * 25/60 + 65*20/60),
        (18, 95, 95*20/60), 
        (19, 95, 95*20/60), 
        (20, 95, 95*20/60)
])
   def test_Pricer(self, slot: int, duration: int, expectedCost: float):
        # A
        ep = ElectricityPricer.ElectricityPricer(self.configCharging, self.tariffItems)

        # A&A
        self.assertAlmostEqual(expectedCost * self.costAdjust, ep.GetCost(slot, duration), 12)

   def test_IteratorFull(self):
       # A
       target = SchedulerKernel.Iterator([3, 4, 3], 10)

       # A&A
       self.assertListEqual([0, 3, 7], target.Slots)
       target.Next()
       self.assertTrue(target.Eof)
   
   def test_Iterator(self):
       # A
       target = SchedulerKernel.Iterator([3, 4, 3], 12)
       expectedSlotsList = [[0, 3, 7], \
           [0, 3, 8], \
           [0, 3, 9], \
           [0, 4, 8], \
           [0, 4, 9], \
           [0, 5, 9], \
           [1, 4, 8], \
           [1, 4, 9], \
           [1, 5, 9], \
           [2, 5, 9]]

       expectedSlots = set()
       for expectedSlot in expectedSlotsList:
           expectedSlots.add(self.__reduceSlotList(expectedSlot))

       # A
       actualSlots = set()
       while not target.Eof:
           slots = target.Slots
           self.assertEqual(3, len(slots))
           self.assertTrue(all(f >= 0 and f <= 9 for f in slots))
           self.assertTrue((slots[1] - slots[0]) >= 3)
           self.assertTrue((slots[2] - slots[1]) >= 4)
           actualSlots.add(self.__reduceSlotList(target.Slots))
           target.Next()

       # A
       self.assertSetEqual(expectedSlots, actualSlots)

   def test_IteratorTooManySlots(self):
       with self.assertRaises(Exception) as cm:
           target = SchedulerKernel.Iterator([3, 4, 3], 9)
       
       self.assertTrue('there are too many slots' in cm.exception.args[0])

   @parameterized.parameterized.expand([
        (0, datetime.time(18, 0)),
        (1, datetime.time(18,30)),
        (2, datetime.time(19,0)),
        (3, datetime.time(19,30)),
        (4, datetime.time(20,0)),
        (5, datetime.time(20,30)),
        (6, datetime.time(21,0)),
        (7, datetime.time(21,30)),
        (8, datetime.time(22,0)),
        (9, datetime.time(22,30)),
        (10, datetime.time(23,0)),
        (11, datetime.time(23,30)),
        (12, datetime.time(0,0)),
        (13, datetime.time(0,30)),
        (14, datetime.time(1,0)),
        (15, datetime.time(1,30)),
        (16, datetime.time(2,0)),
        (17, datetime.time(2,30)),
        (18, datetime.time(3,0)),
        (19, datetime.time(3,30)),
        (20, datetime.time(4,0)),
        (21, datetime.time(4,30)),
        (22, datetime.time(5,0)),
        (23, datetime.time(5,30)),
        (24, datetime.time(6,0)),
        (25, datetime.time(6,30)),
        (26, datetime.time(7,0)),
        (27, datetime.time(7,30)),
        (28, datetime.time(8,0)),
        (29, datetime.time(8,30)),
        (30, datetime.time(9,0))
])
   def test_Helper_SlotToTime(self, slot: int, expectedTime: datetime.time):
        # A
        helper = ElectricityPricer.TimeSlotHelper(self.configCharging)

        # A&A
        self.assertEqual(expectedTime, helper.SlotToTime(slot))

   @parameterized.parameterized.expand([
        (datetime.time(18, 0), 0),
        (datetime.time(18,10), 0),
        (datetime.time(18,30), 1),
        (datetime.time(18,50), 1),
        (datetime.time(19,0),  2),
        (datetime.time(19,30), 3),
        (datetime.time(20,0), 4),
        (datetime.time(23,15), 10),
        (datetime.time(23,55), 11),
        (datetime.time(0,0), 12),
        (datetime.time(0,5), 12),
        (datetime.time(3,40), 19),
        (datetime.time(5,5), 22),
        (datetime.time(5,30), 23),
        (datetime.time(5,59), 23)
])
   def test_Helper_TimeToSlot(self, candidateTime: datetime.time, expectedSlot: int):
       # A
       helper = ElectricityPricer.TimeSlotHelper(self.configCharging)
        
       # A&A
       self.assertEqual(expectedSlot, helper.TimeToSlot(candidateTime))

   @parameterized.parameterized.expand([
         (datetime.time(18, 0), 0),
         (datetime.time(18,10), 10),
         (datetime.time(18,30), 30),
         (datetime.time(18,50), 50),
         (datetime.time(19,0),  60),
         (datetime.time(19,30), 90),
         (datetime.time(20,0), 120),
         (datetime.time(23,15), 315),
         (datetime.time(23,55), 355),
         (datetime.time(0,0), 360),
         (datetime.time(0,5), 365),
         (datetime.time(3,40), 580),
         (datetime.time(5,5), 665),
         (datetime.time(5,30), 690),
         (datetime.time(5,59), 719)
])
   def test_Helper_OffsetToTime(self, expectedTime: datetime.time, offset: int):
        # A
        helper = ElectricityPricer.TimeSlotHelper(self.configCharging)

        # A&A
        self.assertEqual(expectedTime, helper.OffsetToTime(offset))

   @parameterized.parameterized.expand([
       (0, 0, 0.0),
       (1, 1, 1/30),
       (10, 1, 1/3),
       (15, 1, 0.5),
       (30, 1, 1.0),
       (45, 2, 0.5),
       (60, 2, 1.0),
       (70, 3, 1/3),
       (85, 3, 5/6),
       (90, 3, 1.0),
       (120, 4, 1.0),
       (160, 6, 1/3)
])
   def test_Helper_DurationToSlotCount(self, duration: int, expectedSlotCount: int, expectedLastRatio: float):
        # A
        helper = ElectricityPricer.TimeSlotHelper(self.configCharging)

        # A
        result = helper.DurationToSlotCount(duration)

        # A
        self.assertEqual(expectedSlotCount, result[0])
        self.assertAlmostEqual(expectedLastRatio, result[1], 12)

   @parameterized.parameterized.expand([
            (datetime.time(18, 0), 0, 0),
            (datetime.time(18, 10), 0, 10),
            (datetime.time(18, 30), 0, 30),
            (datetime.time(18, 55), 0, 55),
            (datetime.time(19, 15), 0, 75),
            (datetime.time(20, 0), 0, 120),
            (datetime.time(20, 50), 0, 170),
            (datetime.time(22, 00), 0, 240),
            (datetime.time(0, 40), 0, 400),
            (datetime.time(5, 0), 0, 660),
            (datetime.time(18, 40), 1, 10),
            (datetime.time(19, 00), 1, 30),
            (datetime.time(19, 25), 1, 55),
            (datetime.time(22, 30), 1, 240),
            (datetime.time(5, 30), 1, 660),
            (datetime.time(20, 30), 5, 0),
            (datetime.time(20, 40), 5, 10),
            (datetime.time(21, 0), 5, 30),
            (datetime.time(23, 20), 5, 170),
            (datetime.time(3, 10), 5, 400),
            (datetime.time(22, 40), 9, 10),
            (datetime.time(23, 00), 9, 30),
            (datetime.time(23, 25), 9, 55),
            (datetime.time(2, 30), 9, 240),
            (datetime.time(23, 30), 11, 0),
            (datetime.time(23, 40), 11, 10),
            (datetime.time(0, 0), 11, 30),
            (datetime.time(2, 20), 11, 170),
            (datetime.time(6, 10), 11, 400),
            (datetime.time(0, 0), 12, 0),
            (datetime.time(0, 30), 12, 30),
            (datetime.time(0, 55), 12, 55),
            (datetime.time(4, 10), 12, 250),
            (datetime.time(3, 30), 19, 0),
            (datetime.time(3, 40), 19, 10),
            (datetime.time(4, 0), 19, 30),
            (datetime.time(6, 20), 19, 170),
            (datetime.time(5, 30), 23, 0),
            (datetime.time(5, 40), 23, 10),
            (datetime.time(6, 0), 23, 30)
])
   def test_Helper_GetEndTime(self, expectedTime: datetime.time, slot: int, duration: int):
       # A
       helper = ElectricityPricer.TimeSlotHelper(self.configCharging)

       # A&A
       self.assertEqual(expectedTime, helper.GetEndTime(slot, duration))

   def test_ChargingPointData_large(self):
       # Arrange
       target = SchedulerKernel.ChargingPointData(333, 12)
       item1 = self.__createChargingSchedule(13)

       # act & assert
       self.assertEqual(12, target.SlotsAvailable)
       self.assertFalse(target.Allocate(item1))
       self.assertEqual(12, target.SlotsAvailable)
       self.assertEqual(0, len(target.BusesAllocated))

       # act & assert
       item2 = self.__createChargingSchedule(12)
       self.assertTrue(target.Allocate(item2))
       self.assertEqual(0, target.SlotsAvailable)
       self.assertListEqual([item2.BusStatus], list(f.BusStatus for f in target.BusesAllocated))

       # act & assert
       item3 = self.__createChargingSchedule(1)
       self.assertFalse(target.Allocate(item3))
       self.assertEqual(0, target.SlotsAvailable)
       self.assertListEqual([item2.BusStatus], list(f.BusStatus for f in target.BusesAllocated))
  
   def test_ChargingPointData_multiple(self):
       # Arrange
       target = SchedulerKernel.ChargingPointData(1, 12)
       item1 = self.__createChargingSchedule(4)
       item2 = self.__createChargingSchedule(3)
       item3 = self.__createChargingSchedule(2)
       item4 = self.__createChargingSchedule(4)
       expectedSchedule = [item1.BusStatus, item2.BusStatus, item3.BusStatus]

       # act
       self.assertTrue(target.Allocate(item1))
       self.assertTrue(target.Allocate(item2))
       self.assertTrue(target.Allocate(item3))

       # assert
       self.assertEqual(3, target.SlotsAvailable)
       self.assertListEqual(expectedSchedule, list(f.BusStatus for f in target.BusesAllocated))

       # act/assert
       self.assertFalse(target.Allocate(item4))
       self.assertEqual(3, target.SlotsAvailable)
       self.assertListEqual(expectedSchedule, list(f.BusStatus for f in target.BusesAllocated))

   @parameterized.parameterized.expand([
        (1, [300], [1]),
        (1, [220, 200, 190, 45], [1, 1, 1, 1]),
        (2, [220, 200, 190, 100, 70, 40], [1, 2, 2, 1, 1, 2]),
        (3, [220, 200, 170, 100, 70, 40], [1, 2, 3, 3, 2, 1]),
        (1, [300, 200, 150, 90, 60], [1, 1, 1, 0, 1]),
        (1, [300, 200, 150, 60, 60], [1, 1, 1, 1, 0]),
        (2, [300, 200, 190, 150, 140, 130, 100, 100, 60, 40, 30], [1, 2, 2, 1, 2, 1, 2, 1, 0, 0, 2])
  ])
   def test_Scheduler_Allocate_Succeeds(self, chargePointCount: int, durations: [int], expectedIndexes: [int]):
       # A
       target = self.__createSceduler(chargePointCount, durations)
       expectedFailCount = expectedIndexes.count(0)
    
       #A
       result = target.AllocateChargingPoints()
 
       #A
       self.assertEqual(expectedFailCount, result)
       self.assertListEqual(expectedIndexes, list(f.ChargingPoint for f in target.RetrieveChargingSchedule()))
       for i in range(0, chargePointCount):
           expectedBuses = list(target.RetrieveChargingSchedule()[f[1]] for f in filter(lambda x: x[0] == i+1,([expectedIndexes[n], n] for n in range(0, len(expectedIndexes)))))
           chargingPoint = next((c for c in target.RetrieveChargingPoints() if c.ChargingPointId == i + 1), None)
           self.assertListEqual(expectedBuses, chargingPoint.BusesAllocated)

   @parameterized.parameterized.expand([
        ([30], [(18, 23)], [10.0]),
        ([180], [(18, 18)], [60.0]),
        ([240], [(16, 16)], [85.0]),
        ([90, 60], [(18, 19), (21, 22)], [30.0, 20.0]),
        ([150, 90], [(19, 19), (16, 16)], [50.0, 35.0]), 
        ([180, 120, 30], [(13, 13), (19, 19), (23, 23)], [72.5, 40.0, 10.0]),
  ])
   def test_Scheduler_FindBestChargingTime(self, durations: [int], expectedSlots: [(int, int)], expectedCost: [float]):
       # A
       target = self.__createSceduler(1, durations)
       target.AllocateChargingPoints()

       # A
       target.FindBestChargingTimes()

       #A
       schedule = target.RetrieveChargingSchedule()
       indexedItems = list([schedule[n], n] for n in range(0, len(schedule)))
       self.assertTrue(all(f[0].ChargeSlot >= expectedSlots[f[1]][0] and f[0].ChargeSlot <= expectedSlots[f[1]][1] for f in indexedItems))
       self.assertTrue(all(abs(expectedCost[f[1]] * self.costAdjust - f[0].ChargeCost) < 1e-12 for f in indexedItems))

   def test_scheduler_DurationCalculation(self):
       # Arrange
       buses = [ self.__bus(.5, .75), self.__bus(.6, .6), self.__bus(0, 1), self.__bus(.1, .9), self.__bus(.25, .35)]
       expectedDurations = [ 273, 245, 95, 55, 27 ]
       expectedSlotCount = [ 10, 9, 4, 2, 1 ]
       database = self.__createDatabase(5, buses)
       target = SchedulerKernel.SchedulerKernel(self.configCharging, database, "2023-12-01")
       sortedBuses = [buses[2], buses[3], buses[0], buses[4], buses[1]]

       # Act
       target.CalculateChargingDurations()
       result = target.RetrieveChargingSchedule()

       # Assert
       self.assertListEqual(sortedBuses, list(f.BusStatus for f in result))
       self.assertListEqual(expectedDurations, list(f.ChargeDuration for f in result))
       self.assertListEqual(expectedSlotCount, list(f.SlotCount for f in result))

   @parameterized.parameterized.expand([
        (1, [300], [0], 165.0),
        (1, [220, 200, 190, 45], [0, 8, 15, 22], 125.0 + (60.0 + 100.0/3) + (37.5+ 100.0/3) + 15.0),
        (2, [220, 200, 190, 100, 70, 40], [0, 0, 7, 8, 12, 14], 125.0 + 115 + (75 + 50/3) + 50 + (7*25/6) + 50/3),
        (3, [220, 200, 170, 100, 70, 40], [0, 0, 0, 6, 7, 8], 125 + 115 + 17*35/6 + 50 + 35 + 20),
        (1, [300, 200, 150, 90, 60], [0, 10, 17, -1, 22], 165 + (30 + 175/3) + (12.5 + 40) + 0 + 20),
        (1, [300, 200, 150, 60, 60], [0, 10, 17, 22, -1], 165 + (30 + 175/3) + (12.5 + 40) + 20 + 0),
        (2, [300, 200, 190, 150, 140, 130, 100, 100, 60, 40, 30], [0, 0, 7, 10, 14, 15, 19, 20, -1, -1, 23], 165 + 115 + (75+ 50/3) + (30+37.5) + (50 + 20/3) + (37.5+40/3) + 100/3 + 100/3 + 0 + 0 + 10)
  ])
   def test_Scheduler_BaselineCost(self, chargePointCount: int, durations: [int], unused: [int], expectedCost: [float]):
       # A
       target = self.__createSceduler(chargePointCount, durations)
       
       # A
       result = target.CalculateBaselineCost()

       #A
       self.assertAlmostEqual(expectedCost * self.costAdjust, result, 12)

# main
if (__name__ == '__main__'):
   unittest.main()

