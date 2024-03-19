import pandas as pd
import pyodbc
import numpy as np
import json

# Load configuration from file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Load clean data into a DataFrame
data = pd.read_parquet(config['parquet_file_path'])
clean_data = data[data['passenger_count'] > 0]

# Define your SQL Server connection details
server = config['server']
database = config['database']

# Create connection string with Windows Authentication
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'

# Connect to SQL Server
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Define table name
table_name = config['table_name']

# Drop table if exists (optional)
cursor.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name}")

# Detect schema and create table dynamically
create_table_query = f"CREATE TABLE {table_name} ("
for col_name, col_type in clean_data.dtypes.items():
    if np.issubdtype(col_type, np.integer):
        sql_type = 'INT'
    elif np.issubdtype(col_type, np.floating):
        sql_type = 'FLOAT'
    elif np.issubdtype(col_type, np.datetime64):
        sql_type = 'DATETIME'
    else:
        sql_type = 'NVARCHAR(MAX)'  # Adjust based on your data types
    create_table_query += f"{col_name} {sql_type}, "
create_table_query = create_table_query.rstrip(', ') + ")"  # Remove trailing comma

# Execute the CREATE TABLE query
cursor.execute(create_table_query)

# Prepare the INSERT query template
insert_query_template = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(clean_data.columns))})"

# Convert DataFrame to list of tuples for bulk insertion
data_to_insert = [tuple(row) for row in clean_data.values]

# Execute bulk insert
cursor.executemany(insert_query_template, data_to_insert)

# Commit the transaction
conn.commit()

# Close the connection
conn.close()

print("Data loaded successfully into SQL Server database.")
