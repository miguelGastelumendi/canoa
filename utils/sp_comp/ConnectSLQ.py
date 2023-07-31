# Import required libraries
from sqlalchemy import create_engine
import pandas as pd
import os

# Create the database engine
engine = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])

# Test the connection by executing a simple SQL query and fetching the results
query = 'SELECT * FROM CustoEtapa'
df = pd.read_sql_query(query, engine)
print(df.head())