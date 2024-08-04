import Config
import Database
import datetime
import sys
import os
import mysql.connector
import csv
import itertools
import random
import time
       
class LoadPreCalcData(object):
    """description of class"""
    def __init__(self, config: Config.ChargingConfig, db : Database.Database, date: str):
        self.__config = config
        self.__database = db
        self.__date = date
        self.__preCalcData = []
 
    def LoadData(self):
        i = 1
        chargeDataFilename = 'input-files\chargeData_' + self.__date + '.csv'
        CHUNK=10_000
        sleepTime = 5 #  when testing set to 5 seconds, in reality set it to 60 seconds
  
        while i > 0:
            if  os.path.exists(chargeDataFilename):
                i = 0  

                with open (chargeDataFilename, 'r') as csvfile:
                    csv_data =  csv.reader(csvfile, delimiter =',')
                    self.__preCalcData = list(Database.PreCalcData(f) for f in list(itertools.islice(csv_data, CHUNK)))
                    self.__database.SavePreCalcData(self.__preCalcData, self.__date)
            else:
                time.sleep(sleepTime) 
                print(" Please check. Input file," ,chargeDataFilename, "is not present. Will try again in", str(sleepTime), "seconds.")
                
    def GenerateRandomData(self, randomArgs):
        random.seed()
        for i in range(0, randomArgs.buscount):
            soc = randomArgs.minsoc + random.random() * (randomArgs.maxsoc - randomArgs.minsoc)
            req = randomArgs.minreq + random.random() * (randomArgs.maxreq - randomArgs.minreq)
            self.__preCalcData.append(Database.PreCalcData((self.__date, i + 1, soc, req )))
            
        self.__database.SavePreCalcData(self.__preCalcData, self.__date)            
                    
