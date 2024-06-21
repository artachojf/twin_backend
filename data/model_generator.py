import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
import pickle

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.apply(pd.to_numeric, errors='coerce')
    return df.dropna()

def filter_columns(json_file='columns.json') -> pd.DataFrame:
    with open(json_file, 'r') as f:
        json_data = json.load(f)

    columns = [json_data["fatigue"], json_data["goal_distance"], json_data["goal_time"], json_data["remaining_days"], json_data["distance"], json_data["pace"], json_data["hr"]]
    df = pd.read_csv(json_data["file"])
    df = df[columns]
    
    del json_data["file"]
    json_data = {value: key for key, value in json_data.items()}
    df = df.rename(columns=json_data)
    return clean_dataset(df)

def generate_model(df, input, output, file_name="model.pkl"):
    X = df[input]
    y = df[output]
    
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    model = LinearRegression()
    multi_output_model = MultiOutputRegressor(estimator=model)
    multi_output_model.fit(X, y)

    with open(file_name, "wb") as f:
        pickle.dump(multi_output_model, f)

def predict_values(data, file_name="model.pkl"):
    with open(file_name, "rb") as f:
        model = pickle.load(f)

    data_array = np.array([list(data.values())])
    output = model.predict(data_array)
    print(output)

data = filter_columns()
input = ['fatigue','goal_time','goal_distance','remaining_days']
output = ['distance','pace','hr']
generate_model(data, input, output)
#data = {"fatigue": 85, "goal_time": 15000, "goal_distance": 21097, "remaining_days": 32}
#predict_values(data)