from datetime import datetime as dt, time

import pygame
import random
from disjoint_set import DisjointSet
import math

from gudhi.alpha_complex import AlphaComplex
from pygame import Vector2

import dataloader

pygame.init()

cam_center = (39.994, 116.325)
cam_zoom = 80000

filteration_value = .00001

# Code adjusts to screensize. Adjust as you like.
screen_width = 1400
screen_height = 1000
screen_size = (screen_width, screen_height)
window = pygame.display.set_mode(screen_size, vsync=1)

pygame.display.set_caption("Simplicial Complex")

# Fill the screen with white color
window.fill((255, 255, 255))


def to_screen(p):
    x = (p[0] - cam_center[0]) * cam_zoom + screen_width / 2
    y = (p[1] - cam_center[1]) * cam_zoom + screen_height / 2
    return (x, y)


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
def drawPoint(point, color):
    pygame.draw.circle(window, color, to_screen(point), 4, 0)


def drawLine(point1, point2):
    pygame.draw.line(window, (255, 0, 255), to_screen(point1), to_screen(point2), 1)


def drawTriangle(point1, point2, point3, color):
    pygame.draw.polygon(window, color, [to_screen(point1), to_screen(point2), to_screen(point3)], 0)


def getRepColor(rep):
    return (rep * 25 % 255., rep * 1 % 255, rep * 7 % 255)


def draw(points, simplices, groupReps):
    # 'i' are the tuples
    i = 0
    for s in simplices:
        simplex = s[0]
        r = s[1]
        if (r < filteration_value):
            # If size == 1, only draw point.
            # If size == 2, draw points, and a line.
            # If size == 3, draw points, and a triangle
            rep = groupReps[simplex[0]]
            if len(simplex) == 1:
                c = getRepColor(rep)
                drawPoint(points[simplex[0]], (c[0]/2, c[1]/2, c[2]/2))
            if len(simplex) == 2:
                drawLine(points[simplex[0]], points[simplex[1]])
            if len(simplex) == 3:
                drawTriangle(points[simplex[0]], points[simplex[1]], points[simplex[2]],
                             getRepColor(rep))
            i += 11

running = True
datapoints = dataloader.loadPoints(500000)
drawPoints =[]
for p in datapoints:
    drawPoints.append((p.Long, p.Lat))


# source: https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame
def text_to_screen(screen, text, x, y, size=50,
                   color=(200, 000, 000), font_type='Arial.ttf'):
    try:

        text = str(text)
        font = pygame.font.Font(font_type, size)
        text = font.render(text, True, color)
        screen.blit(text, (x, y))

    except Exception as e:
        print('Font Error, saw it coming')
        raise e



saves = {}
hour = 16
min = 0

timeIncrementPerSave = 5
timeRangeMinutes:float = 15

for hour in range(0, 2):
    for min in range(0, 60, timeIncrementPerSave):

        timeRangeStart = time(hour,  int(max(min - timeRangeMinutes/2,0)), 0)
        h = hour
        m = min + int(timeRangeMinutes/2)
        while (m >= 60):
            m -= 60
            h += 1

        timeRangeEnd = time(h, m, 0)

        print(str(hour) + ":" + str(min))
        simplexPoints = []
        simplexPointsRealId = {}

        for i in range(len(datapoints)):
            p = datapoints[i]
            if timeRangeStart <= p.Time <= timeRangeEnd:
                simplexPoints.append((p.Long, p.Lat))
                simplexPointsRealId[ len(simplexPoints)-1] =i

        ac = AlphaComplex(points=simplexPoints)
        stree = ac.create_simplex_tree()
        simps = []
        for filtered_value in stree.get_filtration():
            if filtered_value[1] <= filteration_value:
                simps.append(filtered_value)

        set = DisjointSet()

        realSimps = []
        for s in range(len(simps)):
            simp = simps[s]
            if len(simp[0]) == 1:
                realSimps.append(([simplexPointsRealId[simp[0][0]]], simp[1]))
            if len(simp[0]) == 2:
                realSimps.append(([simplexPointsRealId[simp[0][0]], simplexPointsRealId[simp[0][1]]], simp[1]))
            if len(simp[0]) == 3:
                realSimps.append(([simplexPointsRealId[simp[0][0]], simplexPointsRealId[simp[0][1]], simplexPointsRealId[simp[0][2]]], simp[1]))

        simps = realSimps

        for simp in simps:
            if len(simp[0]) == 2:
                set.union(simp[0][0], simp[0][1])

        groupReps = {}
        for simp in simps:
            if len(simp[0]) == 1:
                groupReps[simp[0][0]] = set.find(simp[0][0])

        saves[hour * 60 + min] = [simplexPoints, simps, groupReps, set]

