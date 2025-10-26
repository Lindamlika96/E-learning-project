from sklearn.base import BaseEstimator, TransformerMixin

class NameGetter(BaseEstimator, TransformerMixin):
    def __init__(self, name):
        self.name = name

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X  # ou X[[self.name]] si tu veux extraire une seule colonne

    def get_feature_names_out(self, input_features=None):
        return [self.name]
