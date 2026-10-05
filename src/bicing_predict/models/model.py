from __future__ import annotations

import numpy as np


def func(X, weights: np.ndarray, intercept):
    products = X @ weights
    return products + intercept


def gradient(batch_X, batch_y, weights, batch_size, regu_param, intercept):
    error = func(batch_X, weights=weights, intercept=intercept) - batch_y
    sumat = batch_X.T @ error
    gradient_w = (sumat / batch_size) + (regu_param * weights * 2)
    gradient_inter = np.mean(error)
    return gradient_w, gradient_inter


def Adam(
    X,
    y: np.ndarray,
    weights: np.ndarray,
    tolerance,
    learning_rate,
    epochs,
    regu_param,
    beta1=0.9,
    beta2=0.999,
):
    epsilon = 1e-8
    moment_m = np.zeros(weights.shape)
    moment_v = np.zeros(weights.shape)
    moment_m_intercept = 0
    moment_v_intercept = 0
    instant = 1
    intercept = 0
    for i in range(epochs):
        a_t = learning_rate
        grd, grd_inter = gradient(X, y, weights, X.shape[0], regu_param, intercept)
        moment_m = (moment_m * beta1) + ((1 - beta1) * grd)
        moment_v = (moment_v * beta2) + ((1 - beta2) * (grd**2))
        m_bias_correct = moment_m / (1 - (beta1**instant))
        v_bias_correct = moment_v / (1 - (beta2**instant))
        moment_m_intercept = (moment_m_intercept * beta1) + ((1 - beta1) * grd_inter)
        moment_v_intercept = (moment_v_intercept * beta2) + (
            (1 - beta2) * (grd_inter**2)
        )
        weights = weights - (
            (a_t / (np.sqrt(v_bias_correct) + epsilon)) * m_bias_correct
        )
        m_bias_correct_intercept = moment_m_intercept / (1 - (beta1**instant))
        v_bias_correct_intercept = moment_v_intercept / (1 - (beta2**instant))
        intercept = intercept - (
            (a_t / (np.sqrt(v_bias_correct_intercept) + epsilon))
            * m_bias_correct_intercept
        )
        instant += 1

        if (i % 1000) == 0:
            norma = np.sqrt(np.sum(grd**2) + grd_inter**2)
            if norma < tolerance:
                break

    return weights, intercept
