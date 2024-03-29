import csv
import math
import os
import glob
import shutil

from dataclasses import dataclass
from datetime import timedelta, datetime, time

from pygame import Vector2


@dataclass
class DataPoint:
    Index: int
    Long: float
    Lat: float
    LatLongVector: Vector2
    DateTime: datetime
    Time: time
    TimeDelta: timedelta
    IsFinalPoint: bool


# Mijn dank aan ChatGPT voor deze functie
def convert_days_to_datetime(days):
    # Convert the number of days to a timedelta object
    delta = timedelta(days=days)
    # Define the base date (12/30/1899)
    base_date = datetime(1899, 12, 30)
    # Add the delta to the base date to get the final DateTime object
    result = base_date + delta
    return result


def getLongLatFinalPoint(path):
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|',)
        row = csvfile.readlines()[-1].split(sep=',')
        lat = float(row[0])
        long = float(row[1])
        return Vector2(long, -lat)

def getPointsInFile(path, max_points=-1):
    points = []
    r = 0
    time_offset = timedelta(0),
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if (r > 7):
                date = convert_days_to_datetime(float(row[4]))
                lat = float(row[0])
                long = float(row[1])

                if len(points) == 0:
                    time_offset = datetime.combine(date.min, date.time()) - datetime.min

                points.append(DataPoint(
                    -1,
                    long,
                    lat,
                    Vector2(long, -lat),
                    date,
                    date.time(),
                    datetime.combine(date.min, date.time()) - datetime.min - time_offset,
                    False)),
            r += 1

            if max_points != -1 and len(points) >= max_points:
                return points

    points[len(points) - 1].IsFinalPoint = True
    return points


def distance(p1, p2):
    x = math.fabs(p1.Long - p2.Long)
    y = math.fabs(p1.Lat - p2.Lat)
    return math.sqrt(x * x + y * y)


def loadPoints(count, max_distance_between_datapoints):
    points = []
    pltPaths = glob.glob(os.getcwd() + '\\FilteredData\\**\\*.plt', recursive=True)
    f = 0
    while len(points) < count and f < len(pltPaths):
        filePoints = getPointsInFile(pltPaths[f])
        valid = True

        for i in range(len(filePoints) - 1):
            if distance(filePoints[i], filePoints[i + 1]) > max_distance_between_datapoints:
                valid = False
                break

        if valid:
            for p in filePoints:
                p.Index = len(points)
                points.append(p)

        f = f + 1
    return points[0:count]


def load_points_filtered(lat, long, radius, time_interval_start: timedelta, time_interval_end: timedelta, max_count):
    points = []
    pltPaths = glob.glob(os.getcwd() + '\\**\\*.plt', recursive=True)
    f = 0
    while len(points) < max_count and f < len(pltPaths):
        filePoints = getPointsInFile(pltPaths[f])
        center = Vector2(lat, long)
        p1 = filePoints[0]
        if center.distance_to(p1.LatLongVector) < radius and time_interval_start < p1.TimeDelta < time_interval_end:
            for p in filePoints:
                p.Index = len(points)
                points.append(p)
        f = f + 1
    return points[0:max_count]


def refilter_data(lat, long, radius, time_interval_start: timedelta, time_interval_end: timedelta):
    pltPaths = glob.glob(os.getcwd() + '\\Data\\**\\*.plt', recursive=True)
    center = Vector2(lat, long)
    if os.path.isdir('FilteredData'):
        shutil.rmtree('FilteredData')

    os.mkdir('FilteredData')
    for path in pltPaths:
        p1 = getPointsInFile(path, 1)[0]
        if center.distance_to(p1.LatLongVector) < radius and time_interval_start < p1.TimeDelta < time_interval_end:
            shutil.copy2(path, 'FilteredData')


def refilter_data(lat, long, radius):
    pltPaths = glob.glob(os.getcwd() + '\\Data\\**\\*.plt', recursive=True)
    center = Vector2(long, -lat)
    if os.path.isdir('FilteredData'):
        shutil.rmtree('FilteredData')

    os.mkdir('FilteredData')
    for path in pltPaths:
        # points = getPointsInFile(path)
        # p1=  points[len(points)-1]
        p1 = getPointsInFile(path, 1)[0]
        if center.distance_to(p1.LatLongVector) < radius:
            shutil.copy2(path, 'FilteredData')


def refilter_data(filter_left_top: Vector2, filter_right_bottom: Vector2, filter_end_points):
    pltPaths = glob.glob(os.getcwd() + '\\Data\\**\\*.plt', recursive=True)
    if os.path.isdir('FilteredData'):
        shutil.rmtree('FilteredData')

    os.mkdir('FilteredData')
    for path in pltPaths:
        p: Vector2
        if filter_end_points:
            p = getLongLatFinalPoint(path)
        else:
            p = getPointsInFile(path, 1)[0].LatLongVector

        if (filter_left_top.x <= p.x <= filter_right_bottom.x and
                filter_left_top.y <= p.y <= filter_right_bottom.y):
            shutil.copy2(path, 'FilteredData')
