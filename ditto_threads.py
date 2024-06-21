import threading
import time
import ditto_utils
import mysql_manager
import os
from dotenv import load_dotenv
from model.DittoUserInformation import DittoUserInformation

load_dotenv()
N_DAYS = int(os.getenv('N_DAYS'))
DITTO_BASE_URL = os.getenv('DITTO_BASE_URL')

class DittoCurrentStateThread(threading.Thread):
    def __init__(self, thingId):
        threading.Thread.__init__(self)
        self.clientId = thingId.split('-')[0]

    def run(self):
        time.sleep(5) #sleep 5 seconds to compensate Ditto's reading delay

        user = DittoUserInformation(self.clientId)
        values = user.calculateCurrentState()
        print(values)
        
        try:
            mysql_manager.insertValues(values)
        except:
            values = (values[2],values[3],values[4],values[5],values[1],values[0])
            mysql_manager.updateValues(values)

        data = mysql_manager.selectValues(self.clientId)
        print(data)
        if len(data) >= 10:
            features = ditto_utils.updateThing(data, user.generalInfo.features.goal.properties, user.generalInfo.features.preferences.properties)
            user.generalInfo.features = features
            user.uploadChanges()

class DittoGeneralInfoThread(threading.Thread):
    def __init__(self, clientId):
        threading.Thread.__init__(self)
        self.clientId = clientId

    def run(self):
        print