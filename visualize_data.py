import pandas as pd
import pyodbc
import plotly.express as px
import json

# Load configuration from file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Define your SQL Server connection details
server = config['server']
database = config['database']

# Create connection string with Windows Authentication
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes'

# Connect to SQL Server
conn = pyodbc.connect(conn_str)

# Query to aggregate total amount per day
query = """
        SELECT CAST(tpep_pickup_datetime AS DATE) AS pickup_date, SUM(total_amount) AS total_amount
        FROM {table_name}
        GROUP BY CAST(tpep_pickup_datetime AS DATE)
        ORDER BY pickup_date
        """.format(table_name=config['table_name'])

# Execute the query and fetch the results into a DataFrame
aggregated_data = pd.read_sql(query, conn)

# Close the connection
conn.close()

# Format the 'pickup_date' column to include both date and day of the week
aggregated_data['pickup_date'] = pd.to_datetime(aggregated_data['pickup_date'])
aggregated_data['pickup_date'] = aggregated_data['pickup_date'].dt.strftime('%Y-%m-%d (%a)')

# Plotting the aggregated data using Plotly
fig = px.bar(aggregated_data, x='pickup_date', y='total_amount', title='Total Amount per Day',
             text='total_amount', labels={'pickup_date': 'Date', 'total_amount': 'Total Amount'})
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_xaxes(tickangle=45)
fig.show()
