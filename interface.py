import tkinter as tk
from tkinter import filedialog, messagebox
from graph import *
import matplotlib.pyplot as plt
from test_graph import CreateGraph_1
from path import FindShortestPath, PlotPath

graph = None


def ShowGraph():
    global graph
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return
    plt.close()
    Plot(graph)
    plt.show()


def SelectNode(graph):
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return

    def display_neighbors():
        node_name = entry.get()
        if PlotNode(graph, node_name):
            plt.show()
        else:
            messagebox.showerror("Error", f"Nodo '{node_name}' no encontrado.")

    window = tk.Toplevel()
    window.title("Mostrar Vecinos")
    tk.Label(window, text="Introduce el nombre del nodo:").pack()
    entry = tk.Entry(window)
    entry.pack()
    tk.Button(window, text="Mostrar", command=display_neighbors).pack()


def ShowReachableNodes(graph):
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return

    def display_reachable():
        start_node_name = entry.get()

        start_node = None
        for node in graph.nodes:
            if node.name == start_node_name:
                start_node = node
                break

        if not start_node:
            messagebox.showerror("Error", f"Nodo '{start_node_name}' no encontrado.")
            return

        reachable_nodes = GetReachableNodes(graph, start_node_name)
        if not reachable_nodes:
            messagebox.showinfo("Información", f"No hay nodos alcanzables desde '{start_node_name}'.")
            return

        plt.figure()
        plt.grid(True, color='red', alpha=0.5, linestyle='dotted')
        plt.title(f"Nodos alcanzables desde {start_node_name}")

        node_dict = {node.name: node for node in graph.nodes}

        x_coords = [node.coordx for node in graph.nodes]
        y_coords = [node.coordy for node in graph.nodes]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        padding = max((x_max - x_min), (y_max - y_min)) * 0.1
        plt.xlim(x_min - padding, x_max + padding)
        plt.ylim(y_min - padding, y_max + padding)

        for segment in graph.segments:
            if segment.orig.name not in reachable_nodes or segment.dest.name not in reachable_nodes:
                plt.plot([segment.orig.coordx, segment.dest.coordx],
                         [segment.orig.coordy, segment.dest.coordy], '-', color='gray', alpha=0.6)
                mid_x = (segment.orig.coordx + segment.dest.coordx) / 2
                mid_y = (segment.orig.coordy + segment.dest.coordy) / 2
                plt.text(mid_x, mid_y, f"{segment.cost:.2f}", color='black', fontsize=9,
                         ha='center', va='center')

        for node in graph.nodes:
            if node.name not in reachable_nodes:
                plt.plot(node.coordx, node.coordy, 'o', color='gray', markersize=8)
            # Mostrar nombre de todos los nodos claramente
            plt.text(node.coordx, node.coordy + 0.3, node.name, fontsize=10,
                     ha='center', va='center', color='black', weight='bold')

        for node_name in reachable_nodes:
            node = node_dict.get(node_name)
            if node:
                plt.plot(node.coordx, node.coordy, 'o', color='green', markersize=9)

        # Dibujar conexiones alcanzables
        drawn_edges = []
        for node_name in reachable_nodes:
            node = node_dict.get(node_name)
            if not node:
                continue

            for neighbor in node.neighbors:
                if neighbor.name in reachable_nodes:
                    edge = tuple(sorted([node_name, neighbor.name]))
                    if edge not in drawn_edges:
                        drawn_edges.append(edge)

                        # Flecha más delgada
                        dx = neighbor.coordx - node.coordx
                        dy = neighbor.coordy - node.coordy
                        plt.arrow(node.coordx, node.coordy, dx, dy,
                                  head_width=0.35, head_length=0.5, fc='green', ec='green',
                                  linewidth=1.2, length_includes_head=True, zorder=5)

                        # Mostrar costo
                        segment_cost = 0
                        for segment in graph.segments:
                            if (segment.orig.name == node_name and segment.dest.name == neighbor.name) or \
                                    (segment.orig.name == neighbor.name and segment.dest.name == node_name):
                                segment_cost = segment.cost
                                break
                        if segment_cost == 0:
                            segment_cost = Distance(node, neighbor)

                        mid_x = (node.coordx + neighbor.coordx) / 2
                        mid_y = (node.coordy + neighbor.coordy) / 2
                        plt.text(mid_x, mid_y, f"{segment_cost:.2f}", color='black', fontsize=9,
                                 ha='center', va='center', weight='bold')

        plt.tight_layout()
        plt.show()

    window = tk.Toplevel()
    window.title("Mostrar Nodos Alcanzables")
    tk.Label(window, text="Introduce el nombre del nodo inicial:").pack()
    entry = tk.Entry(window)
    entry.pack()
    tk.Button(window, text="Mostrar Alcanzables", command=display_reachable).pack()


