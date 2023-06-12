import random
from datetime import timedelta

import disjoint_set
import pygame
from pygame import Vector2

import complexGen
import dataloader
import drawUtils
import shared
from drawUtils import to_screen
from graph import Graph, GraphPoint, Connection, draw_graph, setupNX
from shared import Camera

import settings

pygame.init()
running = True
screen = pygame.display.set_mode(settings.window_start_size, vsync=True)
shared.window = screen
clock = pygame.time.Clock()
datapoints: list[dataloader.DataPoint]
datapoints = []

shared.camera = Camera()
shared.camera.screen_size = settings.window_start_size


class TimeSlot:
    start_time: timedelta
    end_time: timedelta
    points: []
    simplex: []
    set: disjoint_set
    group_representative_lookup: {}


slots = []
graph = Graph()
graph.behaviour = 'map'
graph.datapoints = datapoints
current_slot_index = 0

split_mode = False
point_cloud = False
point_cloud_all = False


def find_graph_point(slot: TimeSlot, rep):
    for p in graph.points:
        if p.time_slot == slot and p.representative == rep:
            return p
    raise Exception()


def setup_slots():
    analysis_duration = settings.analysis_time_slot_end_time - settings.analysis_time_slot_start_time
    analysis_duration.total_seconds() / settings.analysis_time_slot_interval.total_seconds()
    cur_time = settings.analysis_time_slot_start_time

    while cur_time + settings.analysis_time_slot_interval + settings.analysis_time_slot_interval_padding < settings.analysis_time_slot_end_time:
        slot = TimeSlot()
        slot.start_time = cur_time - settings.analysis_time_slot_interval_padding
        slot.end_time = cur_time + settings.analysis_time_slot_interval + settings.analysis_time_slot_interval_padding
        slots.append(slot)
        cur_time += settings.analysis_time_slot_interval
        print(str(slot.start_time) + ' - ' + str(slot.end_time))

    print('loading slots points...')
    s: TimeSlot
    for s in slots:
        s.points = []
        p: dataloader.DataPoint
        for p in datapoints:
            if s.start_time < p.TimeDelta < s.end_time:
                s.points.append(p)

    print('generating complexes...')
    for s in slots:
        s.simplex = complexGen.generate_alpha_complex(s.points, settings.alpha_complex_filtration_value)

    print('finding connected components...')
    for s in slots:
        s.set, s.group_representative_lookup = complexGen.find_connected_components(s.simplex)

    print('constructing graph points...')
    graph.points = []
    for s in slots:
        groups = {}
        for index in s.group_representative_lookup:
            groups[s.group_representative_lookup[index]] = 1

        for g in groups:
            gp = GraphPoint()
            gp.representative = g
            gp.position = Vector2(random.randint(-100, 100), random.randint(-100, 100)) / 100
            gp.time_slot = s
            graph.points.append(gp)

    print('finding edges...')
    graph.connections = []
    edges_to_create = {}
    for s1 in range(len(slots) - 1):
        cur_slot: TimeSlot = slots[s1]
        next_slot: TimeSlot = slots[s1 + 1]
        cur_lookup = cur_slot.group_representative_lookup
        next_lookup = next_slot.group_representative_lookup
        for p1 in cur_lookup:
            for p2 in next_lookup:
                if p1 == p2:
                    edges_to_create[(cur_slot, cur_lookup[p1], next_slot, next_lookup[p2])] = 1

    graph.offset = Vector2(500, 500)

    graph.connections = []
    for edge in edges_to_create:
        c = Connection()
        c.A = find_graph_point(edge[0], edge[1])
        c.B = find_graph_point(edge[2], edge[3])
        graph.connections.append(c)

    print('setup nx...')
    setupNX(graph)


def load_datapoints():
    for p in dataloader.loadPoints(10000000, settings.max_distance_between_datapoints):
        datapoints.append(p)
    print(str(len(datapoints)) + ' points loaded')


def setup():
    if settings.refilter_data:
        print('filtering data ...')
        dataloader.refilter_data(39.957, 116.3124, .03, settings.analysis_time_slot_start_time - timedelta(minutes=0),
                                 settings.analysis_time_slot_start_time + settings.analysis_time_slot_interval + timedelta(
                                     minutes=0))
    load_datapoints()
    setup_slots()


