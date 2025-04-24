from node import *
from segment import *
import matplotlib.pyplot as plt


class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []


def GetReachableNodes(graph, start_node_name):
    visited = set()
    stack = [start_node_name]

    while stack:
        current = stack.pop()
        if current in visited:
            continue
        visited.add(current)
        current_node = None
        for node in graph.nodes:
            if node.name == current:
                current_node = node
                break
        if not current_node:
            continue
        for neighbor in current_node.neighbors:
            if neighbor.name not in visited:
                stack.append(neighbor.name)

    return list(visited)


def AddNode(graph, node):
    # first check if node exists already
    for n in graph.nodes:
        if n.name == node.name:
            print("Error: Ya existe un nodo con el nombre", node.name)
            return False

    graph.nodes.append(node)
    return True


def AddSegment(graph, name_or_segment, origin_name=None, destination_name=None):
    if origin_name is not None and destination_name is not None:
        # This is the old format call with separate parameters
        segment_name = name_or_segment

        # Find the origin and destination nodes
        orig_node = None
        dest_node = None
        for node in graph.nodes:
            if node.name == origin_name:
                orig_node = node
            if node.name == destination_name:
                dest_node = node

        # If we couldn't find both nodes, return false
        if not orig_node or not dest_node:
            print("Error: No se encontró uno o ambos nodos para el segmento")
            return False

        segment = Segment(segment_name, orig_node, dest_node)
    else:
        segment = name_or_segment

        orig_node = None
        dest_node = None
        for node in graph.nodes:
            if node.name == segment.orig.name:
                orig_node = node
            if node.name == segment.dest.name:
                dest_node = node

        if not orig_node or not dest_node:
            print("Error: No se encontró uno o ambos nodos para el segmento")
            return False

    if dest_node not in orig_node.neighbors:
        AddNeighbor(orig_node, dest_node)
    if orig_node not in dest_node.neighbors:
        AddNeighbor(dest_node, orig_node)
    for s in graph.segments:
        if s.name == segment.name:
            return True

    segment.orig = orig_node
    segment.dest = dest_node

    graph.segments.append(segment)
    return True


def GetClosest(graph, coordx, coordy):
    if not graph.nodes:
        return None

    closest = graph.nodes[0]
    min_distance = float('inf')

    for node in graph.nodes:
        dx = node.coordx - coordx
        dy = node.coordy - coordy
        distance = (dx * dx + dy * dy) ** 0.5

        if distance < min_distance:
            closest = node
            min_distance = distance

    return closest


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
                  head_width=0.05, head_length=0.05, fc='c', ec='c')

        midx = (segment.orig.coordx + segment.dest.coordx) / 2
        midy = (segment.orig.coordy + segment.dest.coordy) / 2
        plt.text(midx, midy, round(segment.cost, 3), fontsize=10, color='black', weight='bold')

    plt.show()


def PlotNode(g, nameOrigin):
    node = None
    for n in g.nodes:
        if n.name == nameOrigin:
            node = n
            break
    if not node:
        print("Error: No se encontró el nodo", nameOrigin)
        return False

    plt.figure()
    plt.grid(color='red', linestyle='dotted', linewidth=0.5, alpha=0.5)
    plt.title('Vecinos de ' + nameOrigin)
    plt.xlabel('Coordenada x')
    plt.ylabel('Coordenada y')

    x_coords = [n.coordx for n in g.nodes]
    y_coords = [n.coordy for n in g.nodes]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    padding = max((x_max - x_min), (y_max - y_min)) * 0.1
    plt.xlim(x_min - padding, x_max + padding)
    plt.ylim(y_min - padding, y_max + padding)

    for segment in g.segments:
        if segment.orig.name == nameOrigin or segment.dest.name == nameOrigin:
            continue
        plt.plot([segment.orig.coordx, segment.dest.coordx],
                 [segment.orig.coordy, segment.dest.coordy], '-', color='gray', alpha=0.5)

    for n in g.nodes:
        if n.name == nameOrigin or n in node.neighbors:
            continue
        plt.plot(n.coordx, n.coordy, 'o', color='gray', markersize=6)
        plt.text(n.coordx, n.coordy + 0.3, n.name, fontsize=10,
                 ha='center', va='center', color='black')

    for neighbor in node.neighbors:
        plt.plot(neighbor.coordx, neighbor.coordy, 'o', color='blue', markersize=8)
        plt.text(neighbor.coordx, neighbor.coordy + 0.3, neighbor.name, fontsize=10,
                 ha='center', va='center', color='black', weight='bold')

        plt.arrow(node.coordx, node.coordy,
                  neighbor.coordx - node.coordx,
                  neighbor.coordy - node.coordy,
                  head_width=0.35, head_length=0.5, fc='green', ec='green',
                  linewidth=1.2, length_includes_head=True, zorder=5)

        mid_x = (node.coordx + neighbor.coordx) / 2
        mid_y = (node.coordy + neighbor.coordy) / 2
        cost = Distance(node, neighbor)
        plt.text(mid_x, mid_y, f"{cost:.2f}", color='black', fontsize=9,
                 ha='center', va='center', weight='bold')

    plt.plot(node.coordx, node.coordy, 'o', color='red', markersize=10)
    plt.text(node.coordx, node.coordy + 0.3, node.name, fontsize=12,
             ha='center', va='center', color='black', weight='bold')
    return True


def SaveGraphToFile(graph, filename):
    try:
        with open(filename, 'w') as file:
            for node in graph.nodes:
                file.write(f"Node {node.name} {node.coordx} {node.coordy}\n")
            for segment in graph.segments:
                file.write(f"Segment {segment.name} {segment.orig.name} {segment.dest.name}\n")
            file.write("End\n")
        print(f"Graph saved to {filename}")
        return True
    except Exception as e:
        print("Error saving graph:", e)
        return False


def LoadGraphFromFile(filename):
    try:
        with open(filename, 'r') as file:
            g = Graph()
            for line in file:
                # split the line into parts
                parts = line.strip().split(' ')

                if parts[0] == 'Node' and len(parts) == 4:
                    name = parts[1]
                    x = float(parts[2])
                    y = float(parts[3])
                    AddNode(g, Node(name, x, y))

                elif parts[0] == 'Segment' and len(parts) == 4:
                    name = parts[1]
                    origin = parts[2]
                    destination = parts[3]

                    orig_node = None
                    dest_node = None
                    for node in g.nodes:
                        if node.name == origin:
                            orig_node = node
                        if node.name == destination:
                            dest_node = node

                    if orig_node and dest_node:
                        segment = Segment(name, orig_node, dest_node)
                        g.segments.append(segment)

                        AddNeighbor(orig_node, dest_node)
                        AddNeighbor(dest_node, orig_node)

            return g

    except Exception as e:
        print("Error loading graph:", e)
        return None


def FindShortestPath(g, origin, destination):
    from path import FindShortestPath
    return FindShortestPath(g, origin, destination)