import pandas as pd
from pmdarima.arima import auto_arima
from datetime import datetime, timedelta
from dittoCurrentState import dittoCurrentState
import os
from dotenv import load_dotenv

load_dotenv()
N_DAYS = int(os.getenv('N_DAYS'))

def getObjectList(jsonList: list) -> list[dittoCurrentState]:
    objectList = []
    deadline = datetime.now() - timedelta(days=N_DAYS)

    for o in jsonList:
        session = o['features']['trainingSession']['properties']
        sleep = o['features']['sleepRating']['properties']['overall']
        object = dittoCurrentState(o['thingId'], session['strength'], session['aerobic_endurance'], session['anaerobic_endurance'], session['fatigue'], sleep)
        if object.date < deadline: object.deleteThing()
        else: objectList.append(object)

    return objectList

def calculateCurrentState(list: list[dittoCurrentState]) -> tuple[datetime,str,float,float,float,float,float]:
    sum = [0.0]*5
    n = 0
    workoutIndex = (list[0].date - list[-1].date).days + 1
    restIndex = 0

    for e in list:
        if e.isRest():
            n += restIndex
            restIndex += 1
        else:
            session = e.toList()
            for i in range(len(sum)):
                sum[i] += (session[i]*workoutIndex)
            n += workoutIndex
            workoutIndex -= 1
    
    for i in range(restIndex, workoutIndex+1):
        n += i
    
    for i in range(len(sum)):
        sum[i] /= n
    
    return (list[0].date.strftime('%Y-%m-%d'),list[0].clientId,sum[0],sum[1],sum[2],sum[3],sum[4])

def getPredictions(data: pd.DataFrame, nPredictions: int):
    prediction = []
    for i in data.columns:
        print('\n\n',i,'\n')
        column = data[[i]]

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
        prediction.append(model.predict(n_periods=nPredictions))
    
    return prediction