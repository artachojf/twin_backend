from datetime import datetime
import os
from dotenv import load_dotenv
import requests

load_dotenv()
N_DAYS = int(os.getenv('N_DAYS'))
DITTO_BASE_URL = os.getenv('DITTO_BASE_URL')

class Thing:
    def __init__(self, thingId: str, policyId: str, attributes, features):
        self.thingId = thingId
        self.policyId = policyId
        self.attributes = Attributes(**attributes)
        self.features = Features(**features)

    def deleteThing(self) -> int:
        r = requests.delete(DITTO_BASE_URL + '/api/2/things/' + self.thingId)
        requests.delete(DITTO_BASE_URL + '/api/2/policies/' + self.policyId)
        return r.status_code
    
    def getDate(self) -> datetime:
        split = self.thingId.split('-')
        return datetime(year=int(split[1]), month=int(split[2]), day=int(split[3]))
    
    def calculate_trimp(self) -> float:
        zones = self.features.trainingSession.properties
        return zones.zone1.time*1 + zones.zone2.time*2 + zones.zone3.time*3
    
    def calculate_ctl_coef(self) -> float:
        ideal_light_sleep = 4*60*60
        ideal_deep_sleep = 1.5*60*60
        ideal_rem_sleep = 2*60*60

        # Normalize total steps
        normalized_steps = min(1, self.features.stepsRecord.properties.count / 10000)

        # Calculate deviations from ideal sleep durations (penalty for less than ideal sleep)
        light_sleep_deviation = max(0, (ideal_light_sleep - self.features.sleepSession.properties.light) / ideal_light_sleep)
        deep_sleep_deviation = max(0, (ideal_deep_sleep - self.features.sleepSession.properties.deep) / ideal_deep_sleep)
        rem_sleep_deviation = max(0, (ideal_rem_sleep - self.features.sleepSession.properties.rem) / ideal_rem_sleep)

        # Weight the contribution of different factors (can be adjusted)
        weighted_steps = 0.5 * normalized_steps
        weighted_light_sleep = 0.1 * light_sleep_deviation
        weighted_deep_sleep = 0.2 * deep_sleep_deviation
        weighted_rem_sleep = 0.2 * rem_sleep_deviation

        # Combine weighted factors and limit the coefficient to the desired range
        fatigue_coef = weighted_steps + weighted_light_sleep + weighted_deep_sleep + weighted_rem_sleep
        return fatigue_coef
    
class Attributes:
    def __init__(self, googleId, date) -> None:
        self.googleId = googleId

class Features:
    def __init__(self, trainingSession, sleepSession, stepsRecord) -> None:
        self.trainingSession = TrainingSession(**trainingSession)
        self.sleepSession = SleepSession(**sleepSession)
        self.stepsRecord = StepsRecord(**stepsRecord)

class TrainingSession:
    def __init__(self, properties) -> None:
        self.properties = TrainingSessionProperties(**properties)

class TrainingSessionProperties:
    def __init__(self, zone1, zone2, zone3, rest, laps) -> None:
        self.zone1 = TrainingSessionZone(**zone1)
        self.zone2 = TrainingSessionZone(**zone2)
        self.zone3 = TrainingSessionZone(**zone3)
        self.rest = TrainingSessionZone(**rest)
        list = []
        for x in laps:
            list.append(TrainingLap(**x))
        self.laps = list
    
class TrainingSessionZone:
    def __init__(self, avgHr, time, distance):
        self.avgHr = avgHr
        self.time = time
        self.distance = distance

class TrainingLap:
    def __init__(self, startTime, distance, time) -> None:
        self.startTime = startTime
        self.distance = distance
        self.time = time

class SleepSession:
    def __init__(self, properties) -> None:
        self.properties = SleepSessionProperties(**properties)

class SleepSessionProperties:
    def __init__(self, awake, light, deep, rem) -> None:
        self.awake = awake
        self.light = light
        self.deep = deep
        self.rem = rem

class StepsRecord:
    def __init__(self, properties) -> None:
        self.properties = StepsRecordProperties(**properties)

class StepsRecordProperties:
    def __init__(self, count) -> None:
        self.count = count