def draw_slot_components(slot: TimeSlot):
    for s in slot.simplex:
        slotTime = int(slot.start_time.total_seconds())
        simplex = s[0]
        c = shared.camera
        if len(s[0]) == 1:
            p1 = to_screen(datapoints[simplex[0]].LatLongVector, c)
            color = drawUtils.get_datapoint_index_color(slot.group_representative_lookup[simplex[0]] + len(slot.points))
            pygame.draw.circle(shared.window, color, p1, 3)
        if len(s[0]) == 2:
            simplex = s[0]
            p1 = to_screen(datapoints[simplex[0]].LatLongVector, c)
            p2 = to_screen(datapoints[simplex[1]].LatLongVector, c)
            color = drawUtils.get_datapoint_index_color(slot.group_representative_lookup[simplex[0]] + len(slot.points))
            pygame.draw.line(shared.window, color, p1, p2)
        if len(s[0]) == 3:
            p1 = to_screen(datapoints[simplex[0]].LatLongVector, c)
            p2 = to_screen(datapoints[simplex[1]].LatLongVector, c)
            p3 = to_screen(datapoints[simplex[2]].LatLongVector, c)
            color = drawUtils.get_datapoint_index_color(slot.group_representative_lookup[simplex[0]] + len(slot.points))
            c2 = drawUtils.get_datapoint_index_color(simplex[0])
            color = color.lerp(c2, .0)
            pygame.draw.polygon(shared.window, color, (p1, p2, p3))


def draw_point_cloud(points):
    p: DataPoint
    for p in points:
        pygame.draw.circle(screen, (255, 255, 255), drawUtils.to_screen(p.LatLongVector, shared.camera), 3)


def update():
    global current_slot_index
    global lastPressed
    global window

    update_input()
    graph_offset = Vector2(0, 0)
    if split_mode:
        graph_offset = Vector2(screen.get_width() / 2, 0)

    if point_cloud:
        if point_cloud_all:
            draw_point_cloud(datapoints)
        else:
            draw_point_cloud(slots[current_slot_index].points)
    else:
        draw_slot_components(slots[current_slot_index])

    lastPressed = pygame.key.get_pressed()

    current_slot: TimeSlot = slots[current_slot_index]

    w = screen.get_width()
    h = screen.get_height()

    if split_mode:
        pygame.draw.rect(shared.window, (15, 15, 25),
                         [Vector2(w / 2, 0), Vector2(w / 2, h)],
                         border_radius=6)

    if split_mode:
        shared.camera.screen_size = Vector2(w / 2, h)
    else:
        shared.camera.screen_size = Vector2(w, h)

    if split_mode:
        screen.set_clip([Vector2(w / 2, 0), Vector2(w / 2, h)])

    draw_graph(graph, slots[current_slot_index], graph_offset)

    screen.set_clip([Vector2(0, 0), Vector2(w, h)])

    drawUtils.text_to_screen(shared.window, str(current_slot.start_time) + ' - ' + str(current_slot.end_time), 50, 50,
                             (255, 255, 255), drawUtils.font_clock)


def update_input():
    global current_slot_index, split_mode, point_cloud, point_cloud_all

    dirX = 0
    dirY = 0

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
        shared.camera.zoom *= 1 + .04
    if keys[pygame.K_e]:
        shared.camera.zoom *= 1 - .04

    if keys[pygame.K_1] and not lastPressed[pygame.K_1]:
        current_slot_index -= 1
    if keys[pygame.K_2] and not lastPressed[pygame.K_2]:
        current_slot_index += 1
    if keys[pygame.K_3] and not lastPressed[pygame.K_3]:
        graph.behaviour = 'physics'
    if keys[pygame.K_4] and not lastPressed[pygame.K_4]:
        graph.behaviour = 'map'
    if keys[pygame.K_5] and not lastPressed[pygame.K_5]:
        graph.behaviour = 'networkx'
    if keys[pygame.K_c] and not lastPressed[pygame.K_c]:
        split_mode = not split_mode
    if keys[pygame.K_p] and not lastPressed[pygame.K_p]:
        point_cloud = not point_cloud
    if keys[pygame.K_o] and not lastPressed[pygame.K_o]:
        point_cloud_all = not point_cloud_all

    shared.camera.center += Vector2(dirX, dirY) / shared.camera.zoom * 10
    current_slot_index = current_slot_index % len(slots)


setup()

lastPressed = pygame.key.get_pressed()
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((15, 15, 15))
    update()
    # flip() the display to put your work on screen
    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

pygame.quit()