def FindShortestPath(graph):
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return

    def display_shortest_path():
        start_node_name = entry_start.get()
        end_node_name = entry_end.get()

        # Validar nodos
        start_node = end_node = None
        for node in graph.nodes:
            if node.name == start_node_name:
                start_node = node
            if node.name == end_node_name:
                end_node = node

        if not start_node or not end_node:
            messagebox.showerror("Error", f"Uno o ambos nodos '{start_node_name}' y '{end_node_name}' no encontrados.")
            return

        try:
            from path import FindShortestPath as PathFindShortestPath
            path = PathFindShortestPath(graph, start_node_name, end_node_name)

            if not path or not path.nodes:
                messagebox.showinfo("Información",
                                    f"No se encontró un camino desde '{start_node_name}' hasta '{end_node_name}'.")
                return

            plt.figure()

            plt.grid(True, color='red', alpha=0.5, linestyle='dotted')

            # Obtener límites de ejes para mantener el mismo tamaño
            x_coords = [node.coordx for node in graph.nodes]
            y_coords = [node.coordy for node in graph.nodes]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            padding = max((x_max - x_min), (y_max - y_min)) * 0.1
            plt.xlim(x_min - padding, x_max + padding)
            plt.ylim(y_min - padding, y_max + padding)

            for segment in graph.segments:
                # Si el segmento no es parte del camino, dibujarlo en gris
                is_in_path = False
                for i in range(len(path.nodes) - 1):
                    if ((segment.orig.name == path.nodes[i].name and segment.dest.name == path.nodes[i + 1].name) or
                            (segment.dest.name == path.nodes[i].name and segment.orig.name == path.nodes[i + 1].name)):
                        is_in_path = True
                        break

                if not is_in_path:
                    plt.plot([segment.orig.coordx, segment.dest.coordx],
                             [segment.orig.coordy, segment.dest.coordy], '-', color='gray', alpha=0.6)
                    # Mostrar el costo en segmentos no resaltados
                    mid_x = (segment.orig.coordx + segment.dest.coordx) / 2
                    mid_y = (segment.orig.coordy + segment.dest.coordy) / 2
                    plt.text(mid_x, mid_y, f"{segment.cost:.2f}", color='black', fontsize=9,
                             ha='center', va='center')

            for node in graph.nodes:
                if node not in path.nodes:
                    plt.plot(node.coordx, node.coordy, 'o', color='gray', markersize=8)
                # Mostrar nombre del nodo con mayor visibilidad
                plt.text(node.coordx, node.coordy + 0.3, node.name, fontsize=10,
                         ha='center', va='center', color='black', weight='bold')

            for node in path.nodes:
                if node != start_node and node != end_node:  # Nodos intermedios
                    plt.plot(node.coordx, node.coordy, 'o', color='blue', markersize=9)

            plt.plot(start_node.coordx, start_node.coordy, 'o', color='blue', markersize=10)
            plt.plot(end_node.coordx, end_node.coordy, 'o', color='blue', markersize=10)

            total_cost = 0
            for i in range(len(path.nodes) - 1):
                orig, dest = path.nodes[i], path.nodes[i + 1]

                dx = dest.coordx - orig.coordx
                dy = dest.coordy - orig.coordy
                plt.arrow(orig.coordx, orig.coordy, dx, dy,
                          head_width=0.35, head_length=0.5, fc='blue', ec='blue', linewidth=1.2,
                          length_includes_head=True, zorder=5)

                segment_cost = 0
                for segment in graph.segments:
                    if (segment.orig.name == orig.name and segment.dest.name == dest.name) or \
                            (segment.orig.name == dest.name and segment.dest.name == orig.name):
                        segment_cost = segment.cost
                        break

                if segment_cost == 0:
                    from node import Distance
                    segment_cost = Distance(orig, dest)

                total_cost += segment_cost

                mid_x = (orig.coordx + dest.coordx) / 2
                mid_y = (orig.coordy + dest.coordy) / 2
                plt.text(mid_x, mid_y, f"{segment_cost:.2f}", color='blue', fontsize=9,
                         ha='center', va='center', weight='bold')

            plt.title(f"Camino más corto de {start_node_name} a {end_node_name} (Costo: {total_cost:.2f})")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar el camino más corto: {str(e)}")

    window = tk.Toplevel()
    window.title("Encontrar Camino Más Corto")
    tk.Label(window, text="Nodo de inicio:").pack()
    entry_start = tk.Entry(window)
    entry_start.pack()
    tk.Label(window, text="Nodo de destino:").pack()
    entry_end = tk.Entry(window)
    entry_end.pack()
    tk.Button(window, text="Buscar Camino", command=display_shortest_path).pack()


