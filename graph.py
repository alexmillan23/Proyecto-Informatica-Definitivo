import matplotlib.pyplot as plt
from node import Node, Distance
from segment import Segment, CalcCost


class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []
        
    def get_reachable_nodes(self, start_node_name):
        """
        Finds all nodes that are reachable from the given start node.
        
        Args:
            start_node_name: Name of the starting node
            
        Returns:
            A list of names of all reachable nodes from the starting node
        """
        visited = set()
        stack = [start_node_name]

        while stack:
            node_name = stack.pop()
            if node_name not in visited:
                visited.add(node_name)
                for node in self.nodes:
                    if node.name == node_name:
                        stack.extend(neighbor.name for neighbor in node.neighbors if neighbor.name not in visited)
                        break

        return list(visited)


def AddNode(g, n):
    if n in g.nodes:
        return False
    g.nodes.append(n)
    return True


def AddSegment(g, nombre, nameOriginNode, nameDestinationNode):
    origen, destino = None, None

    for node in g.nodes:
        if node.name == nameOriginNode:
            origen = node
        if node.name == nameDestinationNode:
            destino = node

    if not origen or not destino:
        print(f"Error: Uno o ambos nodos no existen ({nameOriginNode}, {nameDestinationNode})")
        return False

    seg = Segment(nombre, origen, destino)
    seg.cost = CalcCost(seg)
    g.segments.append(seg)

    if destino not in origen.neighbors:
        origen.neighbors.append(destino)

    return True


def GetClosest(g, x, y):
    if not g.nodes:
        print("El grafo no tiene nodos.")
        return None

    closest_node = None
    min_distance = float('inf')

    for node in g.nodes:
        dist = Distance(Node("", x, y), node)
        if dist < min_distance:
            min_distance = dist
            closest_node = node

    return closest_node


def Plot(g):
    plt.grid(color='red', linestyle='dashed', linewidth=0.5)
    plt.title('Grafo')
    plt.xlabel('Coordenada x')
    plt.ylabel('Coordenada y')

    for node in g.nodes:
        plt.plot(node.coordx, node.coordy, marker='o', color='r', markersize=6)
        plt.text(node.coordx + 0.1, node.coordy + 0.1, node.name, fontsize=10, color='g', weight='bold')

    for segment in g.segments:
        plt.arrow(segment.orig.coordx, segment.orig.coordy,
                  segment.dest.coordx - segment.orig.coordx,
                  segment.dest.coordy - segment.orig.coordy,
                  head_width=0.05, head_length=0.05, fc='b', ec='b')
        midx = (segment.orig.coordx + segment.dest.coordx) / 2
        midy = (segment.orig.coordy + segment.dest.coordy) / 2
        plt.text(midx, midy, round(segment.cost, 3), fontsize=10, color='black', weight='bold')


def PlotNode(g, nameOrigin):
    origin = None
    for node in g.nodes:
        if node.name == nameOrigin:
            origin = node
            break

    if not origin:
        print(f"Error: Nodo {nameOrigin} no encontrado.")
        return False

    plt.grid(color='red', linestyle='dashed', linewidth=0.5)
    plt.title(f'Nodo {nameOrigin} y sus vecinos')
    plt.xlabel('Coordenada x')
    plt.ylabel('Coordenada y')

    for node in g.nodes:
        color = 'gray'
        if node == origin:
            color = 'blue'
        elif node in origin.neighbors:
            color = 'green'
        plt.plot(node.coordx, node.coordy, marker='o', color=color, markersize=6)
        plt.text(node.coordx + 0.1, node.coordy + 0.1, node.name, fontsize=10, color='g', weight='bold')

    for neighbor in origin.neighbors:
        plt.arrow(origin.coordx, origin.coordy,
                  neighbor.coordx - origin.coordx,
                  neighbor.coordy - origin.coordy,
                  head_width=0.05, head_length=0.05, fc='r', ec='r')
        midx = (origin.coordx + neighbor.coordx) / 2
        midy = (origin.coordy + neighbor.coordy) / 2
        plt.text(midx, midy, round(Distance(origin, neighbor), 3), fontsize=10, color='black', weight='bold')

    plt.show()
    return True


def LoadGraphFromFile(filename):
    try:
        with open(filename, 'r') as fichero:
            g = Graph()
            for linea in fichero:
                trozos = linea.strip().split(' ')
                if trozos[0] == 'Node' and len(trozos) == 4:
                    AddNode(g, Node(trozos[1], float(trozos[2]), float(trozos[3])))
                elif trozos[0] == 'Segment' and len(trozos) == 4:
                    AddSegment(g, trozos[1], trozos[2], trozos[3])
                else:
                    print(f"Línea inválida: {linea.strip()}")
            return g
    except FileNotFoundError:
        print(f"Error: Archivo {filename} no encontrado.")
        return None


def AddNodeGraphically(g, name, x, y):
    new_node = Node(name, x, y)
    if AddNode(g, new_node):
        print(f"Nodo {name} añadido en ({x}, {y}).")
    else:
        print(f"El nodo {name} ya existe.")


def AddSegmentGraphically(g, name, nameOriginNode, nameDestinationNode):
    if AddSegment(g, name, nameOriginNode, nameDestinationNode):
        print(f"Segmento {name} añadido entre {nameOriginNode} y {nameDestinationNode}.")
    else:
        print(f"No se pudo añadir el segmento {name}. Verifica los nodos.")


def DeleteNodeGraphically(g, name):
    found = False
    for node in g.nodes:
        if node.name == name:
            found = True
            g.nodes.remove(node)
            g.segments = [s for s in g.segments if s.orig != node and s.dest != node]
            print(f"Nodo {name} eliminado, junto con sus segmentos.")
    if not found:
        print(f"Nodo {name} no encontrado.")


def SaveGraphToFile(graph, filename):
    with open(filename, 'w') as file:
        for node in graph.nodes:
            file.write(f"Node {node.name} {node.coordx} {node.coordy}\n")
        for segment in graph.segments:
            file.write(f"Segment {segment.name} {segment.orig.name} {segment.dest.name}\n")
        file.write("End\n")
    print(f"Grafo guardado en {filename}")


def FindShortestPath(g, origin, destination):
    """
    Returns a Path describing the shortest path between origin and destination.
    Returns None if there is no path connecting these nodes.
    
    Args:
        g: The graph containing nodes and segments
        origin: Name of the origin node
        destination: Name of the destination node
        
    Returns:
        A Path object representing the shortest path, or None if no path exists
    """
    from path import find_shortest_path
    return find_shortest_path(g, origin, destination)