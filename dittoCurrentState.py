from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()
DITTO_BASE_URL = os.getenv('DITTO_BASE_URL')

class dittoCurrentState:
    def __init__(self, thingId: str, strength: float, aerobic: float, anaerobic: float, fatigue: float, sleep: float):
        self.thingId = thingId
        self.strength = strength
        self.aerobic_endurance = aerobic
        self.anaerobic_endurance = anaerobic
        self.fatigue = fatigue
        self.sleep_rating = sleep

        split = thingId.split(':')[1].split('-')
        self.clientId = split[0]
        self.date = datetime(year=int(split[1]), month=int(split[2]), day=int(split[3]))

    def deleteThing(self) -> int:
        r = requests.delete(DITTO_BASE_URL + '/api/2/things/' + self.thingId)
        requests.delete(DITTO_BASE_URL + '/api/2/policies/' + self.thingId)
        return r.status_code
    
    def toList(self) -> list[float]:
        return [self.strength,self.aerobic_endurance,self.anaerobic_endurance,self.fatigue,self.sleep_rating]
    
    def isRest(self) -> bool:
        return self.strength == 0 and self.aerobic_endurance == 0 and self.anaerobic_endurance == 0 and self.fatigue == 0