import pandas as pd
from pmdarima.arima import auto_arima
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
N_DAYS = int(os.getenv('N_DAYS'))

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

def parseDate(year: str, month: str, day: str) -> datetime:
    return datetime(year=int(year), month=int(month), day=int(day))