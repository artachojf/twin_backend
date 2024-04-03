from datetime import datetime

class Thing:
    def __init__(self, thingId: str, policyId: str, attributes, features) -> None:
        self.thingId = thingId
        self.policyId = policyId
        self.attributes = Attributes(**attributes)
        self.features = Features(**features)

class Attributes:
    def __init__(self, gender, heigth, weigth, birthYear, runningYear) -> None:
        self.gender = int(gender)
        self.heigth = int(heigth)
        self.weigth = float(weigth)
        self.birthYear = int(birthYear)
        self.runningYear = int(runningYear)

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
    def __init__(self, distance, seconds, date) -> None:
        self.distance = int(distance)
        self.seconds = int(seconds)
        split = date.split('-')
        self.date = datetime(year=int(split[0]), month=int(split[1]), day=int(split[2]))

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
    def __init__(self, day, distance, times, rest, expectedTime) -> None:
        self.day = day
        self.distance = distance
        self.times = times
        self.rest = rest
        self.expectedTime = expectedTime

class Suggestions:
    def __init__(self, properties) -> None:
        self.properties = SuggestionProperties(**properties)

class SuggestionProperties:
    def __init__(self, suggestions) -> None:
        list = []
        for x in suggestions:
            list.append(GoalProperties(**x))
        self.suggestions = list

class Preferences:
    def __init__(self, properties) -> None:
        self.properties = PreferencesProperties(**properties)

class PreferencesProperties:
    def __init__(self, trainingDays: list[int]) -> None:
        self.trainingDays = trainingDays