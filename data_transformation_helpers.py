from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, LabelEncoder
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.text import TfidfTransformer

class NameGettingPipeline(Pipeline):
    
    def get_feature_names(self):
        try:
            return self.steps[-1][1].get_feature_names()
        except: # using error handling for process control is cool, right?
            return self.steps[0][1].get_feature_names()
        
class OneHotWrapper(TransformerMixin):
    def __init__(self):
        self.encoder = LabelEncoder()
        self.transformer = OneHotEncoder()
        
    def fit(self, X, y=None):
        encoded = self.encoder.fit_transform(X).values.reshape(-1, 1)
        return self.transformer.fit(encoded)
    
    def transform(self, X, y=None):
        encoded = self.encoder.transform(X).values.reshape(-1, 1)
        return self.transformer.transform(encoded)
    
    def get_feature_names(self):
        return self.encoder.classes_
    
class MinMaxWrapper(TransformerMixin):
    def __init__(self):
        self.transformer = MinMaxScaler()
        
    def fit(self, X, y=None):
        return self.transformer.fit(X.values.reshape(-1, 1))
    
    def transform(self, X, y=None):
        return self.transformer.transform(X.values.reshape(-1, 1))

class ItemSelector(TransformerMixin):
    def __init__(self, key):
        self.key = key
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        return X[self.key]
    
    def get_feature_names(self):
        return [self.key]