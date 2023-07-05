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
from graph import Graph, GraphPoint, Connection, draw_graph_points, draw_graph_edges, update_graph, setupNX
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

right_view_name = 'Graph'


class Scene:
    draw_point_cloud_timeslot: bool = False
    draw_alpha_complex_connected: bool = False
    draw_alpha_complex: bool = False
    draw_point_cloud_all: bool = True
    draw_filter_rect: bool = True
    draw_graph_points: bool = False
    draw_graph_points_weighted: bool = False
    draw_graph_edges: bool = False
    graph_behaviour: str = 'map'
    view_name_show_timeslot: bool = False
    view_name: str = 'Point cloud (all filtered points)'
    right_view_name: str = ''

    split_mode = False

    def reset(self):
        self.draw_alpha_complex_connected = False
        self.draw_point_cloud_timeslot = False
        self.draw_point_cloud_all = False
        self.draw_alpha_complex = False
        self.draw_filter_rect = True
        self.draw_graph_points = False
        self.draw_graph_points_weighted = False
        self.draw_graph_edges = False
        self.view_name_show_timeslot = False
        self.graph_behaviour = 'map'
        self.split_mode = False
        self.right_view_name = ''


scene: Scene = Scene()


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


def find_graph_point(slot: TimeSlot, rep):
    for p in graph.points:
        if p.time_slot == slot and p.representative == rep:
            return p
    raise Exception()


def setup_slots():
    # analysis_duration = settings.analysis_time_slot_end_time - settings.analysis_time_slot_start_time
    # analysis_duration.total_seconds() / settings.analysis_time_slot_interval.total_seconds()
    cur_time = settings.analysis_time_slot_interval_padding
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

            # if settings.filter_end_points and p.IsFinalPoint and p.TimeDelta < s.start_time:
            #      s.points.append(p)

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
            if s.group_representative_lookup[index] in groups:
                groups[s.group_representative_lookup[index]] = groups[s.group_representative_lookup[index]] + 1
            else:
                groups[s.group_representative_lookup[index]] = 1

        for g in groups:
            gp = GraphPoint()
            gp.representative = g
            gp.representing_points_count = groups[g]
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
    for p in dataloader.loadPoints(100000000, settings.max_distance_between_datapoints):
        datapoints.append(p)
    print(str(len(datapoints)) + ' points loaded')


def setup():
    if settings.refilter_data:
        print('filtering data ...')
        dataloader.refilter_data(settings.filter_left_top, settings.filter_right_bottom, settings.filter_end_points)
    load_datapoints()
    setup_slots()


def draw_slot_components(slot: TimeSlot):
    for s in slot.simplex:
        slotTime = int(slot.start_time.total_seconds())
        simplex = s[0]
        c = shared.camera
        if len(s[0]) == 1:
            p1 = to_screen(datapoints[simplex[0]].LatLongVector, c)
            color = drawUtils.get_datapoint_index_color(simplex[0])
            pygame.draw.circle(shared.window, color, p1, 3)
        if len(s[0]) == 2:
            simplex = s[0]
            p1 = to_screen(datapoints[simplex[0]].LatLongVector, c)
            p2 = to_screen(datapoints[simplex[1]].LatLongVector, c)
            color = drawUtils.get_datapoint_index_color(simplex[0])
            pygame.draw.line(shared.window, color, p1, p2)
        if len(s[0]) == 3:
            p1 = to_screen(datapoints[simplex[0]].LatLongVector, c)
            p2 = to_screen(datapoints[simplex[1]].LatLongVector, c)
            p3 = to_screen(datapoints[simplex[2]].LatLongVector, c)
            color = drawUtils.get_datapoint_index_color(simplex[0])
            c2 = drawUtils.get_datapoint_index_color(simplex[0])
            color = color.lerp(c2, .0)
            pygame.draw.polygon(shared.window, color, (p1, p2, p3))


def draw_slot_components_connected(slot: TimeSlot):
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


