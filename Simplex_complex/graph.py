import math
import random

import networkx
import pygame
from networkx import spring_layout, spectral_layout, kamada_kawai_layout
from networkx.drawing.nx_agraph import graphviz_layout
from pygame import Vector2

import drawUtils
import shared


class GraphPoint:
    pull_factor: float = 0
    representative: int
    time_slot: any
    position: Vector2 = Vector2(0, 0)
    velocity: Vector2 = Vector2(0, 0)


class Connection:
    A: GraphPoint
    B: GraphPoint


class Graph:
    datapoints: []
    behaviour: str
    offset: Vector2
    points: list[GraphPoint]
    connections: []
    nx_graph: networkx.Graph
    layout: spring_layout


# source chatgpt
def remove_all_except_largest_component(graph):
    components = networkx.connected_components(graph)
    largest_component = max(components, key=len)
    new_graph = graph.subgraph(largest_component).copy()
    graph.clear()
    graph.add_nodes_from(new_graph)
    graph.add_edges_from(new_graph.edges())


def setupNX(graph):
    graph.nx_graph = networkx.Graph()
    for p in graph.points:
        graph.nx_graph.add_node(p)
    for c in graph.connections:
        graph.nx_graph.add_edge(c.A, c.B)

    remove_all_except_largest_component(graph.nx_graph)
    graph.layout = kamada_kawai_layout(graph.nx_graph)


def draw_graph_edges(graph: Graph, offset):
    for connection in graph.connections:
        pygame.draw.line(shared.window, (155, 155, 155), offset + connection.A.position,
                         offset + connection.B.position, 5)
def draw_graph_points(graph: Graph, current_visible_slot, offset):
    for p in graph.points:
        if p.time_slot == current_visible_slot:
            pygame.draw.circle(shared.window, (255, 255, 255), offset + p.position, 10)

        pygame.draw.circle(shared.window,
                           drawUtils.get_datapoint_index_color(p.representative + len(p.time_slot.points)),
                           offset + p.position, 8)

def update_graph(graph):
    if graph.behaviour == 'physics' or graph.behaviour == 'time_physics':
        for p in graph.points:
            for p2 in graph.points:
                if p != p2:
                    diff = p.position - p2.position
                    if diff.x == 0 or diff.y == 0:
                        diff = Vector2(random.randint(-100, 100), random.randint(-100, 100))
                    dir = diff.normalize()
                    p.position += dir * (1 / (p.position.distance_to(p2.position))) * 130.4

        for c in graph.connections:
            if c.A == c.B:
                raise Exception()
            dir = (c.A.position - c.B.position).normalize()
            # c.A.Velocity += dir * c.A.position.distance_to(c.B.position) * .001
            # if(c.A.position.distance_to(c.B.position) > 60):

            center = (c.A.position + c.B.position) / 2

            c.A.position -= dir * 3
            c.B.position += dir * 3
        for p in graph.points:
            p.position += (p.pull_factor * 5, 0)
            # p.position *= .98
            p.position += p.velocity * 10
            p.velocity *= .5

        avg = Vector2()
        for p in graph.points:
            avg += p.position
        avg *= 1.0 / len(graph.points)
        for p in graph.points:
            p.position = p.position - avg
            p.position *= .9
            p.position += avg

    if graph.behaviour == 'map':
        for p in graph.points:
            p.position = drawUtils.to_screen(graph.datapoints[p.representative].LatLongVector, shared.camera)

    if graph.behaviour == 'networkx':
        i = 0
        for p in graph.points:
            if p in graph.nx_graph:
                p.position = Vector2(graph.layout[p][0],graph.layout[p][1]) * 400
                p.position[0] += 500
                p.position[1] += 600
            else:
                i+=1
                p.position = Vector2(50 + 3*i, 50)