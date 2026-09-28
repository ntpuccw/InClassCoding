import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

n = 10
color=['blueviolet','r','m','fuchsia','hotpink','pink','indigo','b','k','purple']
x = np.arange(0, 10.1)
y = np.arange(0, 10.1)
x1 = [0, 5, -5, 0]
y1 = [0, -20, -20, 0]

angle = np.arange(0, 360, 1)

fig, ax = plt.subplots(1, figsize=(6, 6))

def animate(frame):
    ax.clear()
    ax.axis('off')  
    m_angle = frame
    for i in range(n):
        ax.plot(
            x.reshape(-1, 1) * np.cos((m_angle + 360 * i / n) * np.pi / 180),
            y.reshape(-1, 1) * np.sin((m_angle + 360 * i / n) * np.pi / 180),
            color=color[i]
        )
        x2 = 10 * np.cos((m_angle + 360 * i / n) * np.pi / 180)
        y2 = 10 * np.sin((m_angle + 360 * i / n) * np.pi / 180)
        x2_array = [x2 - 1, x2, x2 + 1, x2 - 1]
        y2_array = [y2, y2 + 1, y2, y2]
        x2_array = np.array(x2_array, dtype=np.float64)
        y2_array = np.array(y2_array, dtype=np.float64)
        x3_array = [x2 - 1, x2 + 1, x2 + 1, x2 - 1, x2 - 1]
        y3_array = [y2 + 1, y2 + 1, y2 - 1, y2 - 1, y2 + 1]
        x3_array = np.array(x3_array, dtype=np.float64)
        y3_array = np.array(y3_array, dtype=np.float64)
        ax.plot(
            x2_array,
            y2_array - 1,
            color=color[i]
        )
        ax.plot(
            x3_array,
            y3_array - 2,
            color=color[i]
        )
        ax.plot(
            10 * np.cos(angle.reshape(-1, 1) * np.pi / 180),
            10 * np.sin(angle.reshape(-1, 1) * np.pi / 180),
            color='k'
        )
    ax.plot(
        x1,
        y1,
        color='k'
    )

plt.gca().set_aspect('equal', adjustable='box')

ani = FuncAnimation(fig, animate, frames=np.arange(0, 360), interval=50)
plt.show()