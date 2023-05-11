import pygame
import numpy as np
import random
from pygame.locals import *
 
pygame.init()

screen_width = 800
screen_height = 600
screen_size = (screen_width, screen_height)
window = pygame.display.set_mode(screen_size)

pygame.display.set_caption("Simplices Complex")
 
# Fill the screen with white color
window.fill((255, 255, 255))

# x, y range from 0-1
# note that (0, 0) is in the top left in PyGame
# Transformation/Mapping of actual data might be necessary
dummy_points = []
for _ in range(20):
    dummy_points.append((random.random(), random.random()))
dummy_points = dummy_points 

dummy_connections = [(1), (2, 4), (7, 8, 9), (3), (5)]

def drawPoint(x, y):
    x_point = x * screen_width 
    y_point = y * screen_height
    pygame.draw.circle(window, (0, 0, 0), [x_point, y_point], 5, 0)  

def getCoordinateTuple(x, y):
    return (x * screen_width, y * screen_height)

def draw(points, simplices):
    x = []
    y = []
    for i in points:
        x.append(i[0])
        y.append(i[1])
    
    # 'i' are the tuples
    for i in simplices:
        if isinstance(i, int):
            drawPoint(x[i], y[i])
        if isinstance(i, tuple):
            for j in i:
                drawPoint(x[j], y[j])
            if len(i) == 2:
                start_pos = getCoordinateTuple(x[i[0]], y[i[0]])
                end_pos = getCoordinateTuple(x[i[1]], y[i[1]])
                pygame.draw.line(window, (255, 0, 255), start_pos, end_pos, 5)
            else:
                p1 = getCoordinateTuple(x[i[0]], y[i[0]])
                p2 = getCoordinateTuple(x[i[1]], y[i[1]])
                p3 = getCoordinateTuple(x[i[2]], y[i[2]])
                pygame.draw.polygon(window, (25, 25, 255), [p1, p2, p3], 5)
                pass
            
    # Draws the surface objects to the screen.    
    pygame.display.update()

draw(dummy_points, dummy_connections)
 
