import pygame
import random
import math

from gudhi.alpha_complex import AlphaComplex

import dataloader
pygame.init()

cam_center = (39.994, 116.325)
cam_zoom = 80000

filteration_value = .0001


# Code adjusts to screensize. Adjust as you like.
screen_width = 1400
screen_height = 1000
screen_size = (screen_width, screen_height)
window = pygame.display.set_mode(screen_size)

pygame.display.set_caption("Simplicial Complex")
 
# Fill the screen with white color
window.fill((255, 255, 255))


def to_screen(p):
    x = (p[0]-cam_center[0])*cam_zoom + screen_width/2
    y = (p[1]-cam_center[1])*cam_zoom + screen_height/2
    return (x,y)
# ----------------
# Dummy Data
# Note 1: The dummy data has x, y range from 0-1. Actual data might
# have a different domain/range which impact the view, thus
# transformation/mapping of actual data might be necessary
# Note 2: In PyGame (0, 0) is in the top left 
dummy_points = []
for _ in range(20):
    dummy_points.append((random.random(), random.random()))
dummy_points = dummy_points 

dummy_connections = [(1), (2, 4), (7, 8, 9), (3), (5)]
# ----------------

# Helper function to draw all points
def drawPoint(point):
    pygame.draw.circle(window, (0, 0, 0), to_screen(point), 3, 0)
    
def drawLine(point1, point2):
    pygame.draw.line(window, (255, 0, 255), to_screen(point1), to_screen(point2), 1)


def drawTriangle(point1, point2, point3, color):
    pygame.draw.polygon(window, color, [to_screen(point1),to_screen( point2),to_screen( point3)], 0)


def draw(points, simplices):
    # 'i' are the tuples
    i = 0
    for s in simplices:
        simplex = s[0]
        r = s[1]
        if(r < filteration_value):
            # If size == 1, only draw point.
            # If size == 2, draw points, and a line.
            # If size == 3, draw points, and a triangle
            if len(simplex) == 1:
                drawPoint(points[simplex[0]])
            if len(simplex) == 2:
                drawLine(points[simplex[0]], points[simplex[1]])
            if len(simplex) == 3:
                drawTriangle(points[simplex[0]], points[simplex[1]], points[simplex[2]], (i*25 % 255., i*3 % 255,i*7 %255))
            i+=1
    # Draws the surface objects to the screen.
    pygame.display.update()

running = True
points = dataloader.loadPoints(3000)
ac = AlphaComplex(points=points, )
stree = ac.create_simplex_tree()
fmt = '%s -> %.2f'
simps = []
for filtered_value in stree.get_filtration():
    simps.append(filtered_value)

while(running):

    dirX = 0
    dirY = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        dirX -= 1
    if keys[pygame.K_d]:
        dirX += 1
    if keys[pygame.K_w]:
        dirY -= 1
    if keys[pygame.K_s]:
        dirY += 1
    if keys[pygame.K_q]:
        cam_zoom *= 1 + .01
    if keys[pygame.K_e]:
        cam_zoom *= 1 - .01
    if keys[pygame.K_1]:
        filteration_value *= 1 - .04
    if keys[pygame.K_2]:
        filteration_value *= 1 + .04

    cam_center = (cam_center[0] + dirX * .0001, cam_center[1] + dirY* .0001)

    window.fill((255, 255, 255))
    #draw(dummy_points, dummy_connections)
    draw(points, simps)
pygame.quit()
