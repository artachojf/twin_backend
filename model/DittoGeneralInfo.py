from datetime import datetime

class Thing:
    def __init__(self, thingId: str, policyId: str, attributes, features) -> None:
        self.thingId = thingId
        self.policyId = policyId
        self.attributes = Attributes(**attributes)
        self.features = Features(**features)

    def to_dict(self):
        return {"thingId": self.thingId, "policyId": self.policyId,
                "attributes": self.attributes.to_dict(), "features": self.features.to_dict()}

class Attributes:
    def __init__(self, gender, height, weight, birthdate, runningDate) -> None:
        self.gender = gender
        self.height = int(height)
        self.weight = float(weight)
        split = birthdate.split('-')
        self.birthdate = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))
        split = runningDate.split('-')
        self.runningDate = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))

    def to_dict(self):
        return {"gender": self.gender, "height": self.height, "weight": self.weight,
                "birthdate": self.birthdate.strftime('%Y-%m-%d'), "runningDate": self.runningDate.strftime('%Y-%m-%d')}

class Features:
    def __init__(self, goal, trainingPlan, suggestions, preferences, fatigue) -> None:
        self.goal = Goal(**goal)
        self.trainingPlan = TrainingPlan(**trainingPlan)
        self.suggestions = Suggestions(**suggestions)
        self.preferences = Preferences(**preferences)
        self.fatigue = Fatigue(**fatigue)
    
    def to_dict(self):
        return {"goal": self.goal.to_dict(), "trainingPlan": self.trainingPlan.to_dict(),
                "suggestions": self.suggestions.to_dict(), "preferences": self.preferences.to_dict(),
                "fatigue": self.fatigue.to_dict()}

class Goal:
    def __init__(self, properties) -> None:
        self.properties = GoalProperties(**properties)
    
    def to_dict(self):
        return {"properties": self.properties.to_dict()}

class GoalProperties:
    def __init__(self, distance, seconds, estimations, date) -> None:
        self.distance = int(distance)
        self.seconds = int(seconds)
        split = date.split('-')
        self.date = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))
        list = []
        for x in estimations:
            list.append(Estimation(**x))
        self.estimations = list
        self.estimations.sort(key=lambda x: x.date, reverse=True)

    def to_dict(self):
        return {"distance": int(self.distance), "seconds": int(self.seconds), 
                "estimations": [x.to_dict() for x in self.estimations], "date": self.date.strftime('%Y-%m-%d')}

class Estimation:
    def __init__(self, date, seconds, goalReachDate) -> None:
        if type(date) is str:
            split = date.split('-')
            self.date = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))
        else:
            self.date = date
        self.seconds = seconds
        if goalReachDate is str:
            split = goalReachDate.split('-')
            self.goalReachDate = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))
        else:
            self.goalReachDate = goalReachDate

    def to_dict(self):
        if isinstance(self.date, datetime):
            self.date = self.date.strftime('%Y-%m-%d')
        if isinstance(self.goalReachDate, datetime):
            self.goalReachDate = self.goalReachDate.strftime('%Y-%m-%d')
        return {"date": self.date, "seconds": int(self.seconds), "goalReachDate": self.goalReachDate}

class TrainingPlan:
    def __init__(self, properties) -> None:
        self.properties = TrainingPlanProperties(**properties)

    def to_dict(self):
        return {"properties": self.properties.to_dict()}

class TrainingPlanProperties:
    def __init__(self, sessions) -> None:
        list = []
        for x in sessions:
            list.append(TrainingSession(**x))
        self.sessions = list
        self.sessions.sort(key=lambda x: x.day, reverse=False)

    def to_dict(self):
        return {"sessions": [x.to_dict() for x in self.sessions]}

class TrainingSession:
    def __init__(self, day, distance, times, rest, expectedTime, meanHeartRate) -> None:
        split = str(day).split(' ')[0].split('-')
        self.day = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))
        self.distance = distance
        self.times = times
        self.rest = rest
        self.expectedTime = expectedTime
        self.meanHeartRate = meanHeartRate

    def to_dict(self):
        return {"day": self.day.strftime('%Y-%m-%d'), "distance": int(self.distance), "times": int(self.times),
                "rest": int(self.rest), "expectedTime": int(self.expectedTime), "meanHeartRate": int(self.meanHeartRate)}

class Suggestions:
    def __init__(self, properties) -> None:
        self.properties = SuggestionProperties(**properties)

    def to_dict(self):
        return {"properties": self.properties.to_dict()}

class SuggestionProperties:
    def __init__(self, suggestions) -> None:
        list = []
        for x in suggestions:
            if type(x) == SuggestionDetail:
                list.append(x)
            else:
                list.append(SuggestionDetail(**x))
        self.suggestions = list

    def to_dict(self):
        return {"suggestions": [x.to_dict() for x in self.suggestions]}

class SuggestionDetail:
    def __init__(self, id, type, distance = 0, seconds = 0, date = 0, trainingDays = []) -> None:
        self.id = id
        self.type = type
        self.distance = distance
        self.seconds = seconds
        self.date = date
        self.trainingDays = trainingDays

    def to_dict(self):
        return {"id": self.id, "type": self.type, "distance": int(self.distance), "seconds": int(self.seconds),
                "date": self.date, "trainingDays": self.trainingDays}

class Preferences:
    def __init__(self, properties) -> None:
        self.properties = PreferencesProperties(**properties)
    
    def to_dict(self):
        return {"properties": self.properties.to_dict()}

class PreferencesProperties:
    def __init__(self, trainingDays: list[int]) -> None:
        self.trainingDays = trainingDays
    
    def to_dict(self):
        return {"trainingDays": self.trainingDays}

class Fatigue:
    def __init__(self, properties) -> None:
        self.properties = FatigueProperties(**properties)
    
    def to_dict(self):
        return {"properties": self.properties.to_dict()}

class FatigueProperties:
    def __init__(self, historic) -> None:
        list = []
        for i in historic:
            list.append(FatigueData(**i))
        list.sort(key=lambda x: x.date, reverse=True)
        self.historic = list
    
    def to_dict(self):
        return {"historic": [x.to_dict() for x in self.historic]}

class FatigueData:
    def __init__(self, ctl: float, date: str) -> None:
        self.ctl = ctl
        split = str(date).split(' ')[0].split('-')
        self.date = datetime(year=int(split[0]), month=int(split[1]),  day=int(split[2]))
    
    def to_dict(self):
        return {"ctl": self.ctl, "date": self.date.strftime('%Y-%m-%d')}