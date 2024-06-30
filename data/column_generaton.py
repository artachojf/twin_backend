import pandas as pd
import random

def generate_random_column(df, column_name, min_value=0, max_value=100, decimal=False):
    if decimal:
        random_data = [random.uniform(min_value, max_value) for _ in range(len(df))]
    else:
        random_data = pd.Series(random.choices(range(min_value, max_value), k=len(df)))
    column = pd.Series(random_data)
    df[column_name] = column
    return df

def column_random_delta(df, column_name, min_delta=0, max_delta=10, decimal=False):
    if decimal:
        delta = [random.uniform(min_delta, max_delta) for _ in range(len(df))]
    else:
        delta = pd.Series(random.choices(range(min_delta, max_delta), k=len(df)))
    df[column_name] += delta
    return df

def time_to_decimal(str):
    try:
        minutes, seconds = map(int, str.split(":"))
        decimal_minutes = minutes + seconds / 60
        return decimal_minutes
    except ValueError:
        print(f"Invalid time format: {str}")
        return None

def pace_to_float(df, column_name):
    df[column_name] = df[column_name].apply(time_to_decimal)
    return df

for i in range(500):
    file_name = 'apple_watch.csv'
    data = pd.read_csv(file_name)

    newData = generate_random_column(data, 'Fatigue', decimal=True)

    distance = random.randint(5000, 42195)
    newData = generate_random_column(newData, 'Goal_Distance', distance, distance+1)

    pace = random.uniform(3.0, 8.0)
    time = int(distance*pace/10)
    newData = generate_random_column(newData, 'Goal_Time', time, time+1)

    newData = generate_random_column(newData, 'Remaining_Days', 0, len(newData))

    newData = column_random_delta(newData, 'Distance (km)', -2.5, 2.5, True)

    newData = column_random_delta(newData, 'Avg. Heart Rate (BPM)', -15, 15)

    #newData = pace_to_float(newData, 'Avg Pace')
    newData = column_random_delta(newData, 'Avg. Pace (Min/km)', -1, 1, True)

    print(newData.head())
    newData.to_csv('output_'+file_name, mode='a', index=False)