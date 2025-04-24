import matplotlib.pyplot as plt
from node import Distance

class Path:
    def __init__(self):
        self.nodes = []
        self.cost = 0

def add_node_to_path(path, node, segment_cost):
    """
    Adds a node to a path with the specified segment cost.
    
    Args:
        path: The Path object to modify
        node: The node to add to the path
        segment_cost: The cost of the segment connecting this node
    """
    path.nodes.append(node)
    path.cost += segment_cost

def contains_node(path, node):
    """
    Checks if a node is present in a path.
    
    Args:
        path: The Path object to check
        node: The node to look for
        
    Returns:
        True if the node is in the path, False otherwise
    """
    return node in path.nodes

def cost_to_node(path, node):
    """
    Calculates the cost from the origin of the path to a specific node.
    
    Args:
        path: The Path object
        node: The target node
        
    Returns:
        The cost to reach the node, or -1 if the node is not in the path
    """
    if node not in path.nodes:
        return -1
    
    # If it's the first node, cost is 0
    if node == path.nodes[0]:
        return 0
        
    total_cost = 0
    for i in range(len(path.nodes) - 1):
        total_cost += Distance(path.nodes[i], path.nodes[i+1])
        if path.nodes[i+1] == node:
            return total_cost
    
    return total_cost

def plot_path(graph, path):
    """
    Plots a path in the context of a graph.
    
    Args:
        graph: The graph containing the full network
        path: The Path object to plot
    """
    # Plot the full graph in the background
    plt.figure()
    plt.grid(True, color='red')
    
    # Plot all nodes in gray
    for node in graph.nodes:
        plt.plot(node.coordx, node.coordy, 'o', color='gray')
        plt.text(node.coordx, node.coordy, node.name, fontsize=12)
    
    # Plot all segments in blue
    for segment in graph.segments:
        plt.plot([segment.orig.coordx, segment.dest.coordx], 
                [segment.orig.coordy, segment.dest.coordy], '-', color='blue', alpha=0.5)
    
    # Plot the path in purple
    for i in range(len(path.nodes) - 1):
        orig, dest = path.nodes[i], path.nodes[i + 1]
        plt.plot([orig.coordx, dest.coordx], [orig.coordy, dest.coordy], '-', color='purple', linewidth=2)
        # Add edge weight
        mid_x = (orig.coordx + dest.coordx) / 2
        mid_y = (orig.coordy + dest.coordy) / 2
        dist = Distance(orig, dest)
        plt.text(mid_x, mid_y, f"{dist:.2f}", fontsize=8, color='purple')
    
    # Highlight start and end nodes
    if path.nodes:
        plt.plot(path.nodes[0].coordx, path.nodes[0].coordy, 'o', color='green', markersize=10)
        plt.plot(path.nodes[-1].coordx, path.nodes[-1].coordy, 'o', color='red', markersize=10)
    
    # Set title with path cost
    plt.title(f"Path with total cost: {path.cost:.2f}")
    plt.tight_layout()
    plt.show()

# A* Algorithm for finding the shortest path
def find_shortest_path(graph, start_node_name, end_node_name):
    """
    Finds the shortest path between two nodes using the A* algorithm.
    
    Args:
        graph: The graph containing nodes and segments
        start_node_name: Name of the starting node
        end_node_name: Name of the target node
        
    Returns:
        A Path object containing the shortest path if one exists, None otherwise
    """
    # Find the start and end nodes by name
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
        print(f"Error: One or both nodes '{start_node_name}' and '{end_node_name}' not found in the graph.")
        return None
    
    # Check if end node is reachable from start node
    reachable_nodes = graph.get_reachable_nodes(start_node_name)
    if end_node_name not in reachable_nodes:
        print(f"Error: No path exists from '{start_node_name}' to '{end_node_name}'.")
        return None
    
    # Initialize the list of current paths
    # Each path is represented as a Path object
    current_paths = []
    
    # Create initial path with just the start node
    initial_path = Path()
    initial_path.nodes.append(start_node)
    current_paths.append(initial_path)
    
    # Main loop
    max_iterations = 100  # Prevent infinite loops
    
    for iteration in range(max_iterations):
        if not current_paths:
            print(f"Error: No path found from '{start_node_name}' to '{end_node_name}'.")
            return None
            
        # Find the path with minimum total cost (path cost + heuristic)
        min_cost = float('inf')
        min_path_index = -1
        
        for i, path in enumerate(current_paths):
            # Get the last node in the path
            last_node = path.nodes[-1]
            
            # Calculate the heuristic (Euclidean distance to goal)
            heuristic = Distance(last_node, end_node)
            
            # Total cost = actual path cost + heuristic
            total_cost = path.cost + heuristic
            
            if total_cost < min_cost:
                min_cost = total_cost
                min_path_index = i
        
        # Get the path with minimum cost
        current_path = current_paths.pop(min_path_index)
        
        # Get the last node in the current path
        last_node = current_path.nodes[-1]
        
        # If we've reached the goal, return the path
        if last_node.name == end_node_name:
            return current_path
        
        # Expand the current path with all neighbors of the last node
        for neighbor in last_node.neighbors:
            # Skip if this node is already in the path (avoid cycles)
            if neighbor in current_path.nodes:
                continue
                
            # Create a new path by extending the current path
            new_path = Path()
            new_path.nodes = current_path.nodes.copy()
            
            # Calculate segment cost
            segment_cost = Distance(last_node, neighbor)
            
            # Add the neighbor to the new path
            add_node_to_path(new_path, neighbor, segment_cost)
            
            # Add the new path to the list of paths
            current_paths.append(new_path)
    
    print(f"Error: Maximum iterations reached. Could not find path from '{start_node_name}' to '{end_node_name}'.")
    return None
