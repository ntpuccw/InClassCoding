import numpy as np
import matplotlib.pyplot as plt

# define the function
f = lambda x : x[0] * np.exp(-x[0]**2 - x[1]**2)
# create a mesh grid 
n = 100
x = np.linspace(-2, 2, n)
y = np.linspace(-2, 3, n)
X, Y = np.meshgrid(x, y) # mesh grid matric
Z = f([X, Y]) # evaluate the function on the grid
 
# for wireframe, control the wire density by rstride and cstride
fig = plt.figure(figsize=(9, 6))
ax = plt.axes(projection = '3d')
ax.plot_wireframe(X, Y, Z, color ='blue',
    alpha=0.3, rstride = 1, cstride = 1) # rstride=4, cstride=4
ax.set_xlabel('X'), ax.set_ylabel('Y')
ax.set_zlabel('f(X,Y)')
# set the view angle
ax.view_init(10, -60)  #(elev=-165, azim=60)
plt.title('Wireframe (Mesh) Plot')
plt.show()