import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from .model.DittoGeneralInfo import *
from .model.DittoCurrentState import Thing as CurrentState
from .model.DittoUserInformation import DittoUserInformation
from datetime import datetime, timedelta
from enum import Enum
import os
import requests
import json

load_dotenv()
TRAINING_MICROSERVICE_URL = os.getenv('TRAINING_MICROSERVICE_URL')
ARIMA_MICROSERVICE_URL = os.getenv('ARIMA_MICROSERVICE_URL')

class Distances(Enum):
    FIVE_KM = 5000
    TEN_KM = 10000
    HALF_MARATHON = 21097
    MARATHON = 42195

def updateThing(
        data: pd.DataFrame,
        user: DittoUserInformation
    ) -> DittoUserInformation:

    data = fill_missing_days(data)
    column = getEstimationColumn(user.generalInfo.features.goal.properties.distance, data)
    estimation = float(column.iloc[-1, 0])
    print(estimation) #Calculated estimation using mathematical formulas
    newEstimations = []
    for x in user.generalInfo.features.goal.properties.estimations:
        if x.date.date() != datetime.today().date():
            newEstimations.append(x)
    newEstimations.append(Estimation(datetime.today(), estimation, datetime.today())) #TODO: Goal reach date
    user.generalInfo.features.goal.properties.estimations = newEstimations

    prediction = getPredictions(column, (user.generalInfo.features.goal.properties.date - datetime.now()).days)
    print(prediction) #Calculate prediction using ARIMA

    calculate_fatigue(user.generalInfo.features.fatigue.properties, user.trainings)

    suggested_session = generateTrainingPlan(
        user.generalInfo.features.preferences.properties,
        user.generalInfo.features.goal.properties,
        user.generalInfo.features.fatigue.properties.historic[0].ctl
    )
    plan = user.generalInfo.features.trainingPlan.properties.sessions
    for x in plan:
        if x.day <= datetime.today() or x.day == suggested_session.day:
            plan.remove(x)
    plan.append(suggested_session)
    user.generalInfo.features.trainingPlan.properties.sessions = plan

    suggestions = generateSuggestions(user.generalInfo.features.goal.properties, prediction, user.generalInfo.features.preferences.properties)
    user.generalInfo.features.suggestions.properties = suggestions

    return user

def fill_missing_days(df: pd.DataFrame) -> pd.DataFrame:
    completed_data = []
    prev_row = None
    for i,row in df.iterrows():
        if prev_row is None:
            completed_data.append(row.copy())
        else:
            missing_days = (row.iloc[0]-prev_row.iloc[0]).days-1
            for j in range(1, missing_days+1):
                missing_date = prev_row.iloc[0] + pd.Timedelta(days=j)
                missing_row = prev_row.copy()
                missing_row.iloc[0] = missing_date
                completed_data.append(missing_row)
            completed_data.append(row.copy())
        prev_row = row.copy()

    data = pd.DataFrame(completed_data)
    return data

def getPredictions(column: pd.DataFrame, n: int) -> float:
    data = {
        'column': list(column.iloc[:,0]),
        'n': n
    }
    r = requests.post(ARIMA_MICROSERVICE_URL, json=data)
    response = json.loads(r.text)
    print(response)

    return float(response['prediction'])

def next_weekday_date(weekdays: list[int]):
    weekday = datetime.now().weekday()
    days = 0
    while weekday not in weekdays:
        days += 1
        weekday = (weekday + 1) % 7
    return datetime.now() + timedelta(days=days)

def generateTrainingPlan(
        preferences: PreferencesProperties,
        goal: GoalProperties,
        fatigue: float
    ) -> TrainingSession:

    training_date = next_weekday_date(preferences.trainingDays)
    remaining_days = (goal.date - training_date).days

    r = requests.get(f'{TRAINING_MICROSERVICE_URL}?ctl={fatigue}&remaining_days={remaining_days}&distance={goal.distance}&time={goal.seconds}')
    response = json.loads(r.text)
    print(response)

    return TrainingSession(training_date, response['distance'], response['times'], int(response['seconds']/2), response['seconds'], response['hr'])

def suggest_more_training_days(days: list[int]) -> list[int]:
    if len(days) >= 6:
        return days
    
    maxDiffDay, daysGap = 0, 0
    for i in range(len(days)):
        if i != len(days)-1:
            gap = days[i+1] - days[i]
        else:
            gap = days[0] + 7 - days[i]
        
        if gap > daysGap:
            maxDiffDay = days[i]
            daysGap = gap

        days.append((maxDiffDay + int(daysGap/2)) % 7)

    return days

def suggest_less_training_days(days: list[int]) -> list[int]:
    if len(days) <= 2:
        return days
    
    minDiffDay, daysGap = 0, 0
    for i in range(len(days)):
        if i != len(days)-1:
            gap = days[i+1] - days[i]
        else:
            gap = days[0] + 7 - days[i]
        
        if gap < daysGap:
            minDiffDay = days[(i+1)%7]
            daysGap = gap

        days.remove(minDiffDay)
    
    return days

