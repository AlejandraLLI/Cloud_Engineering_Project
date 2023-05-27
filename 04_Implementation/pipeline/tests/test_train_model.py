# libraries for testing
import pytest
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator
from unittest.mock import patch, MagicMock
import src.train_model as tm

# Sample test data and configuration
X = pd.DataFrame({
    'feature1': np.random.rand(100),
    'feature2': ['cat', 'dog']*50,
    'price': np.random.rand(100)
})

config = {
    'train_test_split': {"test_size": 0.2, "random_state": 42},
    'numerical_features': ['feature1'],
    'categorical_features': ['feature2'],
    'models': {
        'model1': {'class': 'LinearRegression', 'parameters': {}}
    }
}

# Sample test model
class MockEstimator(BaseEstimator):
    def fit(self, X, y):
        pass
    def predict(self, X):
        return np.ones(len(X))


def test_define_preprocessor():
    preprocessor = tm.define_preprocessor(config)
    assert len(preprocessor.transformers) == 2
    assert preprocessor.transformers[0][0] == 'num'
    assert preprocessor.transformers[1][0] == 'cat'


def test_train_model():
    preprocessor = tm.define_preprocessor(config)
    model = MockEstimator()
    trained_model = tm.train_model(preprocessor, model, X, X['price'])
    assert isinstance(trained_model, Pipeline)


def test_calculate_metrics():
    y_test = pd.Series([1, 2, 3, 4, 5])
    y_pred = pd.Series([1.5, 2.5, 3.5, 4.5, 5.5])
    metrics = tm.calculate_metrics(y_test, y_pred)
    assert isinstance(metrics, dict)
    assert 'MSE' in metrics
    assert 'MAE' in metrics
    assert 'RMSE' in metrics
    assert 'R2' in metrics
