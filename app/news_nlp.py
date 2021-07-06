import pandas as pd
import numpy as np
pd.set_option('display.max_colwidth', None) #Need this to see full headlines
import pickle

# To load and save fit models
from pathlib import Path
root = Path('.')

# NLP Libraries
import re
import spacy
nlp = spacy.load('en_core_web_sm')
lemmatizer = spacy.lang.en.English()
from nltk.corpus import stopwords
stop_words = stopwords.words('english') # Defining a global variable stopwords list
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import TruncatedSVD, NMF, PCA

# Add any stopwords if needed
stop_words.extend(['m', 'say', 'could', 'people', 'plan', 'woman', 'man'])

def preprocessor(doc):
	"""
	Takes in a single doc and returns a doc with stop words and symbols removed and lematization.
	"""
	# Remove symbols
	doc = re.sub(r"[^\w\s]", '', doc, flags=re.UNICODE)
	# Remove extra spaces created in previous step
	doc = re.sub(' +', ' ', doc)
	# Lemmatize and remove stop words
	#doc = [token.lemma_ for token in nlp(doc) if not token.is_stop]
	doc = [token.lemma_ for token in nlp(doc) if token.text.lower() not in stop_words]
	return ' '.join(doc)

def entity_rec(spacy_doc):
	"""
	Takes in a Spacy object and returns a list of recognized entities and a list of the words used in any of the entities.
	"""
	ents = [ent.text for ent in spacy_doc.ents]
	# Splits up the entities in their single words so we don't token them twice
	ent_words = []
	for ent in ents:
		ent_words.extend(ent.split(' '))
	
	return ents, ent_words

def tokenizer(doc):
	"""
	Takes in a doc and returns a list of tokens with entity recognition
	"""
	spacy_doc = nlp(doc) #Identifies words as spacy objects so we can get their properties
	ents, ent_words = entity_rec(spacy_doc)
	non_ents = [token.text.lower() for token in spacy_doc if token.text not in ent_words]
	return ents + non_ents

def noun_only_tokenizer(doc):
	"""
	Takes in a doc and returns a list of NOUN ONLY tokens with entity recognition.
	"""
	spacy_doc = nlp(doc) #Identifies words as spacy objects so we can get their properties
	ents, ent_words = entity_rec(spacy_doc)
	non_ents = [token.text.lower() for token in spacy_doc if token.text not in ent_words and token.pos_ == 'NOUN']
	return ents + non_ents

#Global variables forto nlp_pipe
vectorizer = CountVectorizer(strip_accents='unicode', preprocessor=preprocessor, tokenizer=tokenizer, min_df=0.01, max_df=0.95)
noun_only_vectorizer = CountVectorizer(strip_accents='unicode', preprocessor=preprocessor, tokenizer=noun_only_tokenizer, min_df=0.01, max_df=0.95)

# Human decided topiuc names
ten_topic_names = {0: 'UK News',
				   1: 'Brexit',
				   2: 'US News',
				   3: 'Letters',
				   4: 'Crime',
				   5: 'Climate',
				   6: 'Children',
				   7: 'Trump',
				   8: 'Global Politics',
				   9: 'EU Politics'}

class nlp_pipe:
	"""
	Object to create n topics for a corpus and group docs into each topic.
	"""
	
	def __init__(self, vectorizer=None, model=None):
		self.vectorizer = vectorizer
		self.model = model
		self._is_fit = False
		self.doc_word = None
		self.doc_topic = None
		self.corpus = None
		self.data = None
					
	def fit_new_data(self, df):
		# Keeping the original data frame with all the columns as an attribute for now.
		self.data = df
		self.corpus = list(df['webTitle'])
		self.doc_word = self.vectorizer.fit_transform(self.corpus)
		self.doc_topic = self.model.fit_transform(self.doc_word)
		self._is_fit = True

	def save_pipe(self, filename):
		if type(filename) != str:
			raise TypeError("filename must be a string")
		if filename[-4:] != '.mdl':
			filename += '.mdl'
		pickle.dump(self.__dict__, open(root/"fit_models"/filename,'wb'))

	def load_pipe(self, filename):
		if type(filename) != str:
			raise TypeError("filename must be a string")
		if filename[-4:] != '.mdl':
			filename += '.mdl'
		self.__dict__ = pickle.load(open(root/"fit_models"/filename,'rb'))

	def st_print_topics(self, period_df, freq='D', show_n_tokens=10, show_n_docs=5):
		"""
		Prints topic name, top words, links, and time series graph for each topic
		"""
		
		# Streamlit and my streamlit stuff
		import streamlit as st
		import streamlit_library as stlib
		import matplotlib.pyplot as plt

		features = self.vectorizer.get_feature_names()

		doc_topic_df = pd.DataFrame(self.doc_topic.round(5), index=self.corpus, columns=[n for n in range(self.model.n_components)])
		doc_topic_df = doc_topic_df[doc_topic_df.index.isin(list(period_df['webTitle']))]

		# Join doc topic df with full data set (on headline) so we can get the pub_datetime for each story in the doc_topic_df
		doc_topic_time_df = doc_topic_df.join(period_df[['webTitle', 'pub_datetime']].set_index('webTitle'), how='left')
		
		# Groups by `freq` and sums the topic scores
		daily_topic_activity = doc_topic_time_df.groupby(pd.Grouper(key='pub_datetime', freq=freq)).mean()

		for ix, topic in enumerate(self.model.components_):
			top_words = [features[i].upper() for i in topic.argsort()[:-show_n_tokens - 1:-1]]
			# We can't be showing coronavirus stuff before it was even known to be a thing
			if period_df['pub_datetime'].max().year < 2020:
				if 'CORONAVIRUS' in top_words: top_words.remove('CORONAVIRUS')
			top_words = " | ".join(top_words)

			if len(self.model.components_) == 5:
				name = five_topic_names[ix]
			else:
				name = ten_topic_names[ix]
			st.write(f'**{name}**')
			st.write(top_words)

			for doc in doc_topic_df.nlargest(show_n_docs, [ix]).index:
				link = period_df.loc[period_df['webTitle'] == doc, 'webUrl'].iloc[0]
				st.write(f'[{doc}]({link})')
			
			with st.beta_expander('Show Chart'):
				# Plot a time series (grouped by `freq`) for the specified topic
				fig, ax = plt.subplots()
				ax.plot(daily_topic_activity.index, daily_topic_activity[ix])
				ax.tick_params(axis="x", rotation=50)
				st.pyplot(fig)