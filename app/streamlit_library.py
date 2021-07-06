import pandas as pd
import streamlit as st

def get_data():
	"""Goes to SQL database, get's all the data, and makes a dataframe"""

	pd.set_option('display.max_colwidth', None)

	from sqlalchemy import create_engine
	engine = create_engine('sqlite:///data/guardian_content.db', echo=False)

	# Query to get all news articles and filter out stuff we don't carer about like the university guide and obituaries.
	news_query = "SELECT *\
              FROM content\
              WHERE\
              pillarName = 'News' AND\
              type = 'article' AND\
              webTitle NOT LIKE '%university rankings%' AND\
              webTitle NOT LIKE '%University guide%'AND\
              webTitle NOT LIKE '%obituary%';"
	news_df = pd.read_sql(news_query, engine)
	news_df['pub_datetime'] = pd.to_datetime(news_df['pub_datetime'])

	return news_df

def create_datetime(m, d, y, h):
	"""Coverts ints to string that can be passed as datetime."""
	sep_d = '-'
	sep_t = ':'
	date = sep_d.join([str(m), str(d), str(y)])
	time = sep_t.join([str(h), '00', '00'])
	return date + ' ' + time

def datetime_string_format(datetimeseries, unit):
	"""
	Function for processing datetime formats to only show certain units (i.e. If grouping weekly, we don't want to see hours in datetimes.)

	datetimeseries: series of some metric grouped by date (date as index)
	unit: frequency of grouping ('H', 'D', 'W', etc.)
	returns a  generic date format string
	"""
	   
	start_datetime = datetimeseries.index.min()
	end_datetime = datetimeseries.index.max()

	if unit == 'H':
		format = '%H:00'
		if start_datetime.day != end_datetime.day:
			format = '%m/%d %H:00'
	elif unit == 'D' or unit == 'W':
		format = '%b %d, %y'
	elif unit == 'M':
		format = '%b %y'
	else:
		format = '%y'

	return format

from upsetplot import plot
import matplotlib.pyplot as plt

def keyword_plot(period_news, keywords):
	"""
	Generates boolean columns each keyword if it shows up in a headline. Then uses the boolean counts to make keyword timeseries.
	"""
	cat_bools = period_news.iloc[:, 8:]
	keywords_count_series = cat_bools.fillna(False).groupby(keywords).count()['pub_datetime']

	fig = plt.figure()
	plot(keywords_count_series, fig=fig, sort_by="cardinality", facecolor='navy')
	return fig

def show_more(period_news, i):
	"""
	Displays more stories in the 'Recent Stories' section.
	"""
	date_and_time = period_news.iloc[i, 8]
	title = period_news.iloc[i, 5]
	char_lim = 60
	if len(title) > char_lim:
	 	title = title[0:char_lim+1] + '...'
	link = period_news.iloc[i, 6]
	st.write(f"{date_and_time} [{title}]({link})")

def show_headlines(period_news):
	"""
	Displays links to stories.
	"""
	for i in range(50):
		try:
			show_more(period_news, i)
		except IndexError:
			break