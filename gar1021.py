# draw the wireframe for f(x,y) = x*exp(-x^2 - y^2)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')

# Make data.
x = np.arange(-3, 3, 0.1)
y = np.arange(-3, 3, 0.1)
X, Y = np.meshgrid(x, y)
Z = X * np.exp(-X**2 - Y**2)

# Plot the wireframe.
ax.plot_wireframe(X, Y, Z, cmap=cm.coolwarm,
    rstride=1, cstride=1, linewidth=0.5)

ax.view_init(10, -60)  #(elev=-165, azim=60)
# Add a color bar which maps values to colors.
# fig.colorbar(surf, shrink=0.5, aspect=5)
ax.set_xlabel('X axis')
ax.set_ylabel('Y axis')
ax.set_zlabel('Z axis')
plt.show()