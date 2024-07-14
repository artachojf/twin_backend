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

    def uploadChanges(self):
        requests.put(DITTO_BASE_URL + '/api/2/things/' + self.generalInfo.thingId,
                     data=json.dumps(self.generalInfo.to_dict()))

    def trainingParameters(self) -> dict:
        distance, time, atDistance, atTime = 0.0, 0.0, 0.0, 0.0

        for currentState in self.trainings:
            session = currentState.features.trainingSession.properties
            distance += (session.zone1.distance + session.zone2.distance + session.zone3.distance)
            time += (session.zone1.time + session.zone2.time + session.zone3.time)
            atDistance += session.zone2.distance
            atTime += session.zone2.time

        days = (datetime.now() - self.trainings[len(self.trainings)-1].getDate()).days
        return {
            'weeklyDistance': ((distance / days) * 7),
            'weeklyTrainingDays': ((float(len(self.trainings)) / days) * 7),
            'weeklyTrainingTime': ((time / days) * 7),
            'trainingSpeed': (distance / time),
            'anaerobicThresholdSpeed': (atDistance / atTime)
        }

    def calculateCurrentState(self, date: datetime) -> tuple[datetime,str,float,float,float,float]:

        bmi = self.generalInfo.attributes.weight / ((self.generalInfo.attributes.height / 100) ** 2) #kg/m2
        runningExp = (date - self.generalInfo.attributes.runningDate).days / 365 #year
        age = (date - self.generalInfo.attributes.birthdate).days / 365 #year

        parameters = self.trainingParameters()
        weeklyDistance = parameters['weeklyDistance'] / 1000 #km/wk
        weeklyTrainingDays = parameters['weeklyTrainingDays'] #d/wk
        weeklyTrainingTime = parameters['weeklyTrainingTime'] / 3600 #h/wk
        trainingSpeed = msToKmh(parameters['trainingSpeed']) #km/h
        anaerobicThresholdSpeed = parameters['anaerobicThresholdSpeed'] #m/s

        bodyFat = 0.0 #%
        if self.generalInfo.attributes.gender != 'Female': bodyFat += (1.2*bmi) + (0.23*age) - 16.2
        if self.generalInfo.attributes.gender != 'Male': bodyFat += (1.20*bmi) + (0.23*age) - 5.4
        if self.generalInfo.attributes.gender != 'Female' and self.generalInfo.attributes.gender != 'Male': bodyFat /= 2
    
        fourtyTwoKm = self.current42kPrediction(weeklyDistance, trainingSpeed, bodyFat, anaerobicThresholdSpeed, age, hoursToMinutes(weeklyTrainingTime/weeklyTrainingDays))
        twentyOneKm = self.current21kPrediction(bodyFat, trainingSpeed, fourtyTwoKm)
        tenKm = self.current10kPrediction(bmi, weeklyDistance, weeklyTrainingDays, weeklyTrainingTime, runningExp, twentyOneKm)
        fiveKm = self.current5kPrediction(tenKm)
        
        return (date.strftime('%Y-%m-%d'),self.clientId,fiveKm,tenKm,twentyOneKm,fourtyTwoKm)

    '''
    1. Daniels' formula
    '''
    def current5kPrediction(self, tenKmTime: float) -> float:
        return danielsFormula(10000, tenKmTime, 5000)

    '''
    1. Suwunkan, et al. Prediction of 10km running time in recreatinal runners
    2. Daniels' formula
    '''
    def current10kPrediction(self, bmi: float, weeklyDistance: float, weeklyTrainingDays: float, weeklyTrainingTime: float, runningExp: float, twentyOneKm: float) -> float:
        sum = 0
        sum += (71.9 + (0.751*bmi) - (0.188*weeklyDistance) - (3.048*weeklyTrainingDays) + (0.302*weeklyTrainingTime) - (0.982*runningExp)) * 60
        sum += danielsFormula(21097, twentyOneKm, 10000)
        return sum / 2

    '''
    1. Knechtle et al. Prediction of half-marathon race time in recreational female and male runners
    2. Daniels' formula
    '''
    def current21kPrediction(self, bodyFat: float, trainingSpeed: float, fourtyTwoKm: float) -> float:
        sum = 0
        if self.generalInfo.attributes.gender != 'Female': sum += (142.7 + (1.158*bodyFat) - (5.223*trainingSpeed)) * 60
        if self.generalInfo.attributes.gender != 'Male': sum += (168.7 + (1.077*bodyFat) - (7.556*trainingSpeed)) * 60
        if self.generalInfo.attributes.gender != 'Female' and self.generalInfo.attributes.gender != 'Male': sum /= 2
        sum += danielsFormula(42195, fourtyTwoKm, 21097)
        return sum / 2

    '''
    1. Tanda G. Prediction of marathon performance time
    2. Barandun et al.
    3. Fohrenbach et al.
    4. Takeshima et al.
    '''
    def current42kPrediction(self, weeklyDistance, trainingSpeed, bodyFat, anaerobicThresholdSpeed, age, workoutDuration) -> float:
        sum = 0
        sum += (11.03 + (98.46*(2 ** (-0.0053*weeklyDistance))) + (0.387*kmhToSeckm(trainingSpeed))  + (0.1*(2 ** (0.23*bodyFat)))) * 60
        sum += (326.3 + (2.394*bodyFat) - (12.06*trainingSpeed)) * 60 #for men
        sum += (42.195/(-0.389 + (1.046*anaerobicThresholdSpeed))*60) #anaThrSpeed m/s
        sum += (5.858 - (0.052*age) + (0.067*workoutDuration)) * 60 #workoutDuration min
        sum += kmhToSeckm(anaerobicThresholdSpeed*1.013 - 0.944)*42.195
        return sum / 4
    
def msToKmh(x: float) -> float: return (x*3.6)

def kmhToSeckm(x: float) -> float: return (x ** -1) * 3600

def hoursToMinutes(x: float) -> float: return x*60

def danielsFormula(sourceDistance: float, seconds: float, targetDistance: float) -> float:
    critical_velocity = sourceDistance / (seconds + 60) #m/s
    return targetDistance / critical_velocity - 60