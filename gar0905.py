# draw the pdf of T distribution
import numpy as np
from scipy.stats import t, norm
import matplotlib.pyplot as plt

# degrees of freedom from 0.1:0.1:2.0 and 1:3:30
k = np.arange(0.1, 2, 0.1)
k = np.append(k, np.arange(1, 30, 3))
x = np.linspace(-6, 6, 1000)
fig = plt.figure(figsize = (6, 3))
# draw the pdf of standard normal distribution
z = norm.pdf(x, 0, 1)
plt.plot(x, z, linewidth = 3, color = 'r', label = 'Z distribution')

for i in range(len(k)):
    y = t.pdf(x, k[i])
    # plt.plot(x, y, color = 'b', alpha = 0.5, label = 'k = ' + str(k[i]))
    plt.plot(x, y, color = 'b', alpha = 0.5)
    plt.title('The degree of freedom = {}'.format(k[i]))
    plt.pause(0.5)

plt.legend()
plt.grid(True)
plt.show()