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
    message = struct.pack('>I', len(x1)) + x1
    message = message + struct.pack('>I', len(y1)) + y1
    return message


def generate_three_points(x, y, R):
    message = ""
    for i in range(3):
        message = message + generate_points(x, y, R)
    return message


def decode_three_points(message):
    points_list = []
    for i in range(3):
        point = []
        x1_len = message[0:4]
        x1_len = struct.unpack('>I', x1_len)[0]
        x1 = message[4:4+x1_len]
        y1_len = message[4+x1_len:8+x1_len]
        y1_len = struct.unpack('>I', y1_len)[0]
        y1 = message[8+x1_len:8+x1_len+y1_len]
        print(x1, y1)
        x1 = float(x1)
        y1 = float(y1)
        point.append(x1)
        point.append(y1)
        points_list.append(point)
        print(x1*x1 + y1*y1)
        message = message[8+x1_len+y1_len:]
    print(points_list)


def decode_points(message):
    x1_len = message[0:4]
    x1_len = struct.unpack('>I', x1_len)[0]
    x1 = message[4:4+x1_len]
    y1_len = message[4+x1_len:8+x1_len]
    y1_len = struct.unpack('>I', y1_len)[0]
    y1 = message[8+x1_len:]
    print(x1, y1)
    x1 = float(x1)
    y1 = float(y1)
    print(x1*x1 + y1*y1)



#message = generate_three_points(0, 0, 5)
#decode_three_points(message)
message = generate_points(5, 5, 5)

