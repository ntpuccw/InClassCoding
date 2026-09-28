import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Rectangle
from matplotlib.animation import FuncAnimation

n = 8
fig, ax = plt.subplots()
radius = 3
theta = np.pi / (n / 2)

# 存所有圖形的列表
cars = []

# 初始化函數

def init():
    x= [0, 0]
    y = [0, 3]
    center = (0, 0)
    radius = 3
    circle = plt.Circle(center, radius, color="lightseagreen", fill=False, linewidth=4, zorder=2)
    circle_small = plt.Circle(center, radius - 1.5, color="lightseagreen", fill=False, linewidth=4, zorder=5)
    ax.add_artist(circle)
    ax.add_artist(circle_small)
    # 畫地基
    x_ground = [0, -1.8, 1.8, 0]
    y_ground = [0, -5, -5, 0]
    ax.plot(x_ground, y_ground, color="slateblue", linewidth=4.5, zorder=1)
    rectangle = Rectangle((-2,-5.5), 4, 1, color='slateblue', zorder=1)
    plt.gca().add_patch(rectangle)

    return cars

# 更新函数
def update(frame):
    
    # 清除上一張圖
    for car in cars:
        car.remove()

    cars.clear()
    ax.plot((0,0), (0,3), color="silver", linewidth=4, zorder=3)
    a = 2 * np.pi * frame / 360  # 對應幀數的弧度
    
    for j in np.arange(a, 2 * np.pi + a, theta):
        x = radius * np.sin(j)
        y = radius * np.cos(j) - 0.5
        center = (x, y)
        radius_cars = 0.6

        # 上半圆
        upper_circle = Wedge(center, radius_cars, 0, 180, fc='blue', alpha=0.5, zorder=4)
        ax.add_patch(upper_circle)
        cars.append(upper_circle)

        # 下半圆
        lower_circle = Wedge(center, radius_cars, 180, 360, fc='tomato', zorder=4)
        ax.add_patch(lower_circle)
        cars.append(lower_circle)

    # 畫中間的軸
    
    x_line = [0, 0] 
    y_line = [0, 3]
    A_animate = [[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]]
    V_animate = A_animate @ np.vstack((x_line, y_line))
    x_line = V_animate[0, :]
    y_line = V_animate[1, :]
    line, =ax.plot(x_line, y_line, color="silver", linewidth=4, zorder=3)
    cars.append(line)

    for i in range(n):
        A = [[np.cos(theta), np.sin(theta)], [-np.sin(theta), np.cos(theta)]]
        V = A @ np.vstack((x_line, y_line))
        x_line = V[0, :]
        y_line = V[1, :]
        line, =ax.plot(x_line, y_line, color="silver", linewidth=4, zorder=3)
        cars.append(line)

    return cars

# 動畫
ani = FuncAnimation(fig, update, frames=range(360), init_func=init, blit=True, repeat=False, interval=50)

ax.set_xlim(-5, 5)
ax.set_ylim(-6, 4)
ax.axis('off')
plt.title('Rotating Ferris Wheel')
plt.show()
ani.save('images/animation.gif', fps=30) #存成gif