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

file_name = 'garmin.csv'
data = pd.read_csv(file_name)
newData = generate_random_column(data, 'Fatigue',0, decimal=True)
print(newData.head())
newData.to_csv(file_name, index=False)