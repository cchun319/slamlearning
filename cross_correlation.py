#! /usr/bin/python3

import numpy as np
import math
## develop a mini example for pose optimization 
## use quratic form and gauss newton

## given: landmark true poses, odom observations

def R(theta:float):
    return np.array([[math.cos(theta), -math.sin(theta)],[ math.sin(theta), math.cos(theta)]]) 

def se2ToSE2(x):
    assert x.shape == (1, 3) or len(x) == 3
    ret = np.identity(3)
    ret[0:2, 0:2] = R(x[2])

    ret[0:2, 2] = x[:2]

    return ret

def SE2Tose2(t):
    assert t.shape == (3, 3)
    ret = [0] * 3

    ret[0:2] = t[0:2, 2]
    ret[2] = np.arctan2(t[1,0], t[0,0])

    return np.array(ret)

def covariance_progress():
    pass # estimate the uncertainty without landmark

# add noises
def add_noise(x, scale:list):
    ret = []
    for i, j in zip(x, scale):
        # print(f"i: {i}\nj: {j}")
        ret.append(np.random.normal(loc=0, scale=j) + i)
    return np.array(ret)

def observe_vector(x:list, l:list):
    # l, pos2 in world frame
    # x, robot pos2 in world frame
    # return observation vector in robot frame
    assert len(x) == 3
    assert len(l) == 2
    
    return l - x[:2]

def error(residuals_list, covariances):
    # r: 1 x n 
    residual = np.array([r for rs in residuals_list for r in rs])
    dimension = len(residual)
    covariance = np.zeros((dimension, dimension))
    print(f"Error dim {dimension}")
    offset = 0

    for r, cov in zip(residuals_list, covariances):
        covariance[offset:offset + len(r), offset:offset + len(r)] = cov
        offset += len(r)

    return 0.5 * residual.T @ np.linalg.inv(covariance) @ residual

def inverse(m):
    return np.linalg.inv(m)

# print(se2ToSE2(x_0))
# print(se2ToSE2(x_1))

# print(np.linalg.inv(se2ToSE2(x_0)))    

x_0 = np.array([0.0, 0.0, np.pi])

x_1 = np.array([1.0,1.0, np.pi/4])
x_2 = np.array([2.0, 1.0, 0])

landmark1 = np.array([0, 1])
landmark2 = np.array([1, 2])

true_x0_to_x1 = np.linalg.inv(se2ToSE2(x_0)) @ se2ToSE2(x_1)
true_x1_to_x2 = np.linalg.inv(se2ToSE2(x_1)) @ se2ToSE2(x_2)


odom_0_1 = add_noise(SE2Tose2(true_x0_to_x1) , [0.2, 0.2, 0.1]) 
odom_1_2 = add_noise(SE2Tose2(true_x1_to_x2) , [0.2, 0.2, 0.1]) 

t_0 = x_0
t_1 = SE2Tose2(se2ToSE2(t_0) @ se2ToSE2(odom_0_1))
print(f"t1 :{t_1}")
t_2 = SE2Tose2(se2ToSE2(t_1) @ se2ToSE2(odom_1_2))

r1 = inverse(se2ToSE2(odom_0_1)) @ inverse(se2ToSE2(t_0)) @ se2ToSE2(t_1) 
r2 = inverse(se2ToSE2(odom_1_2)) @ inverse(se2ToSE2(t_1)) @ se2ToSE2(t_2) 

r1_cov = np.identity(3) * 0.1
r2_cov = np.identity(3) * 0.1

print(f"error of odom: {error([SE2Tose2(r1), SE2Tose2(r2)], [r1_cov, r2_cov])}")

print(f"r1: {SE2Tose2(r1)}\nr2: {SE2Tose2(r2)}")

# TODO: landmark gives orientation
h1 = add_noise(observe_vector(t_1, landmark1), [0.01, 0.01])
h2 = add_noise(observe_vector(t_2, landmark2), [0.01, 0.01])

h1_aug = np.append(h1, [0])
h2_aug = np.append(h2, [0])
h1_cov = np.identity(2) * 0.01
h2_cov = np.identity(2) * 0.01

l1_hat = se2ToSE2(t_1) @ se2ToSE2(h1_aug)
l2_hat = se2ToSE2(t_2) @ se2ToSE2(h2_aug)

print(f" l2hat {SE2Tose2(l2_hat)}")

print(f"rl1 {landmark1 - SE2Tose2(l1_hat)[0:2]} rl2 {landmark2 - SE2Tose2(l2_hat)[0:2]}")

rl1 = landmark1 - SE2Tose2(l1_hat)[0:2]
rl2 = landmark2 - SE2Tose2(l2_hat)[0:2]

print(f"error of system: {error([SE2Tose2(r1), SE2Tose2(r2), rl1, rl2], [r1_cov, r2_cov, h1_cov, h2_cov])}")


for i in range(30):
    # stack residual[t_0, t_1, t_2, l_1, l_2], x = [x1, x2]
    # caculate jacobian
    # gauss-newton
    # [optional] fixed leg,
    # update the state
    # plot error
    pass

sensor_noise = np.random.normal(loc=0, scale=0.01, size=((2, 2))) # meter
odom_noise = np.random.normal(loc=0, scale=0.1, size=((2, 2))) # meter
odom_ang_noise = np.random.normal(loc=0, scale=0.05, size=((2, 1))) # 0.05 radian ~ 3deg 

prior_noise = np.random.normal(loc=0, scale=0.01, size = ((1, 3)))

t_0 = prior_noise + x_0
print(t_0)

t_1 = x_1
t_1[:2] += odom_noise[0,:]
t_1[2] += odom_ang_noise[0,:]

h1 = observe_vector(t_1, landmark1)
h1 += sensor_noise[0,:] 

print(f"pose: {t_1} obs: {h1}")


t_2 = x_2
t_2[:2] += odom_noise[1,:]
t_2[2] += odom_ang_noise[1,:]

h2 = observe_vector(t_2, landmark2)
h2 += sensor_noise[1,:] 
print(f"pose: {t_2} obs: {h2}")
