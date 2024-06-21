import pandas as pd
from pmdarima.arima import auto_arima
from datetime import datetime
import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from .model.DittoGeneralInfo import *
from datetime import datetime
from enum import Enum

load_dotenv()
N_DAYS = int(os.getenv('N_DAYS'))

class Distances(Enum):
    FIVE_KM = 5000
    TEN_KM = 10000
    HALF_MARATHON = 21097
    MARATHON = 42195

def updateThing(
        data: pd.DataFrame,
        goal: GoalProperties,
        preferences: PreferencesProperties
    ) -> Features:

    column = getEstimationColumn(goal.distance, data)
    prediction = getPredictions(column, (datetime.now() - goal.date).days)
    print(prediction)

    estimation = column.iloc[-1]
    slope = getSlope(goal, estimation)
    plan = generateTrainingPlan(preferences, goal, data, estimation, slope)
    suggestions = generateSuggestions(goal, data, prediction, slope)

    return Features(Goal(goal), TrainingPlan(plan), Suggestions(suggestions), Preferences(preferences))

def getPredictions(column: pd.DataFrame, nPeriods: int) -> float:
    model = auto_arima(column, start_p=0, start_q=0,
                    test='adf',
                    max_p=5, max_q=5,
                    m=1,
                    q=1,
                    seasonal=True,
                    start_P=0,
                    D=None,
                    trace=True,
                    error_action='ignore',
                    suppress_warnings=True,
                    stepwise=True)
    predictions = model.predict(n_periods=nPeriods)
    print(predictions)
    return predictions.iloc[-1]

def generateTrainingPlan(
        preferences: PreferencesProperties,
        goal: GoalProperties,
        data: pd.DataFrame,
        estimation: float,
        slope: float
    ) -> TrainingPlanProperties:

    preferences.trainingDays
    datetime.now().isoweekday

    #TODO: Generate training plan
    cosine_similarity()
    return

def generateSuggestions(
        goal: GoalProperties,
        data: pd.DataFrame,
        prediction: float,
        slope: float
    ) -> SuggestionProperties:
    
    #TODO: Generate suggestions
    return

def parseDate(year: str, month: str, day: str) -> datetime:
    return datetime(year=int(year), month=int(month), day=int(day))

def getEstimationColumn(goal: float, data: pd.DataFrame) -> pd.DataFrame:
    if goal < Distances.FIVE_KM:
        return data[['5k']] * (goal / Distances.FIVE_KM)
    elif goal == Distances.FIVE_KM:
        return data[['5k']]
    elif goal > Distances.FIVE_KM and goal < Distances.TEN_KM:
        coef = getCoeficients(goal, Distances.FIVE_KM, Distances.TEN_KM)
        return (data[['5k']] * coef[0]) + (data[['10k']] * coef[1])
    elif goal == Distances.TEN_KM:
        return data[['10k']]
    elif goal > Distances.TEN_KM and goal < Distances.HALF_MARATHON:
        coef = getCoeficients(goal, Distances.TEN_KM, Distances.HALF_MARATHON)
        return (data[['10k']] * coef[0]) + (data[['21k']] * coef[1])
    elif goal == Distances.HALF_MARATHON:
        return data[['21k']]
    elif goal > Distances.HALF_MARATHON and goal < Distances.MARATHON:
        coef = getCoeficients(goal, Distances.HALF_MARATHON, Distances.MARATHON)
        return (data[['21k']] * coef[0]) + (data[['42k']] * coef[1])
    elif goal == Distances.MARATHON:
        return data[['42k']]
    elif goal > Distances.MARATHON:
        return data[['42k']] * (goal / Distances.MARATHON)

def getSlope(goal: GoalProperties, estimation: float) -> float:
    daysOffset = (datetime.now() - goal.date).days
    timesOffset = goal.secons - estimation
    return timesOffset / daysOffset

def getCoeficients(distance: float, below: float, above: float) -> tuple[float, float]:
    offset = above - below
    x = distance - below
    percentage = x / offset
    return (1-percentage, percentage)