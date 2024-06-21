from datetime import datetime

class Thing:
    def __init__(self, thingId: str, policyId: str, attributes, features) -> None:
        self.thingId = thingId
        self.policyId = policyId
        self.attributes = Attributes(**attributes)
        self.features = Features(**features)

class Attributes:
    def __init__(self, gender, heigth, weigth, birthdate, runningDate) -> None:
        self.gender = int(gender)
        self.heigth = int(heigth)
        self.weigth = float(weigth)
        split = birthdate.split('-')
        self.birthdate = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))
        split = runningDate.split('-')
        self.runningDate = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))

class Features:
    def __init__(self, goal, trainingPlan, suggestions, preferences) -> None:
        self.goal = Goal(**goal)
        self.trainingPlan = TrainingPlan(**trainingPlan)
        self.suggestions = Suggestions(**suggestions)
        self.preferences = Preferences(**preferences)

class Goal:
    def __init__(self, properties) -> None:
        self.properties = GoalProperties(**properties)

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

class Estimation:
    def __init__(self, date, seconds, goalReachDate) -> None:
        split = date.split('-')
        self.date = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))
        self.seconds = seconds
        split = goalReachDate.split('-')
        self.goalReachDate = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))

class TrainingPlan:
    def __init__(self, properties) -> None:
        self.properties = TrainingPlanProperties(**properties)

class TrainingPlanProperties:
    def __init__(self, sessions) -> None:
        list = []
        for x in sessions:
            list.append(TrainingSession(**x))
        self.sessions = list

class TrainingSession:
    def __init__(self, day, distance, times, rest, expectedTime, meanHeartRate) -> None:
        self.day = day
        self.distance = distance
        self.times = times
        self.rest = rest
        self.expectedTime = expectedTime
        self.meanHeartRate = meanHeartRate

class Suggestions:
    def __init__(self, properties) -> None:
        self.properties = SuggestionProperties(**properties)

class SuggestionProperties:
    def __init__(self, suggestions) -> None:
        list = []
        for x in suggestions:
            list.append(GoalProperties(**x))
        self.suggestions = list

class SuggestionDetail:
    def __init__(self, id, type, distance, seconds, date, trainingDays) -> None:
        self.id = id
        self.type = type
        self.distance = distance
        self.seconds = seconds
        self.date = date
        self.trainingDays = trainingDays

class Preferences:
    def __init__(self, properties) -> None:
        self.properties = PreferencesProperties(**properties)

class PreferencesProperties:
    def __init__(self, trainingDays: list[int]) -> None:
        self.trainingDays = trainingDays