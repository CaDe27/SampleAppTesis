import pandas as pd
import numpy as np


df = pd.read_csv('./app/static/data/csv/movie_info.csv')
df['price(US)'] = np.random.uniform(5, 20, size=len(df))
df['price(US)'] = df['price(US)'].round(2)
df.to_csv('./app/static/data/csv/movie_info.csv', index=False)