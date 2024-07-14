import threading
import time
from .ditto_utils import *
from .mysql_manager import *
import os
from dotenv import load_dotenv
from .model.DittoUserInformation import DittoUserInformation

load_dotenv()
DITTO_BASE_URL = os.getenv('DITTO_BASE_URL')

class DittoCurrentStateThread(threading.Thread):
    def __init__(self, thingId):
        threading.Thread.__init__(self)
        split = thingId.split('-')
        self.clientId = split[0]
        self.date = datetime(year=int(split[1]), month=int(split[2]), day=int(split[3]))

    def run(self):
        time.sleep(5) #sleep 5 seconds to compensate Ditto's reading delay

        user = DittoUserInformation(self.clientId)
        values = user.calculateCurrentState(self.date)
        print(values)
        
        try:
            insertValues(values)
        except:
            values = (values[2],values[3],values[4],values[5],values[1],values[0])
            updateValues(values)

        data = selectValues(self.clientId)
        print(data)
        if len(data) >= 10:
            updateThing(data, user)
            user.uploadChanges()

class DittoGeneralInfoThread(threading.Thread):
    def __init__(self, clientId):
        threading.Thread.__init__(self)
        self.clientId = clientId

    def run(self):
        print