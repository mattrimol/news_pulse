"""
Gets any new data from the API that we don't have and updates the database with it.
"""
from sqlalchemy import create_engine
engine = create_engine('sqlite:///data/guardian_content.db', echo=True)
sqlite_connection = engine.connect()

import pandas as pd
import guardian_data_pipeline as g

# STEP 1 - Find most recent date (last update)
max_timestamp = pd.read_sql('SELECT max(pub_datetime) FROM content;', engine)
latest_pull_date = str(pd.to_datetime(max_timestamp.iloc[0, 0]).date())
#STEP 2 - Delete all rows with the most recent date
q = f"DELETE FROM content WHERE DATE(pub_datetime) >= '{latest_pull_date}';"
engine.execute(q)

#STEP 3 - Go to the API and get all the data from the latest pull until now
url = g.url.replace('<start>', latest_pull_date)
url = url.replace('to-date=<end>&', '')
new_data_list = g.get_results_list(url) #requests

#STEP 4 - Put the results in a dataframe and clean so it is same format as DB
new_data_df = g.results_list_to_df(new_data_list) #converts json to df
new_data_df = g.clean_df(new_data_df) #cleaning (drop some cols, fix datetimes, etc.)

#STEP 5 - Cleaned dataframe gets appended to the SQL DB
new_data_df.to_sql('content', sqlite_connection, if_exists='append')
sqlite_connection.close()