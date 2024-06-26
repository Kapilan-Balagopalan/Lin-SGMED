from optimaldesign import *
from arms_generator import *
import numpy as np
import matplotlib.pyplot as plt


import numpy.random as ra
import numpy.linalg as la

from Lin_SGMED import *

from OFUL import *


def init(seed,K,n,d):
    np.random.seed(seed)
    noise_sigma = 1
    delta = 0.01
    S = 1
    sVal_dimension = d
    sVal_arm_size = K
    sVal_horizon = n
    sVal_lambda = d
    mVal_I = np.eye(sVal_dimension)
    mVal_lvrg_scr_orgn = sVal_lambda*mVal_I
    sVal_arm_set = A = sample_random(sVal_arm_size,sVal_dimension)
    theta_true = np.random.randn(d, 1)
    #print(theta_true.shape)
    #print(A.shape)
    theta_true = S*(theta_true/ (np.linalg.norm(theta_true, axis=0)))
    best_arm = np.argmax(np.matmul(A, theta_true))
    # print(best_arm)
    return sVal_dimension, sVal_arm_size,sVal_horizon, sVal_lambda, mVal_I, mVal_lvrg_scr_orgn, sVal_arm_set, theta_true,\
           noise_sigma, delta, S, best_arm






K = 100
n = 4000
d = 15

acc_regret_linSGMED = 0
acc_regret_OFUL  = 0
n_trials = 50
acc_regret_arr_linSGMED = np.zeros((n_trials,n))
acc_regret_arr_OFUL = np.zeros((n_trials,n))


for j in range(n_trials):
    seed = np.random.randint(1,15751)
    d, K, n, sVal_lambda, mVal_I, mVal_lvrg_scr_orgn, X, theta_true, noise_sigma, delta, S, best_arm = init(seed,K,n,d)
    R = noise_sigma
    linSGMED_inst = Lin_SGMED(X, sVal_lambda, R, S, flags=None, subsample_func=None, subsample_rate=1.0, multiplier=1.0)
    lam = 1 / (S ** 2)
    OFUL_inst = Oful(X, lam, R, S, flags=None, subsample_func=None, subsample_rate=1.0, multiplier=1.0)
    R = noise_sigma
    acc_regret_linSGMED = 0
    acc_regret_OFUL = 0
    for t in range(n):
        x_t_linSGMED, radius_sq_linSGMED = linSGMED_inst.next_arm()
        x_t_OFUL, radius_sq_OFUL = OFUL_inst.next_arm()

        inst_regret_linSGMED = calc_regret(x_t_linSGMED, theta_true, X)
        inst_regret_OFUL = calc_regret(x_t_OFUL, theta_true, X)

        acc_regret_linSGMED = acc_regret_linSGMED + inst_regret_linSGMED
        acc_regret_OFUL = acc_regret_OFUL + inst_regret_OFUL

        acc_regret_arr_linSGMED[j][t] = acc_regret_linSGMED
        acc_regret_arr_OFUL[j][t] = acc_regret_OFUL
        # print(Arm_t)
        reward_t_linSGMED = receive_reward(x_t_linSGMED, theta_true, noise_sigma, X)
        reward_t_OFUL = receive_reward(x_t_OFUL, theta_true, noise_sigma, X)

        linSGMED_inst.update(x_t_linSGMED, reward_t_linSGMED)
        OFUL_inst.update(x_t_OFUL, reward_t_OFUL)


t_alpha = 1.66

acc_regret_arr_linSGMED_mean = np.sum(acc_regret_arr_linSGMED, axis=0)/n_trials
acc_regret_arr_linSGMED_std = np.std(acc_regret_arr_linSGMED, axis=0, ddof=1)
acc_regret_arr_linSGMED_confidence_up = acc_regret_arr_linSGMED_mean + (t_alpha * acc_regret_arr_linSGMED_std)/np.sqrt(n_trials)
acc_regret_arr_linSGMED_confidence_down = acc_regret_arr_linSGMED_mean - (t_alpha * acc_regret_arr_linSGMED_std)/np.sqrt(n_trials)

acc_regret_arr_OFUL_mean = np.sum(acc_regret_arr_OFUL, axis=0)/n_trials
acc_regret_arr_OFUL_std = np.std(acc_regret_arr_OFUL, axis=0, ddof=1)
acc_regret_arr_OFUL_confidence_up = acc_regret_arr_OFUL_mean + (t_alpha * acc_regret_arr_OFUL_std)/np.sqrt(n_trials)
acc_regret_arr_OFUL_confidence_down = acc_regret_arr_OFUL_mean - (t_alpha * acc_regret_arr_OFUL_std)/np.sqrt(n_trials)





plt.plot(np.arange(n), acc_regret_arr_linSGMED_mean , label="Lin-SGMED")
plt.fill_between(np.arange(n),acc_regret_arr_linSGMED_confidence_down, acc_regret_arr_linSGMED_confidence_up)
plt.plot(np.arange(n), acc_regret_arr_OFUL_mean , label="OFUL")
plt.fill_between(np.arange(n),acc_regret_arr_OFUL_confidence_down, acc_regret_arr_OFUL_confidence_up)
# Naming the x-axis, y-axis and the whole graph
plt.xlabel("Time")
plt.ylabel("Regret")
plt.title("Regret with time")
plt.legend()
plt.show()