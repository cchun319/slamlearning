#! /usr/bin/python3

import numpy as np
import math



import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.ticker import LinearLocator

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Make data.
X = np.arange(-8, 8, 0.25)
Y = np.arange(-8, 8, 0.25)
X, Y = np.meshgrid(X, Y)
Z = ((X**2 + Y - 11)**2 + (Y**2 + X -7)**2)


# # Plot the surface.
surf = ax.plot_surface(X, Y, Z, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False, alpha = 0.2)

# Customize the z axis.
ax.set_zlim(0, 800)
ax.zaxis.set_major_locator(LinearLocator(10))
# A StrMethodFormatter is used automatically
ax.zaxis.set_major_formatter('{x:.02f}')

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

# plt.show()



def GetGradientAtXk(x): 
    return np.array([2*(x[0]**2 + x[1] - 11) * 2 * x[0] + 2 * (x[0] + x[1]**2 - 7),
                     2*(x[0]**2 + x[1] - 11) + 2 * (x[0] + x[1]**2 - 7) * 2 * x[1]])

def GetHessianAtXk(x):
    return np.array([[2 + 8*x[0]**2 + 4 * (x[0]**2 + x[1] - 11), 4 * (x[0] + x[1])],
                     [4 * (x[0] + x[1]), 2 + 8 * x[1]**2 + 4 * (x[0] + x[1]**2 - 7)]])

# x_0
# plot x: state in the graph
# https://infinity77.net/go_2021/scipy_test_functions_nd_H.html#go_benchmark.HimmelBlau 

iteration = 5
import copy
x = np.array([[-6.0], [-6.0]]) # 2 x 1
x_all = copy.deepcopy(x.T)
for i in range(iteration):
    H = GetHessianAtXk(x).reshape(2, 2)
    x += -np.linalg.inv(H) @ GetGradientAtXk(x)
    x_all = np.vstack((x_all, x.T))
    
print(x_all)
print(((x_all[:,0]**2 + x_all[:,1] - 11)**2 + (x_all[:,1]**2 + x_all[:,0] -7)**2))
ax.scatter(x_all[:,0], x_all[:,1], ((x_all[:,0]**2 + x_all[:,1] - 11)**2 + (x_all[:,1]**2 + x_all[:,0] -7)**2),
           color='r', s=200, label='Markers')
plt.show()


    # plot x
