import pandas as pd
import numpy as np
import json
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.apply(pd.to_numeric, errors='coerce')
    return df.dropna()

def filter_columns(json_file='columns.json', save=False) -> pd.DataFrame:
    with open(json_file, 'r') as f:
        json_data = json.load(f)

    file_name = json_data["file"]
    columns = [json_data["fatigue"], json_data["goal_distance"], json_data["goal_time"], json_data["remaining_days"], json_data["distance"], json_data["pace"], json_data["hr"]]
    df = pd.read_csv(file_name)
    df = df[columns]
    
    del json_data["file"]
    json_data = {value: key for key, value in json_data.items()}
    df = df.rename(columns=json_data)
    df = clean_dataset(df)
    if save: df.to_csv('data_'+file_name, index=False)
    return df

def generate_regression_model(df, input, output, file_name="model.pkl"):
    X = df[input]
    y = df[output]
    
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    model = LinearRegression()
    multi_output_model = MultiOutputRegressor(estimator=model)
    multi_output_model.fit(X, y)

    with open(file_name, "wb") as f:
        pickle.dump(multi_output_model, f)

def normalize_data(df, file_name='scaler.pkl', fromFile=False):
    if fromFile:
        with open(file_name, 'rb') as f:
            scaler = pickle.load(f)
    else:
        scaler = MinMaxScaler()
    scaler.fit(df)
    normalized_df = scaler.transform(df)
    with open(file_name, 'wb') as f:
        pickle.dump(scaler, f)
    return normalized_df

def normalize_dataset(df, input, output):
    df[input] = normalize_data(df[input], 'input_scaler.pkl')
    df[output] = normalize_data(df[output], 'output_scaler.pkl')
    return df

def denormalize_data(data, file_name='scaler.pkl'):
    with open(file_name, 'rb') as f:
        scaler = pickle.load(f)
    return scaler.inverse_transform(data)

def generate_neural_network(df, input, output, file_name='neural_network.keras'):
    df = normalize_dataset(df, input, output)
    print(df.head())
    X = df[input]
    y = df[output]
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(16, activation="relu", input_shape=(len(input),)),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(len(output))
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=10, batch_size=32)
    model.evaluate(X_test, y_test)
    model.save(file_name)

def predict_regression_values(data, file_name="model.pkl"):
    with open(file_name, "rb") as f:
        model = pickle.load(f)

    data_array = np.array([list(data.values())])
    output = model.predict(data_array)
    print(output)

def predict_neural_network_values(data, file_name='neural_network.keras'):
    model = tf.keras.models.load_model(file_name)
    data_array = np.array([list(data.values())])
    data_array = normalize_data(data_array, 'input_scaler.pkl', True)
    output = model.predict(data_array)
    output = denormalize_data(output, 'output_scaler.pkl')
    print(output)

def generate_decision_tree(data, input, output, file_name='decision_tree.pkl'):
    X = data[input]
    y = data[output]
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = DecisionTreeClassifier(max_depth=3)
    model.fit(X_train, y_train)

    with open(file_name, "wb") as f:
        pickle.dump(model, f)

def predict_decision_tree_values(data, file_name='decision_tree.pkl'):
    with open(file_name, 'rb') as f:
        model = pickle.load(f)

    data_array = np.array([list(data.values())])
    output = model.predict(data_array)
    print(output)

'''data = filter_columns(json_file='columns.json', save=False)
input = ['fatigue','goal_distance','goal_time','remaining_days']
output = ['distance','pace','hr'] #['distance','repetitions','pace','hr']
generate_neural_network(data, input, output, 'neural_network.keras')'''
'''output = ['session_type']
generate_decision_tree(data, input, output)'''
data = {"fatigue": 98, "goal_distance": 23456, "goal_time": 18200, "remaining_days": 32}
predict_neural_network_values(data, 'neural_network.keras')
#predict_decision_tree_values(data)