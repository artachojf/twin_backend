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

df = pd.DataFrame(columns=['fatigue','goal_distance','goal_time','remaining_days','distance','pace','hr'])
#df = pd.DataFrame(columns=['fatigue','goal_distance','goal_time','remaining_days','distance','repetitions','pace','hr'])
#df = pd.DataFrame(columns=['fatigue','goal_distance','goal_time','remaining_days','session_type'])

for i in range(5000):

    goal_distance = random.randint(5000, 42196)
    goal_pace = random.uniform(3.0, 6.0)
    goal_time = int(goal_distance*goal_pace/10)

    for j in range(100):

        remaining_days = j+1
        fatigue = random.uniform(0.0, 100.0)

        distance = goal_distance * random.uniform(0.9, 2) * (1 - (fatigue/100))
        '''repetitions = random.randint(2,8)
        rep_distance = distance / repetitions'''

        pace = goal_pace * random.uniform(0.9, 1.1)
        hr = 160 * random.uniform(0.85, 1.15) / (pace / goal_pace)

        '''session_type = random.randint(0,1)
        if session_type == 0: session_type = "Interval"
        else: session_type = "Continuous"'''

        list = [fatigue,goal_distance,goal_time,remaining_days,distance,pace,hr]
        #list = [fatigue,goal_distance,goal_time,remaining_days,rep_distance,repetitions,pace,hr]
        #list = [fatigue,goal_distance,goal_time,remaining_days,session_type]
        df.loc[j+i*100] = list

    print(i)

print(df.head())
df.to_csv('decision_tree_dataset.csv', index=False)