import mysql.connector
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PWD = os.getenv('DB_PWD')
DB_NAME = os.getenv('DB_NAME')

mydb = mysql.connector.connect(
  host=DB_HOST,
  user=DB_USER,
  password=DB_PWD,
  database=DB_NAME
)
mycursor = mydb.cursor(buffered=True)

sql_insert = 'INSERT INTO MEASUREMENTS (date,client_id,5k,10k,21k,42k) VALUES (%s, %s, %s, %s, %s, %s)'
sql_select = 'SELECT date,5k,10k,21k,42k FROM MEASUREMENTS WHERE client_id = %s ORDER BY date'
sql_update = 'UPDATE MEASUREMENTS SET 5k = %s, 10k = %s, 21k = %s, 42k = %s WHERE client_id = %s AND date = %s'

def insertValues(values: tuple[datetime,str,float,float,float,float]):
    mycursor.execute(sql_insert, values)
    mydb.commit()

def updateValues(values: tuple[float,float,float,float,str,datetime]):
    mycursor.execute(sql_update, values)
    mydb.commit()

def selectValues(clientId: str) -> pd.DataFrame:
    columns = ['Date','5k','10k','21k','42k']
    data = pd.read_sql(sql_select, mydb, params=[clientId], columns=columns)
    return data