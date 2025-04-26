import time
import pandas as pd
from sklearn.datasets import load_iris
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.metadata import Metadata

data = load_iris(as_frame=True)
df = data.frame

metadata = Metadata.detect_from_dataframe(data=df, table_name="iris")

synthesizer = GaussianCopulaSynthesizer(metadata)
synthesizer.fit(data=df)

while True:
    # wait a second
    time.sleep(1)
    synthetic_data = synthesizer.sample(num_rows=1)
    print(synthetic_data)
