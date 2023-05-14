import csv
import os
import glob


def getPointsInFile(path):
    points = []
    r = 0
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if (r > 7):
                points.append(((float(row[0]), float(row[1]))))
            r += 1
    return points


def loadPoints(count):
    points = []
    pltPaths = glob.glob(os.getcwd() + '\\**\\*.plt', recursive=True)
    f = 0
    while (len(points) < count and f < len(pltPaths)):
        for p in getPointsInFile(pltPaths[f]):
            points.append(p)
        f = f + 1
    return points[0:count]


for p in loadPoints(100):
    print(p)