def LoadTestGraph():
    global graph
    try:
        graph = CreateGraph_1()
        if graph and graph.nodes:
            messagebox.showinfo("Éxito", "Grafo de prueba cargado correctamente.")
            ShowGraph()
        else:
            messagebox.showerror("Error", "No se pudo cargar el grafo de prueba.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el grafo de prueba: {str(e)}")


def LoadGraphFromFileUI():
    global graph
    filename = filedialog.askopenfilename(title="Selecciona un archivo de grafo",
                                          filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))
    if filename:
        new_graph = LoadGraphFromFile(filename)
        if new_graph and new_graph.nodes:
            graph = new_graph
            ShowGraph()
        else:
            messagebox.showerror("Error", "El archivo seleccionado no contiene un grafo válido.")


def AddNodeUI():
    if not graph:
        messagebox.showwarning("Aviso", "Primero debes crear o cargar un grafo.")
        return

    def add_node():
        name = entry_name.get()
        try:
            x = float(entry_x.get())
            y = float(entry_y.get())

            # Check if node with this name already exists
            for node in graph.nodes:
                if node.name == name:
                    messagebox.showerror("Error", f"Ya existe un nodo con el nombre '{name}'.")
                    return

            # Create and add the node
            new_node = Node(name, x, y)
            if AddNode(graph, new_node):
                messagebox.showinfo("Éxito", f"Nodo '{name}' añadido en ({x}, {y}).")
                plt.close()
                ShowGraph()
            else:
                messagebox.showerror("Error", "No se pudo añadir el nodo.")
        except ValueError:
            messagebox.showerror("Error", "Las coordenadas deben ser números.")

    window = tk.Toplevel()
    window.title("Añadir Nodo")
    tk.Label(window, text="Nombre del Nodo:").pack()
    entry_name = tk.Entry(window)
    entry_name.pack()
    tk.Label(window, text="Coordenada X:").pack()
    entry_x = tk.Entry(window)
    entry_x.pack()
    tk.Label(window, text="Coordenada Y:").pack()
    entry_y = tk.Entry(window)
    entry_y.pack()
    tk.Button(window, text="Añadir", command=add_node).pack()


def AddSegmentUI():
    if not graph:
        messagebox.showwarning("Aviso", "Primero debes crear o cargar un grafo.")
        return

    def add_segment():
        name = entry_name.get()
        origin = entry_origin.get()
        destination = entry_destination.get()
        if origin and destination:
            # Check if the node exists
            orig_exists = dest_exists = False
            for node in graph.nodes:
                if node.name == origin:
                    orig_exists = True
                if node.name == destination:
                    dest_exists = True

            if not orig_exists:
                messagebox.showerror("Error", f"El nodo de origen '{origin}' no existe.")
                return
            if not dest_exists:
                messagebox.showerror("Error", f"El nodo de destino '{destination}' no existe.")
                return

            if AddSegment(graph, name, origin, destination):
                messagebox.showinfo("Éxito", f"Segmento '{name}' añadido entre {origin} y {destination}.")
                plt.close()
                ShowGraph()
            else:
                messagebox.showerror("Error", "No se pudo añadir el segmento. Es posible que ya exista.")
        else:
            messagebox.showerror("Error", "Debes ingresar un nodo origen y un nodo destino.")

    window = tk.Toplevel()
    window.title("Añadir Segmento")
    tk.Label(window, text="Nombre del Segmento:").pack()
    entry_name = tk.Entry(window)
    entry_name.pack()
    tk.Label(window, text="Nodo Origen:").pack()
    entry_origin = tk.Entry(window)
    entry_origin.pack()
    tk.Label(window, text="Nodo Destino:").pack()
    entry_destination = tk.Entry(window)
    entry_destination.pack()
    tk.Button(window, text="Añadir", command=add_segment).pack()


