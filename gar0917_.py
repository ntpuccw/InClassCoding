# plot chi-square distribution with different degrees of freedom
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats 

fig, ax = plt.subplots(figsize=(8, 3))
x_left, x_right = 0, 50
df = np.arange(4, 30, 1) # degrees of freedom
x = np.linspace(x_left, x_right, 1000)

for i in df:
    y = stats.chi2.pdf(x, df=i)
    ax.plot(x, y, color="blue", label="$df$={}".format(i))
    ax.set_title("df={}".format(i))
    # pause to see the plot
    plt.pause(0.3)
# ax.legend()
ax.grid()
ax.set_title("Chi-Square Distribution with Different Degrees of Freedom")
ax.set_xlabel("x")
ax.set_ylabel("y")
plt.show()