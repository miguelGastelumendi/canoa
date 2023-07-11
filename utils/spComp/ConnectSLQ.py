# Import required libraries
from sqlalchemy import create_engine
import pandas as pd

# Define the connection parameters
driver = 'SQL Server'
server = '54.207.37.232'
port = 30330
database = 'RURALLEGAL'
username = 'sa'
password = 'Hibisco%4012'

# Define the connection string
connection_string = f'mssql+pymssql://{username}:{password}@{server}:{port}/{database}'

# Create the database engine
engine = create_engine(connection_string)

# Test the connection by executing a simple SQL query and fetching the results
query = 'SELECT * FROM CustoEtapa'
df = pd.read_sql_query(query, engine)
print(df.head())