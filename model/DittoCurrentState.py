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
    
class Attributes:
    def __init__(self, googleId) -> None:
        self.googleId = googleId

class Features:
    def __init__(self, trainingSession, sleepRating) -> None:
        self.trainingSession = TrainingSession(**trainingSession)
        self.sleepRating = SleepRating(**sleepRating)

class TrainingSession:
    def __init__(self, properties) -> None:
        self.properties = TrainingSessionProperties(**properties)

class TrainingSessionProperties:
    def __init__(self, zone1, zone2, zone3, rest) -> None:
        self.zone1 = TrainingSessionZone(**zone1)
        self.zone2 = TrainingSessionZone(**zone2)
        self.zone3 = TrainingSessionZone(**zone3)
        self.rest = TrainingSessionZone(**rest)
    
class TrainingSessionZone:
    def __init__(self, avgHr, time, distance):
        self.avgHr = avgHr
        self.time = time
        self.distance = distance

class SleepRating:
    def __init__(self, properties) -> None:
        self.properties = SleepRatingProperties(**properties)

class SleepRatingProperties:
    def __init__(self, overall) -> None:
        self.overall = overall