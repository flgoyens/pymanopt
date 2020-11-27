import autograd.numpy as np


def my_projection(X, alpha):
    # print("check max")
    if(np.amax(np.abs(X)) >= alpha):
        print("projecting")
    X[X > alpha] = alpha
    X[X < -alpha] = -alpha
    return X
