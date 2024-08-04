import Config
import Database
import LoadPreCalcData
import SchedulerKernel
import Reporting
import datetime
import sys
import argparse
import time

def main():
    startTime = time.time()
    c = Config.Config()
    parser = argparse.ArgumentParser(
                    prog='EVScheduler',
                    description='This program calculates the optimal charging schedules for a fleet of electric buses',
                    epilog='')
    parser.add_argument('-d', '--date', default=datetime.datetime.today().strftime('%Y-%m-%d'), help='the date to look for the data')           # positional argument
    parser.add_argument('-r', '--randomise', help='randomly generate charging requirements instead of reading from a file', action='store_true')      # option that takes a value
    parser.add_argument('-rbc', '--buscount', type=int, default=10, help='the number of buses when randomly generating data. Default is 10')
    parser.add_argument('-rsl', '--minsoc', type=float, default=0.05, help='the minimum state of charge when randomly generating data. default is 5%')
    parser.add_argument('-rsh', '--maxsoc', type=float, default=0.3, help='the maximum state of charge when randomly generating data. default is 30%')
    parser.add_argument('-rrl', '--minreq', type=float, default=0.6, help='the minimum required charge when randomly generating data. default is 60%')
    parser.add_argument('-rrh', '--maxreq', type=float, default=0.95, help='the maximum required charge when randomly generating data. default is 95%')
 
    args = parser.parse_args()
      
    date = args.date
    d = Database.Database(c.database)

    ld = LoadPreCalcData.LoadPreCalcData(c.database,d,date)
    if (args.randomise):
       ld.GenerateRandomData(args)
    else:
       ld.LoadData()
    
    sk = SchedulerKernel.SchedulerKernel(c.charging,d, date)
    sk.CalculateSchedule()
    
    reporter = Reporting.Reporting(c.charging, d)
    reporter.CreateChargingReport(date)
    reporter.CreateDepotManagersReport(date)
    
    endTime = time.time()
    timeTaken = endTime - startTime
    print("Time taken = ", str(timeTaken))
    
if __name__ == '__main__':
    main()
    

        