def scale_image(image, zoom):
    width = int(image.get_width() * zoom)
    height = int(image.get_height() * zoom)
    scaled_image = pygame.transform.scale(image, (width, height))
    return scaled_image


lt = drawUtils.to_screen(Vector2(116.22867375128897, -39.996050506192795), shared.camera)
rb = drawUtils.to_screen(Vector2(116.40451027675331, 39.90964512539726), shared.camera)
# ori = pygame.image.load("map.png").convert_alpha()
# map = scale_image(ori, ((rb.x - lt.x) / float(ori.get_width())))


def update():
    global current_slot_index
    global lastPressed
    global window
    global scene

    update_input()

    graph.behaviour = scene.graph_behaviour
    update_graph(graph)

    if scene.draw_filter_rect:
        campusLTscreen = drawUtils.to_screen(settings.filter_left_top, shared.camera)
        pygame.draw.rect(shared.window, pygame.Color(10, 10, 160, 1),
                         pygame.Rect(campusLTscreen,
                                     ((settings.filter_right_bottom - settings.filter_left_top) * shared.camera.zoom)))

    graph_offset = Vector2(0, 0)
    if scene.split_mode:
        graph_offset = Vector2(screen.get_width() / 2, 0)

    if scene.draw_point_cloud_all:
        draw_point_cloud(datapoints)

    if scene.draw_point_cloud_timeslot:
        draw_point_cloud(slots[current_slot_index].points)

    if scene.draw_alpha_complex:
        draw_slot_components(slots[current_slot_index])

    if scene.draw_alpha_complex_connected:
        draw_slot_components_connected(slots[current_slot_index])

    lastPressed = pygame.key.get_pressed()

    current_slot: TimeSlot = slots[current_slot_index]

    w = screen.get_width()
    h = screen.get_height()

    if scene.split_mode:
        pygame.draw.rect(shared.window, (15, 15, 25),
                         [Vector2(w / 2, 0), Vector2(w / 2, h)],
                         border_radius=6)

    if scene.split_mode:
        shared.camera.screen_size = Vector2(w / 2, h)
    else:
        shared.camera.screen_size = Vector2(w, h)

    if scene.split_mode:
        screen.set_clip([Vector2(w / 2, 0), Vector2(w / 2, h)])

    if scene.draw_graph_edges:
        draw_graph_edges(graph, graph_offset)

    if scene.draw_graph_points:
        draw_graph_points(graph, slots[current_slot_index], graph_offset, False)

    if scene.draw_graph_points_weighted:
        draw_graph_points(graph, slots[current_slot_index], graph_offset, True)


    screen.set_clip([Vector2(0, 0), Vector2(w, h)])

    title = scene.view_name
    if scene.view_name_show_timeslot:
        title += ' [' + str(current_slot.start_time)[:-3] + ' - ' + str(current_slot.end_time)[:-3] + ']'
        line_start = Vector2(50, h - 50)
        line_end = Vector2(50 + 400, h - 50)

        pygame.draw.line(shared.window, (255,255,255), line_start, line_end, width=8)
        pygame.draw.circle(shared.window, (255,255,255), line_start.lerp(line_end, (float(current_slot_index) / (len(slots)-1))), 16)
    drawUtils.text_to_screen(shared.window, title, 50, 50,
                             (255, 255, 255), drawUtils.font_clock)

    drawUtils.text_to_screen(shared.window, scene.right_view_name, w/2 + 50, 50,
                             (255, 255, 255), drawUtils.font_clock)

