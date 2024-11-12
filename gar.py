import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

N = 100
mu = 0
sigma = 1
x = norm.rvs(loc = mu, scale = sigma, size = N)
# plt.hist(x, edgecolor = 'y')
# plt.xlabel('x')
# plt.show()

# define a joint likelihood function for N samples
# 1. define a function for the likelihood of a single sample
def likelihood(x, mu, sigma):
    return norm.pdf(x, loc = mu, scale = sigma)
# 2. define a function for the joint likelihood of N samples
def joint(x, mu, sigma):
    return np.prod(likelihood(x, mu, sigma))
# 3. define a function for the log likelihood of N samples
def log_likelihood(x, mu, sigma):
    return np.sum(np.log(likelihood(x, mu, sigma)))


# draw a contour plot of the joint likelihood

mu = np.linspace(-1, 1, 200)
sigma = np.linspace(0.5, 1.5, 200)
L = np.zeros((len(mu), len(sigma)))

for i in range(len(mu)):
    for j in range(len(sigma)):
        L[i, j] = log_likelihood(x, mu[i], sigma[j])


# draw a 3D plot of the joint likelihood by wireframe

fig = plt.figure()
ax = plt.axes(projection = '3d')
MU, SIGMA = np.meshgrid(mu, sigma)
ax.plot_wireframe(MU, SIGMA, L, color ='blue',
    alpha=0.1, rstride = 1, cstride = 1)
# surf = ax.plot_surface(mu, sigma, L, rstride = 1, cstride = 1, cmap = cm.coolwarm, linewidth = 0, antialiased = False)
ax.set_xlabel('$\mu$')
ax.set_ylabel('$\sigma$')
ax.set_zlabel('Joint likelihood')
ax.set_title('Joint Likelihood')
ax.view_init(10, -60)  #(elev=-165, azim=60)
plt.show()