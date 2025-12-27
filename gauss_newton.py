#! /usr/bin/python3

import numpy as np
import math



import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.ticker import LinearLocator

np.random.seed(0)
x = np.linspace(0, 2, 50)
a_true, b_true, c_true = 2.5, -1.3, 0.5
y_clean = a_true * np.exp(b_true * x) + c_true
y = y_clean + 0.12 * np.random.randn(len(x))

def model(params, x):
    a, b, c = params
    return a * np.exp(b * x) + c

def residual(params, x, y):
    a, b, c = params
    return y - (a*np.exp(b*x) + c)

def jacobian(params, x):
    a, b, c = params
    ret = np.zeros((len(x), 3)) # row vector
    ret[:, 0] = -np.exp(b*x)
    ret[:, 1] = -a *x *np.exp(b*x)
    ret[:, 2] = -1
    return ret

# print("Estimated params:", p_opt)
# print("Final cost:", history[-1][1])

# Plot


lm = True
prev_res = -1
state = np.zeros((1, 3)) + 5.0
lam_ = 2 if lm == True else 0

for i in range(100):
    params = state[0, 0], state[0, 1], state[0, 2]
    curr_y =  model(params, x)
    jac = jacobian(params, x)
    res = residual(params, x, y)

    curr_loss = res.T @ res

    ## TODO: is it ill-conditioned?

    # naive newton gauss
    H = jac.T @ jac
    huristic = lam_ * np.eye(3) if lm == True else 0

    dx = -np.linalg.pinv(H + huristic) @ jac.T @ res
    print(f"dx {dx}")
    tho = float('inf')
    if lm == True:
        # compute tho: how much does gn actually drops versus prediction
        # predicted: 
        t_state = state + dx

        params = t_state[0, 0], t_state[0, 1], t_state[0, 2]
        res = residual(params, x, y)
    
        pred_loss = -jac.T @ res @ dx - 0.5 * dx.T @ (H + huristic) @ dx # predicted: f(xk) - f(xk + dx)

        update_loss = res.T @ res
        actual_loss =  curr_loss - update_loss  # should go down
        tho = actual_loss / pred_loss
        ## print the change and error
        if tho <= 0:
            dx = 0
            lam_ *= 10
        else:    
            if tho >= 0.75:
                lam_ /= 2.0
            elif tho <= 0.25:
                lam_ *= 2.0
        print(f"\tlam_ {lam_:.2f} | tho {tho:.2f} | predicted loss {pred_loss:.2f} | actual loss {actual_loss:.2f}")

    state += dx
            
    print(f"params: {state} | res: {curr_loss:.2f}")

params = state[0, 0], state[0, 1], state[0, 2]

plt.scatter(x, y, label="data")
xs = np.linspace(x.min(), x.max(), 200)
plt.plot(xs, model(params, xs), label="LM fit", linewidth=2)
plt.plot(xs, model([a_true, b_true, c_true], xs), '--', label="true")
plt.legend()
plt.show()