def update_input():
    global current_slot_index, split_mode, scene

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

    if keys[pygame.K_o] and not lastPressed[pygame.K_o]:
        current_slot_index -= 1
    if keys[pygame.K_p] and not lastPressed[pygame.K_p]:
        current_slot_index += 1

    # if keys[pygame.K_1] and not lastPressed[pygame.K_1]:
    #     current_slot_index -= 1
    # if keys[pygame.K_2] and not lastPressed[pygame.K_2]:
    #     current_slot_index += 1
    # if keys[pygame.K_3] and not lastPressed[pygame.K_3]:
    #     graph.behaviour = 'physics'
    # if keys[pygame.K_4] and not lastPressed[pygame.K_4]:
    #     graph.behaviour = 'map'
    # if keys[pygame.K_5] and not lastPressed[pygame.K_5]:
    #     graph.behaviour = 'networkx'
    # if keys[pygame.K_c] and not lastPressed[pygame.K_c]:
    #     split_mode = not split_mode
    # if keys[pygame.K_p] and not lastPressed[pygame.K_p]:
    #     point_cloud = not point_cloud
    # if keys[pygame.K_o] and not lastPressed[pygame.K_o]:
    #     point_cloud_all = not point_cloud_all

    # 1 -> point clouds all
    # 2 -> point clouds by time slot
    # 3 -> alpha simplex per time slot
    # 4 -> alpha simplex connected components
    # 5 -> graph points overalyed on the map
    # 6 -> draw edges
    # 7 -> split view (not really clear the graph)
    # 8 -> kumaii graph positions
    # 9 -> highlight current time slot.

    if keys[pygame.K_1] and not lastPressed[pygame.K_1]:
        scene.reset()
        scene.view_name = 'Point cloud (all filtered points)'
        scene.draw_point_cloud_all = True
    if keys[pygame.K_2] and not lastPressed[pygame.K_2]:
        scene.reset()
        scene.view_name = 'Point cloud'
        scene.view_name_show_timeslot = True
        scene.draw_point_cloud_timeslot = True
    if keys[pygame.K_3] and not lastPressed[pygame.K_3]:
        scene.reset()
        scene.view_name = 'Alpha complex'
        scene.view_name_show_timeslot = True
        scene.draw_alpha_complex = True
    if keys[pygame.K_4] and not lastPressed[pygame.K_4]:
        scene.reset()
        scene.view_name = 'Alpha complex connected components'
        scene.view_name_show_timeslot = True
        scene.draw_alpha_complex_connected = True
    if keys[pygame.K_5] and not lastPressed[pygame.K_5]:
        scene.reset()
        scene.view_name = 'Graph nodes'
        scene.draw_alpha_complex_connected = True
        scene.view_name_show_timeslot = True
        scene.draw_graph_points = True
    if keys[pygame.K_6] and not lastPressed[pygame.K_6]:
        scene.reset()
        scene.view_name = 'Graph nodes and edges'
        scene.draw_alpha_complex_connected = True
        scene.view_name_show_timeslot = True
        scene.draw_graph_points = True
        scene.draw_graph_edges = True
    if keys[pygame.K_7] and not lastPressed[pygame.K_7]:
        scene.reset()
        scene.view_name = 'Connected components'
        scene.right_view_name = 'Graph'
        scene.draw_alpha_complex_connected = True
        scene.view_name_show_timeslot = True
        scene.draw_graph_points = True
        scene.draw_graph_edges = True
        scene.split_mode = True
    if keys[pygame.K_8] and not lastPressed[pygame.K_8]:
        scene.reset()
        scene.view_name =  'Connected components'
        scene.right_view_name = 'Graph (networkx \'Kamada\' layout)'
        scene.view_name_show_timeslot = True
        scene.draw_graph_points = True
        scene.draw_graph_edges = True
        scene.split_mode = True
        scene.draw_alpha_complex_connected = True
        scene.graph_behaviour = 'networkx'
    if keys[pygame.K_9] and not lastPressed[pygame.K_9]:
        scene.reset()
        scene.view_name = 'Connected components'
        scene.right_view_name = 'Graph (weighted)'
        scene.view_name_show_timeslot = True
        scene.draw_graph_points_weighted = True
        scene.draw_graph_edges = True
        scene.split_mode = True
        scene.draw_alpha_complex_connected = True
        scene.graph_behaviour = 'networkx'

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
