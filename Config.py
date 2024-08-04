import xml.etree.ElementTree as ET
from datetime import datetime

class DatabaseConfig:
    def __init__(self, xmlnode: ET):
        self.server = xmlnode.find('server').text
        self.user = xmlnode.find('user').text
        self.password = xmlnode.find('password').text
        self.database = xmlnode.find('database').text

class ChargingConfig:
    def __init__(self, xmlnode: ET):
        self.chargewindowstart = datetime.strptime(xmlnode.find('windowstart').text, '%H:%M').time()
        self.chargewindowend = datetime.strptime(xmlnode.find('windowend').text, '%H:%M').time()
        self.slotduration = int(xmlnode.find('slotduration').text)
        self.rate = float(xmlnode.find('rate').text)

class Config:
    """ the following class contains configuration information relevant to the solution """
    def __init__(self):
       tree = ET.parse('config.xml')
       root = tree.getroot()
       self.database = DatabaseConfig(root.find('database'))
       self.charging = ChargingConfig(root.find('charging'))
    
       
       
       

    

