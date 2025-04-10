
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime 

url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attribs = ["Name", "MC_USD_Billion"]
db_name = 'Banks.db'
table_name = 'Largest_banks'
csv_path = './Largest_banks_data.csv'
exchange_rate_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-PY0221EN-Coursera/labs/v2/exchange_rate.csv")



# Code for ETL operations on Country-GDP data

# Importing the required libraries

def extract(url, table_attribs):
    page = requests.get(url).text
    data = BeautifulSoup(page,'html.parser')
    df = pd.DataFrame(columns=table_attribs)
    tables = data.find_all('tbody')
    rows = tables[0].find_all('tr')
    for row in rows:
        col = row.find_all('td')
        if len(col)!=0:
            if col[1].find('a') is not None:
                data_dict = {"Name": col[1].a['title'],
                             "MC_USD_Billion": col[2].contents[0]}
                df1 = pd.DataFrame(data_dict, index=[0])
                df = pd.concat([df,df1], ignore_index=True)
    return df

def transform(df, exchange_rate_df):
    # Cria um dicionário com as taxas de câmbio
    rates = exchange_rate_df.set_index('Currency')['Rate'].to_dict()

    # Converte a coluna MC_USD_Billion para float
    df["MC_USD_Billion"] = df["MC_USD_Billion"].str.replace(",", "").astype(float)

    # Adiciona colunas convertidas
    df["MC_GBP_Billion"] = (df["MC_USD_Billion"] * rates["GBP"]).round(2)
    df["MC_EUR_Billion"] = (df["MC_USD_Billion"] * rates["EUR"]).round(2)
    df["MC_INR_Billion"] = (df["MC_USD_Billion"] * rates["INR"]).round(2)

    return df

def load_to_csv(df, csv_path):
    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)

def run_query(query_statement, sql_connection):
    print(query_statement)
    query_output = pd.read_sql(query_statement, sql_connection)
    print(query_output)

def log_progress(message): 
    timestamp_format = '%Y-%h-%d-%H:%M:%S' # Year-Monthname-Day-Hour-Minute-Second 
    now = datetime.now() # get current timestamp 
    timestamp = now.strftime(timestamp_format) 
    with open("./code_log.txt","a") as f:  
        f.write(timestamp + ' : ' + message + '\n')

log_progress('Preliminaries complete. Initiating ETL process')

df = extract(url, table_attribs)

log_progress('Data extraction complete. Initiating Transformation process')

df = transform(df, exchange_rate_df)

log_progress('Data transformation complete. Initiating loading process')

load_to_csv(df, csv_path)

log_progress('Data saved to CSV file')

sql_connection = sqlite3.connect(db_name)

log_progress('SQL Connection initiated.')

load_to_db(df, sql_connection, table_name)

log_progress('Data loaded to Database as table. Running the query')

query_statement = f"SELECT * FROM {table_name} WHERE MC_USD_Billion >= 300"
run_query(query_statement, sql_connection)

log_progress('Process Complete.')

sql_connection.close()

