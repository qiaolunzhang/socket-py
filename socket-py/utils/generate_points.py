 # -*- coding: utf-8 -*-
import math
import random
import struct


def generate_points(x, y, R):
    theta = 2.0 * math.pi * random.random()
    x1 = x + R * math.sin(theta)
    y1 = y + R * math.cos(theta)
    x1 = str(x1)
    y1 = str(y1)
    point = x1 + " " + y1
    with open("./points.txt", 'a+') as f:
        f.write(point)
        f.write('\n')

for i in range(100):
    R = 10 * random.random()
    generate_points(5, 5, 10)
