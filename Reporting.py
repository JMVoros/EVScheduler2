import ElectricityPricer
import Database
import Config
import datetime

class Reporting(object):
    """description of class"""
    def __init__(self, config: Config.ChargingConfig, database: Database.Database):
       self.helper = ElectricityPricer.TimeSlotHelper(config)
       self.database = database

    def __FormatTime(self, offset: int) -> str:
        return self.helper.OffsetToTime(offset).strftime("%H:%M")
 
    def CreateChargingReport(self, date: str):
        allocated = self.database.GetChargingReportByStation(date, True)
        filename = "reports\EV-Cost-and-Charging-Schedule-" + date + ".txt"
        f = open(filename, "w")

        f.write("\n EV Cost and Charging Schedule Report for " + date  + "\n")
        f.write(" ==================================================="  + "\n")
        f.write("" + "\n")
        f.write(" Charge Point  Start    End      Bus Number  SoC at   Charge     Amount to   Soc on      Charge        Cost" + "\n")
        f.write(" Id            Time     Time     Plate       start    Required   Change      Completion  Time(mins)" + "\n")
        lastcharger = 0
        totalDuration = 0
        totalCost = 0.0
        totalEVs = 0
        
        for item in allocated:
            id = "" if lastcharger == item.ChargingPoint else str(item.ChargingPoint)
            if (item.CapacityRequired+0.1)  > 1.0:
                socCompletion = 1.0 
                amountToCharge = (1.0 - item.Soc)
            elif (item.Soc >= (item.CapacityRequired + 0.1)):
                socCompletion = item.Soc 
                amountToCharge = 0.0 
            else:
                socCompletion = (item.CapacityRequired + 0.1) 
                amountToCharge = (item.CapacityRequired - item.Soc+ 0.1)
            line = " %s           %s    %s    %7s     %4.1f%%    %4.lf%%       %4.1f%%       %5.1f%%      %s        %5.2f\n" % (id.ljust(3), self.__FormatTime(item.ChargeTime), self.__FormatTime(item.ChargeEndTime), item.Registration, item.Soc * 100.0, item.CapacityRequired * 100.0,amountToCharge * 100.0, socCompletion * 100.0 ,str(item.ChargeDuration).rjust(5),  item.ChargeCost)
            f.write(line)
            lastcharger = item.ChargingPoint
            totalDuration = totalDuration + item.ChargeDuration
            totalCost = totalCost + item.ChargeCost
            totalEVs = totalEVs + 1
        f.write("                                                                                           -----      -------\n")
        f.write(" Totals:                                                                                   %s      %.2f\n" % (str(totalDuration).ljust(5), totalCost))
        f.write("\n")
        unallocated = self.database.GetChargingReportByStation(date, False)
        if len(unallocated) == 0 :
            f.write(" *** ALL " + str(totalEVs) + " BUSES SUCCESSFULLY SCHEDULED FOR CHARGING USING " + str(lastcharger) + " CHARGE POINTS ***\n")
        else:
            f.write(" *** WARNING: CAPACITY OF " + str(lastcharger) + " CHARGE POINTS EXCEEDED! ***\n")
            f.write (" *** DUE TO INSUFFICIENT CAPACITY,THE BUSES LISTED BELOW COULD NOT BE SCHEDULED:\n\n")
            f.write(" Bus Number  Soc at     Charge      Charge\n")
            f.write(" Plate       start      Required    Time (mins)\n")
            for item in unallocated:
                line = " %7s     %2.1f%%      %2.1f%%       %s" % (item.Registration, item.Soc * 100.0, item.CapacityRequired * 100.0, str(item.ChargeDuration).ljust(3))
                f.write(line + "\n")
                
        f.write("\n\n")        
        chargeNotNeeded = self.database.GetChargingReportChargeNotNeeded(date, False)
        if len(chargeNotNeeded) > 0:
            f.write (" *** NOTE: THE BUSES LISTED BELOW HAVE SUFFICIENT CHARGE AND DO NOT NEED CHARGING:\n\n")
            f.write(" Bus Number  Soc at     Charge   \n")
            f.write(" Plate       start      Required \n")
            for item in chargeNotNeeded :
                line = " %7s     %2.1f%%      %2.1f%%  " % (item.Registration, item.Soc * 100.0, item.CapacityRequired * 100.0)
                f.write(line + "\n")
        f.write("\n")
        f.close()
        
        f = open(filename, "r")
        print(f.read())
        f.close()

    def CreateDepotManagersReport(self, date: str):
        activities = self.database.GetActivityReport(date)
        filename = "reports\Depot-Managers-Activity-Schedule-" + date + ".txt"
        f = open(filename, "w")
        f.write("\n Depot Manager's Activity Schedule Report for " + date + "\n")
        f.write(" =======================================================\n")
        f.write("\n")
        f.write(" Time      Bus Number    Charge Point   Activity\n")
        f.write("           Plate         Id\n")
        for item in activities:
            activity = "Connect" if item.Connect else "Disconnect"
            line = " %s     %7s        %s           %s" % (self.__FormatTime(item.Time), item.Registration, str(item.ChargingPoint).ljust(3), activity)
            f.write(line + "\n")

        f.write("\n")
        f.close()
        
        f = open(filename, "r")
        print(f.read())
        f.close()