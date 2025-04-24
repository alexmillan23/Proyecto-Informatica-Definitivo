import matplotlib.pyplot as plt
from node import Distance
from graph import GetReachableNodes


class Path:
    def __init__(self):
        self.nodes = []
        self.cost = 0.0


def AddNodeToPath(path, node):
    if not path.nodes:
        path.nodes.append(node)  # Agrega el primer nodo
    else:
        last_node = path.nodes[-1]
        path.nodes.append(node)
        path.cost += Distance(last_node, node)
    return path


def ContainsNode(path, node):
    return node in path.nodes


def CostToNode(path, node):
    if node not in path.nodes:
        return -1

    if node == path.nodes[0]:
        return 0

    total_cost = 0
    for i in range(len(path.nodes) - 1):
        total_cost += Distance(path.nodes[i], path.nodes[i + 1])
        if path.nodes[i + 1] == node:
            return total_cost

    return total_cost


def PlotPath(graph, path):
    if not path or not path.nodes:
        return
    plt.figure()
    plt.grid(True, color='red')

    for node in graph.nodes:
        plt.plot(node.coordx, node.coordy, 'o', color='gray')
        plt.text(node.coordx, node.coordy, node.name, fontsize=12)

    for segment in graph.segments:
        plt.plot([segment.orig.coordx, segment.dest.coordx],
                 [segment.orig.coordy, segment.dest.coordy], '-', color='blue', alpha=0.5)

    for i in range(len(path.nodes) - 1):
        orig, dest = path.nodes[i], path.nodes[i + 1]
        plt.plot([orig.coordx, dest.coordx], [orig.coordy, dest.coordy], '-', color='purple', linewidth=2)
        # Add edge weight
        mid_x = (orig.coordx + dest.coordx) / 2
        mid_y = (orig.coordy + dest.coordy) / 2
        dist = Distance(orig, dest)
        plt.text(mid_x, mid_y, f"{dist:.2f}", fontsize=8, color='purple')

    if path.nodes:
        plt.plot(path.nodes[0].coordx, path.nodes[0].coordy, 'o', color='green', markersize=10)
        plt.plot(path.nodes[-1].coordx, path.nodes[-1].coordy, 'o', color='red', markersize=10)

    plt.title(f"Path with total cost: {path.cost:.2f}")
    plt.tight_layout()
    plt.show()


def FindShortestPath(graph, start_node_name, end_node_name):
    start_node = None
    end_node = None

    for node in graph.nodes:
        if node.name == start_node_name:
            start_node = node
        if node.name == end_node_name:
            end_node = node
        if start_node and end_node:
            break

    if not start_node or not end_node:
        print(f"Error: Alguno o ambos nodos '{start_node_name}' y '{end_node_name}' no encontrados en el grafo.")
        return None

    reachable_nodes = GetReachableNodes(graph, start_node_name)
    if end_node_name not in reachable_nodes:
        print(f"Error: No path exists from '{start_node_name}' to '{end_node_name}'.")
        return None

    open_set = []
    closed_set = set()

    initial_path = Path()
    initial_path.nodes.append(start_node)
    initial_path.cost = 0.0
    open_set.append((0 + Distance(start_node, end_node), initial_path))

    max_iterations = 1000
    iteration = 0

    while open_set and iteration < max_iterations:
        iteration += 1
        open_set.sort(key=lambda x: x[0])
        _, current_path = open_set.pop(0)
        last_node = current_path.nodes[-1]

        if last_node.name == end_node_name:
            return current_path
        closed_set.add(last_node.name)

        for neighbor in last_node.neighbors:
            if neighbor.name in closed_set or ContainsNode(current_path, neighbor):
                continue

            new_path = Path()
            new_path.nodes = current_path.nodes.copy()
            new_path.cost = current_path.cost + Distance(last_node, neighbor)
            AddNodeToPath(new_path, neighbor)

            g_score = new_path.cost
            h_score = Distance(neighbor, end_node)
            f_score = g_score + h_score

            found_better = False
            for i, (existing_f_score, path) in enumerate(open_set):
                if path.nodes[-1] == neighbor and f_score < existing_f_score:
                    open_set[i] = (f_score, new_path)
                    found_better = True
                    break

            if not found_better:
                open_set.append((f_score, new_path))

    print(
        f"Error: Máximo de iteraciones alcanzado o no se encontró camino desde '{start_node_name}' hasta '{end_node_name}'.")
    return None
