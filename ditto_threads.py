import pandas as pd
import requests
import threading
import json
import requests
import time
import ditto_utils
import mysql_manager
import os
from dotenv import load_dotenv

load_dotenv()
N_DAYS = int(os.getenv('N_DAYS'))
DITTO_BASE_URL = os.getenv('DITTO_BASE_URL')

class dittoCurrentStateThread(threading.Thread):
    def __init__(self, thingId):
        threading.Thread.__init__(self)
        self.clientId = thingId.split('-')[0]

    def run(self):
        time.sleep(5) #sleep 5 seconds to compensate Ditto's reading delay
        r = requests.get(DITTO_BASE_URL + '/api/2/search/things?filter=eq(attributes/googleId,"'+ self.clientId +'")&option=size(100)')
        response = json.loads(r.text)
        list = ditto_utils.getObjectList(response['items'])
        list.sort(key=lambda x: x.date, reverse=True)

        values = ditto_utils.calculateCurrentState(list)
        print(values)
        try:
            mysql_manager.insertValues(values)
        except:
            values = (values[2],values[3],values[4],values[5],values[6],values[1],values[0])
            mysql_manager.updateValues(values)

        data = mysql_manager.selectValues(self.clientId)
        print(data)
        if len(data) >= 10:
            prediction = ditto_utils.getPredictions(data, N_DAYS) #we should read the training goal previously
            print(prediction)
            #TODO: Generate training plan and upload to Ditto
            #TODO: Generate suggestions and upload to Ditto

class dittoGeneralInfoThread(threading.Thread):
    def __init__(self, clientId):
        threading.Thread.__init__(self)
        self.clientId = clientId

    def run(self):
        print