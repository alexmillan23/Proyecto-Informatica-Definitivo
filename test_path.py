import matplotlib.pyplot as plt
from graph import Graph, AddNode, AddSegment
from node import Node
from path import Path, add_node_to_path, contains_node, cost_to_node, plot_path, find_shortest_path

def test_path_functions():
    """
    Test the basic path functions (add_node_to_path, contains_node, cost_to_node)
    """
    # Create a simple test graph
    g = Graph()
    
    # Add nodes
    node_a = Node("A", 0, 0)
    node_b = Node("B", 3, 4)
    node_c = Node("C", 6, 2)
    
    AddNode(g, node_a)
    AddNode(g, node_b)
    AddNode(g, node_c)
    
    # Add segments
    AddSegment(g, "AB", "A", "B")
    AddSegment(g, "BC", "B", "C")
    
    # Create a path
    path = Path()
    
    # Test add_node_to_path
    add_node_to_path(path, node_a, 0)  # First node has no segment cost
    assert path.nodes[0] == node_a
    assert path.cost == 0
    
    # Add node B with cost
    add_node_to_path(path, node_b, 5)
    assert path.nodes[1] == node_b
    assert path.cost == 5
    
    # Test contains_node
    assert contains_node(path, node_a) == True
    assert contains_node(path, node_b) == True
    assert contains_node(path, node_c) == False
    
    # Test cost_to_node
    assert cost_to_node(path, node_a) == 0
    assert cost_to_node(path, node_b) == 5
    assert cost_to_node(path, node_c) == -1  # Node not in path
    
    print("Basic path functions passed all tests!")
    return path, g

def test_find_shortest_path():
    """
    Test the A* algorithm for finding the shortest path
    """
    # Create a more complex graph for testing shortest path
    g = Graph()
    
    # Add nodes in a grid pattern
    nodes = {}
    for name, coords in [
        ("A", (0, 0)), ("B", (2, 5)), ("C", (5, 2)), 
        ("D", (7, 7)), ("E", (10, 3)), ("F", (12, 8)),
        ("K", (5, 5)), ("L", (8, 3))
    ]:
        node = Node(name, coords[0], coords[1])
        nodes[name] = node
        AddNode(g, node)
    
    # Add segments to create a connected graph
    segments = [
        ("A", "B"), ("A", "C"), ("A", "K"),
        ("B", "D"), ("C", "E"), ("C", "K"),
        ("D", "F"), ("E", "F"), ("K", "L"),
        ("L", "F")
    ]
    
    for i, (src, dst) in enumerate(segments):
        AddSegment(g, f"S{i}", src, dst)
    
    # Test finding the shortest path from A to F
    path = find_shortest_path(g, "A", "F")
    
    if path:
        print(f"Found path from A to F with cost {path.cost:.2f}:")
        path_str = " -> ".join([node.name for node in path.nodes])
        print(path_str)
        
        # Plot the path for visualization
        plot_path(g, path)
    else:
        print("No path found!")
    
    return g, path

if __name__ == "__main__":
    print("Testing basic path functions...")
    test_path, g = test_path_functions()
    
    print("\nTesting shortest path algorithm...")
    g, shortest_path = test_find_shortest_path()
