import time
import pandas as pd
from sklearn.datasets import load_iris
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import Metadata
import psycopg2
import numpy as np

data = load_iris(as_frame=True)
df = data.frame

metadata = Metadata.detect_from_dataframe(data=df, table_name="iris")

synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit(data=df)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="mydb",
    user="postgres",
    password="postgres",
    host="postgres",
    port="5432"
)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS mytable (
    id SERIAL PRIMARY KEY,
    sepal_length FLOAT,
    sepal_width FLOAT,
    petal_length FLOAT,
    petal_width FLOAT,
    target INT
)
""")
conn.commit()

while True:
    # wait a second
    time.sleep(1)
    synthetic_data = synthesizer.sample(num_rows=1)
    row = synthetic_data.iloc[0]  # Get the first row of the synthetic data
    cursor.execute("""
        INSERT INTO mytable (sepal_length, sepal_width, petal_length, petal_width, target)
        VALUES (%s, %s, %s, %s, %s)
    """, (row['sepal length (cm)'].item(), row['sepal width (cm)'].item(), 
          row['petal length (cm)'].item(), row['petal width (cm)'].item(), row['target'].item()))
    conn.commit()
    print(synthetic_data)
