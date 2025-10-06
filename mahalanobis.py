#!/usr/bin/python3
# https://cookierobotics.com/007/
# https://matplotlib.org/3.1.1/gallery/statistics/confidence_ellipse.html#sphx-glr-gallery-statistics-confidence-ellipse-py
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
mu, sigma = 3, 0.5 # mean and standard deviation
s1 = np.random.normal(mu, sigma, 500)

mu2, sigma2 = 5, 2 # mean and standard deviation
s2 = np.random.normal(mu2, sigma2, 500)

def mahalanobis(x, mean, cov):
    return np.sqrt((x - mean).T @ np.linalg.inv(cov) @ (x - mean))



fig, ax = plt.subplots()

ax.scatter(s1, s2)

ax.set_xlim(0, 15)
ax.set_ylim(0, 15)

meanx = np.mean(s1)
meany = np.mean(s2)

cov_x = np.mean((s1 - meanx)**2)

cov_y = np.mean((s2 - meany)**2)
# print(np.mean(s1 * s2) - meanx * meany)
cov_xy = np.mean(s1 * s2) - meanx * meany
print(f"x: {meanx}, y: {meany}, || stdx: {np.sqrt(cov_x)}, stdy: {np.sqrt(cov_y)} || covxy: {np.sqrt(cov_xy)}")

l1 = (cov_x + cov_y) / 2.0 + np.sqrt(cov_xy**2 + ((cov_x - cov_y) / 2.0)**2)

l2 = (cov_x + cov_y) / 2.0 - np.sqrt(cov_xy**2 + ((cov_x - cov_y) / 2.0)**2)

theta = np.arctan2(l1 , cov_xy)

ellipse = Ellipse(xy=(meanx, meany), width= 2 * np.sqrt(6 * cov_x), height= 2 * np.sqrt(6 * cov_y) , angle=np.pi/2, edgecolor='blue', facecolor='none', linewidth=2)

# Add ellipse to the plot
ax.add_patch(ellipse)

d1 = np.array([meanx + 3*sigma, meany])

d2 = np.array([meanx, meany + 3 * sigma2])

da = np.vstack((d1, d2))
ax.scatter(da[:, 0], da[:, 1], marker='*', c='r')
center = np.array([meanx, meany])

cov_all = np.array([[cov_x, cov_xy], [cov_xy, cov_y]])
                  
print(f"mahalanobis a: {mahalanobis(d1, center, cov_all)}, b: {mahalanobis(d2, center, cov_all)}")
# 95% 
# count, bins, ignored = plt.hist(s, 30, density=True)
# plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) *
#                np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
#          linewidth=2, color='r')
plt.show()