getTicksLastFrame = 0

hour = 0
min = 0

class GraphPoint:
    PullFactor: float
    Representative: int
    SaveIndex: int
    Position: Vector2 = Vector2(0, 0)
    Velocity: Vector2 = Vector2(0, 0)

    def __init__(self, p, r, s):
        self.PullFactor = p
        self.Representative = r
        self.SaveIndex = s

class Connection:
    A: GraphPoint
    B: GraphPoint

    def __init__(self, a, b):
        self.A = a
        self.B = b


graphPoints = []
graphConnections = []

showGraph  = False
def getGraphPoint(saveIndex, rep):
    for e in graphPoints:
        if e.SaveIndex == saveIndex and e.Representative == rep:
           return e

    raise Exception()

saveCount = 16
i=0
for i in range(0, saveCount):
    s = saves[i*timeIncrementPerSave]
    groups = {}
    for p in s[2].values():
        groups[p] = p
    for g in groups.keys():
        gp =GraphPoint(i / saveCount - .5, g, i*timeIncrementPerSave)
        gp.Position = Vector2(i, random.randint(-1000, 1000) / float(1000))
        graphPoints.append(gp)



# s

for i in range(saveCount-1):
    sCur= saves[i*timeIncrementPerSave]
    sNext = saves[(i+1)*timeIncrementPerSave]
    connections = {}

    curSet:DisjointSet = sCur[3]
    nextSet:DisjointSet = sNext[3]

    for p1 in curSet:
        for p2 in nextSet:
            if p1[0] == p2[0]:
                connections[(p1[1], p2[1])] = 1

    for con in connections.keys():
        graphConnections.append(Connection(getGraphPoint(i*timeIncrementPerSave, con[0]), getGraphPoint((i+1)*timeIncrementPerSave, con[1])))




targetGraphConnectionSize = 40;


def drawGraph():

    for p in graphPoints:
        for p2 in graphPoints:
            if p != p2:
                dir = (p.Position - p2.Position).normalize()
                p.Position += dir * (1 / (p.Position.distance_to(p2.Position))) * 30.4

    for c in graphConnections:
        if(c.A == c.B):
            raise Exception()
        dir = (c.A.Position - c.B.Position).normalize()
        # c.A.Velocity += dir * c.A.Position.distance_to(c.B.Position) * .001
        # if(c.A.Position.distance_to(c.B.Position) > 60):

        center = (c.A.Position + c.B.Position)/2

        c.A.Position -= dir * 1
        c.B.Position += dir * 1

    for p in graphPoints:
        p.Position +=  (p.PullFactor *5, 0)
        p.Position *= .98
        p.Position += p.Velocity * 1
        p.Velocity *= .5

    offset = Vector2(800, 300)

    scale = 1
    for connection in graphConnections:
        pygame.draw.line(window, (0, 0, 0), offset + connection.A.Position * scale,
                         offset + connection.B.Position * scale, 5)

    for p in graphPoints:
        pygame.draw.circle(window, getRepColor(p.Representative), offset + p.Position * scale, 14)
        save = saves[hour * 60 + math.floor(min)]
        if p.Representative in save[2] and p.SaveIndex == hour * 60 + math.floor(min):
            pygame.draw.circle(window, (25,25,25), offset + p.Position * scale, 14, 4)


lastPressed = pygame.key.get_pressed()
while running:
    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t
    # min += deltaTime * 5

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

    # if keys[pygame.K_1]:
    #     filteration_value *= 1 - .04
    # if keys[pygame.K_2]:
    #     filteration_value *= 1 + .04

    if keys[pygame.K_1] and not lastPressed[pygame.K_1]:
        min -= 5
    if keys[pygame.K_2] and not lastPressed[pygame.K_2]:
        min += 5
    if keys[pygame.K_g] and not lastPressed[pygame.K_g]:
        showGraph = not showGraph
    if min >= 60:
        min -= 60
        hour += 1
        if hour >= 2:
            hour = 0

    if min < 0:
        min += 60
        hour -= 1
        if hour < 0:
            hour = 2 - 1

    lastPressed = pygame.key.get_pressed()
    cam_center = (cam_center[0] + dirX * .0001, cam_center[1] + dirY * .0001)

    window.fill((255, 255, 255))
    # draw(dummy_points, dummy_connections)
    save = saves[hour * 60 + math.floor(min)]
    draw(drawPoints, save[1], save[2])

    if showGraph:
        drawGraph()

    timeText = '';
    if (hour < 10):
        timeText += '0'
    timeText += str(hour) + ':'

    if (min < 10):
        timeText += '0'
    timeText += str(round(min))
    text_to_screen(window, timeText, 20, 30, 50, (155,0,155))

    pygame.display.update()

pygame.quit()
