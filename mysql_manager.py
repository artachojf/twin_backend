import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="ditto"
)
mycursor = mydb.cursor(buffered=True)

sql_insert = 'INSERT INTO MEASUREMENTS (date,client_id,strength,aerobic_endurance,anaerobic_endurance,fatigue,sleep) VALUES (%s, %s, %s, %s, %s, %s, %s)'
sql_select = 'SELECT strength,aerobic_endurance,anaerobic_endurance,fatigue FROM MEASUREMENTS WHERE client_id = %s ORDER BY date'
sql_update = 'UPDATE MEASUREMENTS SET strength = %s, aerobic_endurance = %s, anaerobic_endurance = %s, fatigue = %s, sleep = %s WHERE client_id = %s AND date = %s'

def insertValues(values: tuple()):
    mycursor.execute(sql_insert, values)
    mydb.commit()

def updateValues(values: tuple()):
    mycursor.execute(sql_update, values)
    mydb.commit()

def selectValues(clientId: str) -> pd.DataFrame:
    columns = ['strength','aerobic_endurance','anaerobic_endurance','fatigue']
    data = pd.read_sql(sql_select, mydb, params=[clientId], columns=columns)
    return data