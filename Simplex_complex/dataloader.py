import csv
import math
import os
import glob

from dataclasses import dataclass
from datetime import timedelta, datetime, time


@dataclass
class DataPoint:
    Long: float
    Lat: float
    DateTime: datetime
    Time: time


# Mijn dank aan ChatGPT voor deze functie
def convert_days_to_datetime(days):
    # Convert the number of days to a timedelta object
    delta = timedelta(days=days)
    # Define the base date (12/30/1899)
    base_date = datetime(1899, 12, 30)
    # Add the delta to the base date to get the final DateTime object
    result = base_date + delta
    return result

def getPointsInFile(path):
    points = []
    r = 0
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if (r > 7):
                date = convert_days_to_datetime(float(row[4]))
                points.append(DataPoint(
                    float(row[0]),
                    float(row[1]),
                    date,
                    date.time()))
            r += 1
    return points


def distance(p1, p2):
    x = math.fabs(p1.Long - p2.Long)
    y = math.fabs(p1.Lat - p2.Lat)
    return math.sqrt(x * x + y * y)

def loadPoints(count):
    points = []
    pltPaths = glob.glob(os.getcwd() + '\\**\\*.plt', recursive=True)
    f = 0
    while len(points) < count and f < len(pltPaths):
        filePoints = getPointsInFile(pltPaths[f])
        if len(points) == 0 or distance(points[0], points[0]) < .0001:
            for p in filePoints:
                points.append(p)
        f = f + 1
    return points[0:count]


for p in loadPoints(100):
    print(p)
