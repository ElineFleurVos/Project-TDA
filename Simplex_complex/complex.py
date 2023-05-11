import pygame
import random
 
pygame.init()

# Code adjusts to screensize. Adjust as you like.
screen_width = 800
screen_height = 600
screen_size = (screen_width, screen_height)
window = pygame.display.set_mode(screen_size)

pygame.display.set_caption("Simplicial Complex")
 
# Fill the screen with white color
window.fill((255, 255, 255))

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
    # Multiplication so that dummy data places correctly on the window.
    x_point = point[0] * screen_width 
    y_point = point[1] * screen_height
    pygame.draw.circle(window, (0, 0, 0), [x_point, y_point], 5, 0)  
    
def drawLine(point1, point2):
    start_pos = (point1[0] * screen_width, point1[1] * screen_height )
    end_pos = (point2[0] * screen_width, point2[1] * screen_height )
    pygame.draw.line(window, (255, 0, 255), start_pos, end_pos, 5)
    
def drawTriangle(point1, point2, point3):
    p1 = (point1[0] * screen_width, point1[1] * screen_height)
    p2 = (point2[0] * screen_width, point2[1] * screen_height)
    p3 = (point3[0] * screen_width, point3[1] * screen_height)
    pygame.draw.polygon(window, (25, 25, 255), [p1, p2, p3], 5)

def draw(points, simplices):
    # 'i' are the tuples
    for i in simplices:
        # If size == 1, only draw point.
        # If size == 2, draw points, and a line.
        # If size == 3, draw points, and a triangle
        if isinstance(i, int):
            drawPoint(points[i])
        if isinstance(i, tuple):
            for j in i:
                drawPoint(points[j])
            if len(i) == 2:
                drawLine(points[i[0]], points[i[1]])
            else:
                drawTriangle(points[i[0]], points[i[1]], points[i[2]])
            
    # Draws the surface objects to the screen.    
    pygame.display.update()

# Call draw to test program
draw(dummy_points, dummy_connections)
 