def DeleteNodeUI():
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return

    def delete_node():
        name = entry.get()
        if name:
            # Check if node exists
            node_to_delete = None
            for node in graph.nodes:
                if node.name == name:
                    node_to_delete = node
                    break

            if not node_to_delete:
                messagebox.showerror("Error", f"No se encontró el nodo '{name}'.")
                return

            graph.nodes.remove(node_to_delete)
            # Remove any segments connected to this node
            graph.segments = [s for s in graph.segments if s.orig != node_to_delete and s.dest != node_to_delete]

            for node in graph.nodes:
                if node_to_delete in node.neighbors:
                    node.neighbors.remove(node_to_delete)

            messagebox.showinfo("Éxito", f"Nodo '{name}' eliminado, junto con sus segmentos.")
            plt.close()
            ShowGraph()
        else:
            messagebox.showerror("Error", "Debes ingresar el nombre del nodo a eliminar.")

    window = tk.Toplevel()
    window.title("Eliminar Nodo")
    tk.Label(window, text="Nombre del Nodo:").pack()
    entry = tk.Entry(window)
    entry.pack()
    tk.Button(window, text="Eliminar", command=delete_node).pack()


def SaveGraphToFileUI():
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. No hay nada que guardar.")
        return

    filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")),
                                            title="Guardar Grafo")
    if filename:
        SaveGraphToFile(graph, filename)
        messagebox.showinfo("Guardado", f"Grafo guardado en {filename}")


def MainInterface():
    root = tk.Tk()
    root.title("Gestión de Grafos")
    root.geometry("450x300")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    load_frame = tk.LabelFrame(frame, text="Cargar y Visualizar Grafo")
    load_frame.pack(fill="x", pady=10)

    button_load_test = tk.Button(load_frame, text="Cargar Grafo de Prueba", command=LoadTestGraph)
    button_load_test.grid(row=0, column=0, padx=5, pady=5)

    button_load_file = tk.Button(load_frame, text="Cargar desde Archivo", command=LoadGraphFromFileUI)
    button_load_file.grid(row=0, column=1, padx=5, pady=5)

    button_show = tk.Button(load_frame, text="Visualizar Grafo", command=ShowGraph)
    button_show.grid(row=0, column=2, padx=5, pady=5)

    analysis_frame = tk.LabelFrame(frame, text="Análisis del Grafo")
    analysis_frame.pack(fill="x", pady=10)

    button_neighbors = tk.Button(analysis_frame, text="Mostrar Vecinos", command=lambda: SelectNode(graph))
    button_neighbors.grid(row=0, column=0, padx=5, pady=5)

    button_reachable = tk.Button(analysis_frame, text="Mostrar Alcanzables", command=lambda: ShowReachableNodes(graph))
    button_reachable.grid(row=0, column=1, padx=5, pady=5)

    button_path = tk.Button(analysis_frame, text="Encontrar Camino", command=lambda: FindShortestPath(graph))
    button_path.grid(row=0, column=2, padx=5, pady=5)

    edit_frame = tk.LabelFrame(frame, text="Editar Grafo")
    edit_frame.pack(fill="x", pady=10)

    button_add_node = tk.Button(edit_frame, text="Añadir Nodo", command=AddNodeUI)
    button_add_node.grid(row=0, column=0, padx=5, pady=5)

    button_add_segment = tk.Button(edit_frame, text="Añadir Segmento", command=AddSegmentUI)
    button_add_segment.grid(row=0, column=1, padx=5, pady=5)

    button_delete_node = tk.Button(edit_frame, text="Eliminar Nodo", command=DeleteNodeUI)
    button_delete_node.grid(row=0, column=2, padx=5, pady=5)

    button_save = tk.Button(edit_frame, text="Guardar Grafo", command=SaveGraphToFileUI)
    button_save.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="we")

    # Mensaje de instrucciones
    instructions = tk.Label(frame,
                            text="Instrucciones: Primero carga un grafo o crea uno nuevo, luego utiliza las funciones de análisis.")
    instructions.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    MainInterface()
