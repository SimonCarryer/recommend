import pandas as pd
import numpy as np
from math import log, sqrt
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
import pickle


def load_user_likes(filepath):
	return pd.read_csv(filepath)
	
def make_matrix(df):
	users = list(df.user_id.unique())
	products = list(df.pattern_id.unique())
	data = np.ones(len(df))
	col = df.user_id.astype('category', categories=users).cat.codes
	row = df.pattern_id.astype('category', categories=products).cat.codes
	N = len(users)
	idf = [1. + log(N / (1. + p)) for p in df.groupby('user_id').size()]
	weighted = [sqrt(hits) * idf[userid] for hits, userid in zip(data, col)]
	return csr_matrix((weighted, (row, col)), shape=(len(products), len(users))), products

if __name__ == '__main__':
	print('loading data')
	data_path = '../../think_data/user_data.csv' #'s3://ravelry-data/user_data.csv'
	user_df = load_user_likes(data_path)
	sampled_df = user_df.sample(10000)
	print('making matrix')
	matrix = make_matrix(sampled_df)
	print('doing decomposition')
	shrinky = TruncatedSVD(300)
	shrunk_matrix = shrinky.fit_transform(matrix)
	print('pickling!')
	pickle.dump(shrunk_matrix, open( "shrunk_matrix.p", "wb" ))