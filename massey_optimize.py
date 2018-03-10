import numpy as np
import sys
import math
from scipy.stats import beta
from scipy.optimize import minimize

def log(x):
    try:
        return math.log(x)
    except ValueError:
        return math.log(sys.float_info.min)

def logloss(x, p):
    return -np.mean([xi*log(pi) + (1.-xi)*log(1.-pi) for xi, pi in zip(x,p)])

def opt_rankdiff(data, ranker='MAS', exp_scale=True):
    """ x: normalized difference in ranking
    """
    ix = np.logical_and(data['W_'+ranker]>-1, data['L_'+ranker]>-1)  # find indeces where teams have a rank
    rank_diff = abs(data['W_'+ranker].values[ix] - data['L_'+ranker].values[ix])
    x = 1.*rank_diff / max(rank_diff)  # normalize by max difference

    if exp_scale:
        # Scale ranking diff by the rank of the best team. E.g. accounts for the idea that the difference
        # between 1-10 is bigger than 290-300.
        best_rank = np.min(data[['W_'+ranker,'L_'+ranker]].values[ix], axis=1)
        x *= np.exp(-best_rank / max(best_rank))

    y = data['W_'+ranker].values[ix] < data['L_'+ranker].values[ix]  # predict Pr of better team win
    return x, y

def beta_shift(x, a, b):
    return (1 + beta.cdf(x, a, b)) / 2

def beta_logloss(params, args):
    a = params[0]
    b = params[1]
    x = args[0]
    y = args[1]
    return logloss(y, beta_shift(x, a, b))

def optimize_beta(data, ranker='MAS', data_func=opt_rankdiff, init_params=[1,1], **kwargs):
    """ Find alpha and beta parameters to model data with a beta distribution  
    """
    x, y = data_func(data, ranker=ranker)
    return minimize(beta_logloss, init_params, args=[x,y], **kwargs)
