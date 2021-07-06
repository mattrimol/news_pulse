# Internal and exteranl Streamlit libraries
import streamlit as st
st.set_page_config(layout='wide')
import streamlit_library as stlib
from streamlit_tags import st_tags #https://pypi.org/project/streamlit-tags/

# Data loading and handeling
import pandas as pd
import numpy as np
pd.set_option('display.max_colwidth', None)

news_df = stlib.get_data()

from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.units as munits
import datetime
from calendar import monthrange

# Contains functions for topic modeling
import news_nlp

st.header('**The Guardian News Cycle Dashboard**')

#Set start datetime
first_y = news_df['pub_datetime'].min().year
last_y = news_df['pub_datetime'].max().year

#datetime start/end inputs
#start_col, end_col = st.sidebar.beta_columns(2)
with st.sidebar.beta_container():
	start_col, end_col = st.beta_columns(2)

	with start_col:
		st.header('Start')
		with st.beta_container():
			start_y = st.selectbox('year', (range(first_y, last_y + 1)), key='start_y')
			start_m = st.selectbox('month', (range(1, 13)), key='start_m')
			start_d = st.number_input('day', 1, monthrange(start_y, start_m)[1], 1, key='start_d')
			start_h = st.selectbox('hour', (range(24)), key='start_h')
			start_datetime = stlib.create_datetime(start_m, start_d, start_y, start_h)

	with end_col:
		st.header('End')
		with st.beta_container():
			end_y = st.selectbox('year', (range(first_y, last_y + 1)), key='end_y')
			today = datetime.date.today()
			month_max = 12
			if end_y == today.year:
				end_m = st.selectbox('month', (range(1, today.month + 1)), key='end_m')
				if end_m == today.month:
					end_d = end_d = st.number_input('day', 1, today.day, 1, key='end_d')
				else:
					end_d = st.number_input('day', 1, monthrange(end_y, end_m)[1], 1, key='end_d')
			else:
				end_m = st.selectbox('month', (range(1, 13)), key='end_m')
				end_d = st.number_input('day', 1, monthrange(end_y, end_m)[1], 1, key='end_d')
			end_h = st.selectbox('hour', (range(24)), key='end_h')
			end_datetime = stlib.create_datetime(end_m, end_d, end_y, end_h)
			if pd.to_datetime(end_datetime) <= pd.to_datetime(start_datetime):
				st.write('End must be after start')
	
	keywords = st_tags(label='# Enter Keywords:', text='Press enter to add more', suggestions=['Biden', 'Football'], maxtags = 20, key='keywords')

# Filtering the data for the start and end time inputs.
search_terms = '|'.join(keywords)

if search_terms:
    period_news = news_df[(news_df['pub_datetime'] >= start_datetime) & (news_df['pub_datetime'] < end_datetime)].sort_values('pub_datetime', ascending=False)
else:
    period_news = news_df[(news_df['pub_datetime'] >= start_datetime) & (news_df['pub_datetime'] < end_datetime)]

#Create boolean columns for each keyword
if len(keywords) > 1:
    for word in keywords:
    	period_news[word] = period_news['webTitle'].str.contains(word, case=False)

freq_dict = {'Hourly': 'H', 'Daily': 'D', 'Weekly': 'W', 'Monthly': 'M', 'Annual': 'Y'}

col1, col2 = st.beta_columns([2, 2])

with col1:
	with st.beta_container():
		#Line chart
		freq = st.selectbox('Frequency', list(freq_dict.keys()))
		volume_by = period_news.resample(freq_dict[freq], on='pub_datetime').id.count().rename('Articles Published')
		
		#If multiple keywords we want a line chart comparing each one
		if len(keywords) > 1:
			volume_by_keywords = (period_news.groupby(pd.Grouper(key='pub_datetime', freq=freq_dict[freq])).agg({k:'sum' for k in keywords}))
			st.line_chart(volume_by_keywords, height= 400, use_container_width=True)
		else:
			st.line_chart(volume_by, height= 400, use_container_width=True)

	#Story link list
	if search_terms:
		if len(keywords) == 1:
			terms_str = search_terms
		else:
			terms_str = ', '.join(keywords[:-1]) + ' or ' + keywords[-1]
		st.header(f'Recent Stories about {terms_str}')
	else:
		st.header('Recent Stories')
	
	stlib.show_headlines(period_news)

with col2:
	#Topic explorer to do things with topic modeling algorithms
	topic_model = news_nlp.nlp_pipe()
	try:
		topic_model.load_pipe('fit_ten_topic_model_nouns.mdl')
		topic_model.st_print_topics(period_news, freq=freq_dict[freq])
	except FileNotFoundError:
		print('No topic model found')

	#Keyword mentions plot
	if len(keywords) > 1:
		st.header('Keyword Mentions in Headlines')
		st.pyplot(fig=stlib.keyword_plot(period_news, keywords))
		with st.beta_expander('More about this chart'):
			st.write('Here we can compare the frequency at which keywords show up in headlines, as well as when multiple keywords show up in the same headline. For\
			  example two dots colored in means that column represents headlines that contain *both* those keywords.')