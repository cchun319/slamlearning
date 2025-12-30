#!/usr/bin/python3
'''
create grid, 20m x 20m
random points for landmarks
3 poses, with translation and rotation
2 transforms between the poses
keep the true values, find the seen lankmarks corrresponding the poses, indices, poses in cameras
'''
from manifpy import SE2, SE2Tangent

import numpy as np
from numpy.linalg import inv
import matplotlib.pyplot as plt

# https://dfki-ric.github.io/pytransform3d/_auto_examples/plots/plot_convention_rotation_global_local.html#sphx-glr-auto-examples-plots-plot-convention-rotation-global-local-py

def RagToDeg(rad):
    return rad / np.pi * 180

if __name__ == '__main__':
    x_0 = SE2.Identity()

    d_x = SE2Tangent(1, 2, 0.5)
    x_1 = x_0 + d_x
    x_1p = d_x + x_0

    print(f"pose: {x_0} dof: {SE2.DoF} dim: {SE2.Dim} transform: {x_0.transform()} translation: {x_0.translation()} angle: {x_0.angle()}")


    x_2 = x_1 + d_x
    

    # plt.plot(x_0.translation()[0], x_0.translation()[1], marker=(3, 1, RagToDeg(x_0.angle())), markersize=20, linestyle='None')
    # plt.plot(x_1.translation()[0], x_1.translation()[1], marker=(3, 0, RagToDeg(x_1.angle())), markersize=20, linestyle='None')
    # plt.plot(x_2.translation()[0], x_2.translation()[1], marker=(3, 0, RagToDeg(x_2.angle())), markersize=20, linestyle='None')
    print(f"pose: \n {x_0.translation()} {x_0.angle()}")
    print(f"pose: \n {x_1.translation()} {x_1.angle()}")
    print(f"pose: \n {x_1p.translation()} {x_1p.angle()}")
    print(f"pose: \n {x_2.translation()} {x_2.angle()}")

    # plt.xlim([-10,10])
    # plt.ylim([-10,10])
# 
    # plt.show()
