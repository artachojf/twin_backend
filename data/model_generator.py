import pandas as pd
import numpy as np
import json
import pickle
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
import warnings

warnings.filterwarnings('ignore', module='sklearn')

################# DATAFRAMES #################

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna()

def filter_columns(json_file='columns.json') -> pd.DataFrame:
    with open(json_file, 'r') as f:
        json_data = json.load(f)

    file_name = json_data["file"]
    columns = [json_data["fatigue"], json_data["goal_distance"], json_data["goal_time"], json_data["remaining_days"], json_data["distance"], json_data["repetitions"], json_data["pace"], json_data["hr"], json_data["session_type"]]
    df = pd.read_csv(file_name)
    df = df[columns]
    
    del json_data["file"]
    json_data = {value: key for key, value in json_data.items()}
    df = df.rename(columns=json_data)
    df = clean_dataset(df)
    return df

################# AI MODEL GENERATION #################

def normalize_data(df, file_name='scaler', fromFile=False):
    if fromFile:
        with open(f'{file_name}.pkl', 'rb') as f:
            scaler = pickle.load(f)
    else:
        scaler = MinMaxScaler()
    scaler.fit(df)
    normalized_df = scaler.transform(df)
    with open(f'{file_name}.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    return normalized_df

def normalize_dataset(df, input, output, file_name='neural_network'):
    df[input] = normalize_data(df[input], f'{file_name}_input_scaler')
    df[output] = normalize_data(df[output], f'{file_name}_output_scaler')
    return df

def denormalize_data(data, file_name='scaler'):
    with open(f'{file_name}.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return scaler.inverse_transform(data)

def generate_neural_network(df, input, output, file_name='neural_network'):
    print(df.head())
    df = normalize_dataset(df, input, output, file_name)
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
    model.save(f'{file_name}.keras')

def generate_decision_tree(data, input, output, file_name='decision_tree'):
    print(data.head())
    X = data[input]
    y = data[output]
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    model = DecisionTreeClassifier(max_depth=3)
    model.fit(X_train, y_train)

    with open(f'{file_name}.pkl', "wb") as f:
        pickle.dump(model, f)

################# TEST #################

def predict_neural_network_values(data, file_name='neural_network'):
    model = tf.keras.models.load_model(f'{file_name}.keras')
    data_array = np.array([list(data.values())])
    data_array = normalize_data(data_array, f'{file_name}_input_scaler', True)
    output = model.predict(data_array)
    output = denormalize_data(output, f'{file_name}_output_scaler')
    return output

def predict_decision_tree_values(data, file_name='decision_tree'):
    with open(f'{file_name}.pkl', 'rb') as f:
        model = pickle.load(f)

    data_array = np.array([list(data.values())])
    output = model.predict(data_array)
    return output

################# MAIN #################

data = filter_columns(json_file='columns.json')
input = ['fatigue','goal_distance','goal_time','remaining_days']

print('\033[31mCONTINUOUS NEURAL NETWORK\033[0m')
continuous_data = data[data['repetitions'] <= 1]
output_continuous = ['distance','pace','hr']
generate_neural_network(continuous_data, input, output_continuous, 'continuous_neural_network')

print('\033[31mINTERVAL NEURAL NETWORK\033[0m')
interval_data = data[data['repetitions'] > 1]
output_interval = ['distance','repetitions','pace','hr']
generate_neural_network(interval_data, input, output_interval, 'interval_neural_network')

print('\033[31mDECISION TREE\033[0m')
output_decision_tree = ['session_type']
generate_decision_tree(data, input, output_decision_tree, 'decision_tree')

print('\033[31mTESTING THE MODELS\033[0m')
data = {"fatigue": 98, "goal_distance": 23456, "goal_time": 18200, "remaining_days": 32}
print(f'\033[32mINPUT:\033[0m\n{data.__str__()}')

output = predict_neural_network_values(data, 'continuous_neural_network')[0]
print(f'\033[32mCONTINUOUS OUTPUT:\033[0m\nDistance: {output[0]}\tPace: {output[1]}\tHeart Rate: {output[2]}')

output = predict_neural_network_values(data, 'interval_neural_network')[0]
print(f'\033[32mINTERVAL OUTPUT:\033[0m\nDistance: {output[0]}\tRepetitions: {output[1]}\tPace: {output[2]}\tHeart Rate: {output[3]}')

print(f'\033[32mDECISION TREE OUTPUT:\033[0m\tSession Type: {predict_decision_tree_values(data, 'decision_tree')[0]}')