def generateSuggestions(
        goal: GoalProperties,
        prediction: float,
        preferences: PreferencesProperties
    ) -> SuggestionProperties:

    class SuggestionType(Enum):
        SMALLER_GOAL = 0
        BIGGER_GOAL = 1
        LESS_TRAINING_DAYS = 2
        MORE_TRAINING_DAYS = 3

    newSuggestions = []
    
    print("Goal:",goal.seconds, "\tPrediction:" , prediction)
    if goal.seconds*1.1 < prediction: #The athlete is considerably far from the goal
        newSuggestions.append(
            SuggestionDetail(
                len(newSuggestions),
                SuggestionType.SMALLER_GOAL.value,
                0.7*goal.distance,
                0.7*goal.seconds,
                goal.date.strftime("%Y-%m-%d"),
                []
            )
        )
        newSuggestions.append(
            SuggestionDetail(
                len(newSuggestions),
                SuggestionType.SMALLER_GOAL.value,
                goal.distance,
                1.1*goal.seconds,
                goal.date.strftime("%Y-%m-%d"),
                []
            )
        )
        if len(preferences.trainingDays) < 6:
            newSuggestions.append(
                SuggestionDetail(
                    len(newSuggestions),
                    SuggestionType.MORE_TRAINING_DAYS.value,
                    goal.distance,
                    goal.seconds,
                    goal.date.strftime("%Y-%m-%d"),
                    suggest_more_training_days(preferences.trainingDays)
                )
            )
    elif goal.seconds*0.9 > prediction: #The athlete is considerably over the goal
        newSuggestions.append(
            SuggestionDetail(
                len(newSuggestions),
                SuggestionType.BIGGER_GOAL.value,
                1.3*goal.distance,
                1.3*goal.seconds,
                goal.date.strftime("%Y-%m-%d"),
                []
            )
        )
        newSuggestions.append(
            SuggestionDetail(
                len(newSuggestions),
                SuggestionType.BIGGER_GOAL.value,
                goal.distance,
                0.9*goal.seconds,
                goal.date.strftime("%Y-%m-%d"),
                []
            )
        )
        if len(preferences.trainingDays) > 3:
            newSuggestions.append(
                SuggestionDetail(
                    len(newSuggestions),
                    SuggestionType.LESS_TRAINING_DAYS.value,
                    goal.distance,
                    goal.seconds,
                    goal.date.strftime("%Y-%m-%d"),
                    suggest_less_training_days(preferences.trainingDays)
                )
            )

    return SuggestionProperties(newSuggestions)

def parseDate(year: str, month: str, day: str) -> datetime:
    return datetime(year=int(year), month=int(month), day=int(day))

def getEstimationColumn(goal: float, data: pd.DataFrame) -> pd.DataFrame:
    if goal < Distances.FIVE_KM.value:
        return data[['5k']] * (goal / Distances.FIVE_KM.value)
    elif goal == Distances.FIVE_KM.value:
        return data[['5k']]
    elif goal > Distances.FIVE_KM.value and goal < Distances.TEN_KM.value:
        coef = getCoeficients(goal, Distances.FIVE_KM.value, Distances.TEN_KM.value)
        return (data[['5k']] * coef[0]) + (data[['10k']] * coef[1])
    elif goal == Distances.TEN_KM.value:
        return data[['10k']]
    elif goal > Distances.TEN_KM.value and goal < Distances.HALF_MARATHON.value:
        coef = getCoeficients(goal, Distances.TEN_KM.value, Distances.HALF_MARATHON.value)
        return (data[['10k']] * coef[0]) + (data[['21k']] * coef[1])
    elif goal == Distances.HALF_MARATHON.value:
        return data[['21k']]
    elif goal > Distances.HALF_MARATHON.value and goal < Distances.MARATHON.value:
        coef = getCoeficients(goal, Distances.HALF_MARATHON.value, Distances.MARATHON.value)
        return (data[['21k']] * coef[0]) + (data[['42k']] * coef[1])
    elif goal == Distances.MARATHON.value:
        return data[['42k']]
    elif goal > Distances.MARATHON.value:
        return data[['42k']] * (goal / Distances.MARATHON.value)

def getCoeficients(distance: float, below: float, above: float) -> tuple[float, float]:
    offset = above - below
    x = distance - below
    percentage = x / offset
    return (1-percentage, percentage)

def calculate_fatigue(fatigue: FatigueProperties, trainings: list[CurrentState]):
        if len(trainings) == 0:
            session = next((x for x in trainings if x.getDate() == date), None)
            if session == None:
                trimp = 0
                coef = 0
            else:
                trimp = session.calculate_trimp()
                coef = session.calculate_ctl_coef()
            fatigue.historic.insert(0, FatigueData(trimp*coef, datetime.now()))
            return
        
        last = fatigue.historic[0]
        days = (datetime.today() - last.date).days
        for i in range(1,days+1):
            date = last.date + timedelta(days=i)
            session = next((x for x in trainings if x.getDate() == date), None)
            if session == None:
                trimp = 0
                coef = 0
            else:
                trimp = session.calculate_trimp()
                coef = session.calculate_ctl_coef()
            
            prev_ctl = next((x for x in fatigue.historic if x.date == (date-timedelta(days=1))), None)
            if prev_ctl == None:
                ctl = trimp*coef
            else:
                ctl = prev_ctl.ctl + (trimp - prev_ctl.ctl)*coef
            fatigue.historic.insert(0, FatigueData(ctl, date))