"""Fits a topic model to a random sample of the data and saves its attributes locally"""

import news_nlp
from streamlit_library import get_data

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import NMF

news_df = get_data()

fit_on_N = 100000

ten_topic_model = NMF(10)

ten_topic_pipe_nouns_only = news_nlp.nlp_pipe(vectorizer=news_nlp.noun_only_vectorizer, model=ten_topic_model)
ten_topic_pipe_nouns_only.fit_new_data(news_df.sample(n=fit_on_N, random_state=42))
ten_topic_pipe_nouns_only.save_pipe('fit_ten_topic_model_nouns')