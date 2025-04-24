from path import Path, AddNodeToPath, ContainsNode, CostToNode, FindShortestPath
from node import Node, Distance
from graph import Graph, AddNode, AddSegment


def test_path():
    print("\n=== Iniciando pruebas del módulo path ===\n")

    # Crear un nuevo camino
    print("1. Probando la creación de un nuevo camino...")
    path = Path()
    if len(path.nodes) == 0:
        print("OK - El nuevo camino no tiene nodos")
    else:
        print("ERROR - El nuevo camino debería estar vacío")

    if path.cost == 0.0:
        print("OK - El costo inicial es 0")
    else:
        print("ERROR - El costo inicial debería ser 0")

    # Crear nodos de prueba
    print("\n2. Creando nodos de prueba...")
    node1 = Node("A", 0, 0)
    node2 = Node("B", 3, 0)
    node3 = Node("C", 3, 4)
    node4 = Node("D", 0, 4)
    print("OK - Nodos creados: A(0,0), B(3,0), C(3,4), D(0,4)")

    # Probar añadir nodos al camino
    print("\n3. Probando añadir nodos al camino...")
    AddNodeToPath(path, node1)
    if len(path.nodes) == 1:
        print("OK - Se añadió el primer nodo correctamente")
    else:
        print("ERROR - No se pudo añadir el primer nodo")

    AddNodeToPath(path, node2)
    if len(path.nodes) == 2:
        print("OK - Se añadió el segundo nodo correctamente")
    else:
        print("ERROR - No se pudo añadir el segundo nodo")

    expected_cost = Distance(node1, node2)
    if path.cost == expected_cost:
        print(f"OK - El costo del camino es correcto: {path.cost:.2f}")
    else:
        print(f"ERROR - El costo debería ser {expected_cost:.2f} pero es {path.cost:.2f}")

    # Probar si un nodo está en el camino
    print("\n4. Probando si los nodos están en el camino...")
    if ContainsNode(path, node1):
        print("OK - Se encontró el nodo A en el camino")
    else:
        print("ERROR - No se encontró el nodo A")

    if not ContainsNode(path, node3):
        print("OK - El nodo C no está en el camino (correcto)")
    else:
        print("ERROR - Se encontró el nodo C cuando no debería estar")

    # Probar el costo hasta un nodo
    print("\n5. Probando el cálculo de costos hasta los nodos...")
    if CostToNode(path, node1) == 0:
        print("OK - El costo hasta el primer nodo es 0")
    else:
        print("ERROR - El costo hasta el primer nodo debería ser 0")

    if CostToNode(path, node2) == Distance(node1, node2):
        print("OK - El costo hasta el segundo nodo es correcto")
    else:
        print("ERROR - El costo hasta el segundo nodo es incorrecto")

    # Probar el camino más corto
    print("\n6. Probando la búsqueda del camino más corto...")
    graph = Graph()

    # Añadir nodos al grafo
    AddNode(graph, node1)
    AddNode(graph, node2)
    AddNode(graph, node3)
    AddNode(graph, node4)

    # Crear un cuadrado con una diagonal
    AddSegment(graph, "AB", "A", "B")
    AddSegment(graph, "BC", "B", "C")
    AddSegment(graph, "CD", "C", "D")
    AddSegment(graph, "DA", "D", "A")
    AddSegment(graph, "AC", "A", "C")  # Diagonal
    print("OK - Grafo creado con forma de cuadrado y una diagonal")

    # Buscar camino más corto de A a C
    shortest_path = FindShortestPath(graph, "A", "C")
    if shortest_path is not None:
        print("OK - Se encontró un camino de A a C")
        if len(shortest_path.nodes) == 2:
            print("OK - El camino usa la diagonal (el camino más corto)")
        else:
            print("ERROR - El camino no usa la diagonal")
    else:
        print("ERROR - No se encontró un camino de A a C")

    # Probar con nodos que no existen
    print("\n7. Probando con nodos que no existen...")
    no_path = FindShortestPath(graph, "A", "X")
    if no_path is None:
        print("OK - No se encontró camino a un nodo que no existe")
    else:
        print("ERROR - Se encontró un camino a un nodo inexistente")

    print("\n=== Pruebas completadas ===")


if __name__ == '__main__':
    test_path()
