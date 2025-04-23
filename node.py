import math

class Node:
    def __init__(self, name, coordx, coordy):
        self.name = name
        self.coordx = coordx
        self.coordy = coordy
        self.neighbors = []

def AddNeighbor(n1, n2):
    if n2 in n1.neighbors:
        return False
    else:
        n1.neighbors.append(n2)
        return True

def Distance(n1, n2):
    return math.sqrt((n1.coordx - n2.coordx) ** 2 + (n1.coordy - n2.coordy) ** 2)