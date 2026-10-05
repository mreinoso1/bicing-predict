import numpy as np
import pytest
from scipy.sparse import csr_matrix
from sklearn.linear_model import Ridge

from bicing_predict.models import model


@pytest.fixture
def data():
    rng = np.random.default_rng(seed = 12345)
    weights = np.array([0.8,5.,2.,8.,10.,100.,30.,-5.,1.,-100.])
    intercept = 2
    X_train = rng.standard_normal((200,10))
    y_train = (X_train @ weights) + intercept

    X_val = rng.standard_normal((100,10))
    y_val = (X_val @ weights) + intercept

    X_test = rng.standard_normal((50,10))
    y_test = (X_test @ weights) + intercept
    
    return X_train, X_val, X_test, y_train, y_val, y_test, weights, intercept

def cost(X,y,w,b):
    error = model.func(X, weights=w , intercept = b) - y
    J = error ** 2
    J = np.sum(J)
    J = J/(2*X.shape[0])
    return  J



def test_comparison_orac(data):
    X_train, _Xval,_Xtest,y_train,_yval,_ytest,_w,_i = data

    learning_rate = 0.0001
    epochs = 10000000
    param_reg = 10
    tolerance = 1e-15
    oracle = Ridge(alpha = param_reg * 2 * X_train.shape[0], tol = tolerance)
    oracle.fit(X_train,y_train)
    weights_orac = oracle.coef_
    intercept_orac = oracle.intercept_

    X_train = csr_matrix(X_train)
    weights = np.zeros(X_train.shape[1])
    pesos, inter = model.Adam(X_train, y_train, weights, tolerance , learning_rate, epochs,param_reg)
    print(pesos)
    print(weights_orac)
    print(inter)
    print(intercept_orac)
    assert np.allclose(weights_orac,pesos, rtol = 1e-3, atol = 1e-3)
    assert inter == pytest.approx(intercept_orac, rel = 1e-3)


def test_gradient(data):
    X_train, _X_val, _X_test, y_train, _y_val, _y_test, _, inter = data
    weights = np.array([1,2,3,4,5,6,7,8,9,10]).astype(float)
    h = 1e-6
    manual_der = []
    for i in range(weights.shape[0]):
        weights[i] += h
        limit_r = cost(X_train,y_train,weights,inter)
        weights[i] -= h*2
        limit_l = cost(X_train,y_train,weights,inter)
        J_der = (limit_r - limit_l) / (2*h)
        manual_der.append(J_der)
        weights[i] += h

    manual_der = np.array(manual_der)
    gradient, _ = model.gradient(X_train,y_train,weights,X_train.shape[0],0,inter)
    assert np.allclose(manual_der,gradient,atol = 1e-3)