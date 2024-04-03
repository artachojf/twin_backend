import requests
import os
from dotenv import load_dotenv
import json
from .DittoGeneralInfo import Thing as DittoGeneralInfo
from .DittoCurrentState import Thing as DittoCurrentState
from datetime import datetime

load_dotenv()
DITTO_BASE_URL = os.getenv('DITTO_BASE_URL')
DITTO_THING_PREFIX = os.getenv('DITTO_THING_PREFIX')

class DittoUserInformation:
    def __init__(self, clientId: str) -> None:
        self.clientId = clientId

        r = requests.get(DITTO_BASE_URL + '/api/2/things/' + DITTO_THING_PREFIX + ':' + self.clientId)
        response = json.loads(r.text)
        self.generalInfo = DittoGeneralInfo(**response)

        r = requests.get(DITTO_BASE_URL + '/api/2/search/things?filter=eq(attributes/googleId,"'+ self.clientId +'")&option=size(100)')
        response = json.loads(r.text)
        self.trainings = []
        for x in response['items']:
            self.trainings.append(DittoCurrentState(**x))
        self.trainings.sort(key=lambda x: x.getDate(), reverse=True)

    def calculateCurrentState(self) -> tuple[datetime,str,float,float,float,float]:
    
        fiveKm = self.current5kPrediction()
        tenKm = self.current10kPrediction()
        twentyOneKm = self.current21kPrediction()
        fourtyTwoKm = self.current42kPrediction()
        
        #TODO: Training day may not be today (no internet connection...)
        return (datetime.now().strftime('%Y-%m-%d'),self.clientId,fiveKm,tenKm,twentyOneKm,fourtyTwoKm)

    def current5kPrediction(self) -> float:
        #TODO: Use mathematical models to calculate a prediction for a 5k race
        return 0.0

    def current10kPrediction(self) -> float:
        #TODO: Use mathematical models to calculate a prediction for a 10k race
        return 0.0

    def current21kPrediction(self) -> float:
        #TODO: Use mathematical models to calculate a prediction for a 21k race
        return 0.0

    def current42kPrediction(self) -> float:
        #TODO: Use mathematical models to calculate a prediction for a 42k race
        return 0.0