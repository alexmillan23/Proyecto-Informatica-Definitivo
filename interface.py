import tkinter as tk
from tkinter import filedialog, messagebox
from graph import *
import matplotlib.pyplot as plt

from test_graph import CreateGraph_1  # Importamos la función para crear el grafo de prueba
from path import find_shortest_path, plot_path  # Import the shortest path function

# Variable global para gestionar el grafo en la interfaz, iniciada vacía.
graph = None

# Funciones de utilidad para visualizaciones
def setup_plot(title="Grafo"):
    """Configuración común para todas las visualizaciones"""
    plt.figure()
    plt.grid(True, color='red', alpha=0.5, linestyle='dotted')
    plt.title(title)
    return plt

def draw_arrow(plt, node1, node2, color='green', width=2):
    """Dibuja una flecha entre dos nodos"""
    dx = node2.coordx - node1.coordx
    dy = node2.coordy - node1.coordy
    plt.arrow(node1.coordx, node1.coordy, dx, dy, 
             head_width=0.5, head_length=0.7, fc=color, ec=color, linewidth=width,
             length_includes_head=True, zorder=5)

def set_axes_limits(plt, nodes):
    """Establece los límites de los ejes basados en las coordenadas de los nodos"""
    if not nodes:
        return
    x_coords = [node.coordx for node in nodes]
    y_coords = [node.coordy for node in nodes]
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    padding = max((x_max - x_min), (y_max - y_min)) * 0.1
    plt.xlim(x_min - padding, x_max + padding)
    plt.ylim(y_min - padding, y_max + padding)

# Función para mostrar el grafo (usa la variable global sin recibir parámetros)
def ShowGraph():
    global graph
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return
    plt.close()
    Plot(graph)
    plt.show()

# Función para seleccionar un nodo y mostrar sus vecinos
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

# Función para mostrar nodos alcanzables
def ShowReachableNodes(graph):
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return
        
    def display_reachable():
        start_node_name = entry.get()
        
        # Validar nodo de inicio
        start_node = None
        for node in graph.nodes:
            if node.name == start_node_name:
                start_node = node
                break
        
        if not start_node:
            messagebox.showerror("Error", f"Nodo '{start_node_name}' no encontrado.")
            return
        
        # Obtener nodos alcanzables
        reachable_nodes = graph.get_reachable_nodes(start_node_name)
        if not reachable_nodes:
            messagebox.showinfo("Información", f"No hay nodos alcanzables desde '{start_node_name}'.")
            return
        
        # Preparar visualización
        plt = setup_plot(f"Nodos alcanzables desde {start_node_name}")
        node_dict = {node.name: node for node in graph.nodes}
        set_axes_limits(plt, graph.nodes)
        
        # Dibujar segmentos no alcanzables en gris
        for segment in graph.segments:
            if segment.orig.name not in reachable_nodes or segment.dest.name not in reachable_nodes:
                plt.plot([segment.orig.coordx, segment.dest.coordx], 
                     [segment.orig.coordy, segment.dest.coordy], '-', color='gray', alpha=0.6)
                mid_x = (segment.orig.coordx + segment.dest.coordx) / 2
                mid_y = (segment.orig.coordy + segment.dest.coordy) / 2
                plt.text(mid_x, mid_y, f"{segment.cost:.2f}", color='black', fontsize=9,
                     ha='center', va='center')
        
        # Dibujar nodos no alcanzables en gris
        for node in graph.nodes:
            if node.name not in reachable_nodes:
                plt.plot(node.coordx, node.coordy, 'o', color='gray', markersize=8)
                plt.text(node.coordx, node.coordy + 0.3, node.name, fontsize=10,
                        ha='center', va='center', color='black')
        
        # Colorear nodos alcanzables
        for node_name in reachable_nodes:
            node = node_dict.get(node_name)
            if node:
                plt.plot(node.coordx, node.coordy, 'o', color='green', markersize=9)
                plt.text(node.coordx, node.coordy + 0.3, node.name, fontsize=10,
                        ha='center', va='center', color='black')
        
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
                        draw_arrow(plt, node, neighbor)
                        
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

# Función para encontrar el camino más corto entre dos nodos
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
            # Buscar camino más corto
            path = find_shortest_path(graph, start_node_name, end_node_name)
            if not path or not path.nodes:
                messagebox.showinfo("Información", f"No se encontró un camino desde '{start_node_name}' hasta '{end_node_name}'.")
                return
                
            # Usar el mismo estilo de visualización que el grafo principal
            plt.figure()
            
            # Establecer cuadrícula roja punteada
            plt.grid(True, color='red', alpha=0.5, linestyle='dotted')
            
            # Obtener límites de ejes para mantener el mismo tamaño
            x_coords = [node.coordx for node in graph.nodes]
            y_coords = [node.coordy for node in graph.nodes]
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            padding = max((x_max - x_min), (y_max - y_min)) * 0.1
            plt.xlim(x_min - padding, x_max + padding)
            plt.ylim(y_min - padding, y_max + padding)
            
            # Dibujar todos los segmentos en gris
            for segment in graph.segments:
                # Si el segmento no es parte del camino, dibujarlo en gris
                is_in_path = False
                for i in range(len(path.nodes) - 1):
                    if ((segment.orig.name == path.nodes[i].name and segment.dest.name == path.nodes[i+1].name) or
                        (segment.dest.name == path.nodes[i].name and segment.orig.name == path.nodes[i+1].name)):
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
            
            # Dibujar todos los nodos en gris, excepto inicio y fin
            for node in graph.nodes:
                # Si el nodo no es parte del camino, dibujarlo en gris
                if node not in path.nodes:
                    plt.plot(node.coordx, node.coordy, 'o', color='gray', markersize=8)
                plt.text(node.coordx, node.coordy + 0.3, node.name, fontsize=10,
                        ha='center', va='center', color='black')
            
            # Resaltar nodos del camino en azul
            for node in path.nodes:
                if node != start_node and node != end_node:  # Nodos intermedios
                    plt.plot(node.coordx, node.coordy, 'o', color='blue', markersize=9)
            
            # Resaltar inicio y fin
            plt.plot(start_node.coordx, start_node.coordy, 'o', color='blue', markersize=10)
            plt.plot(end_node.coordx, end_node.coordy, 'o', color='blue', markersize=10)
            
            # Dibujar el camino con flechas azules
            total_cost = 0
            for i in range(len(path.nodes) - 1):
                orig, dest = path.nodes[i], path.nodes[i + 1]
                
                # Dibujar flecha azul
                dx = dest.coordx - orig.coordx
                dy = dest.coordy - orig.coordy
                plt.arrow(orig.coordx, orig.coordy, dx, dy, 
                         head_width=0.5, head_length=0.7, fc='blue', ec='blue', linewidth=2,
                         length_includes_head=True, zorder=5)
                
                # Calcular costo del segmento
                segment_cost = 0
                for segment in graph.segments:
                    if (segment.orig.name == orig.name and segment.dest.name == dest.name) or \
                       (segment.orig.name == dest.name and segment.dest.name == orig.name):
                        segment_cost = segment.cost
                        break
                
                if segment_cost == 0:
                    segment_cost = Distance(orig, dest)
                
                total_cost += segment_cost
                
                # Mostrar costo en el gráfico con azul
                mid_x = (orig.coordx + dest.coordx) / 2
                mid_y = (orig.coordy + dest.coordy) / 2
                plt.text(mid_x, mid_y, f"{segment_cost:.2f}", color='blue', fontsize=9,
                         ha='center', va='center', weight='bold')
            
            plt.title(f"Camino más corto de {start_node_name} a {end_node_name} (Costo: {total_cost:.2f})")
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al encontrar el camino: {str(e)}")

    window = tk.Toplevel()
    window.title("Encontrar Camino Más Corto")
    tk.Label(window, text="Nodo Origen:").pack()
    entry_start = tk.Entry(window)
    entry_start.pack()
    tk.Label(window, text="Nodo Destino:").pack()
    entry_end = tk.Entry(window)
    entry_end.pack()
    tk.Button(window, text="Encontrar Camino", command=display_shortest_path).pack()

# Función para cargar el grafo de prueba desde test_graph.py
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

# Función para cargar un grafo desde un archivo
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

# Función para añadir nodos
def AddNodeUI():
    if not graph:
        messagebox.showwarning("Aviso", "Primero debes crear o cargar un grafo.")
        return
        
    def add_node():
        name = entry_name.get()
        try:
            x = float(entry_x.get())
            y = float(entry_y.get())
            AddNodeGraphically(graph, name, x, y)
            plt.close()
            ShowGraph()
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
    tk.Button(window, text="Añadir Nodo", command=add_node).pack()

# Función para añadir segmentos
def AddSegmentUI():
    if not graph:
        messagebox.showwarning("Aviso", "Primero debes crear o cargar un grafo.")
        return
        
    def add_segment():
        name = entry_name.get()
        origin = entry_origin.get()
        destination = entry_destination.get()
        if origin and destination:
            AddSegmentGraphically(graph, name, origin, destination)
            plt.close()
            ShowGraph()
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
    tk.Button(window, text="Añadir Segmento", command=add_segment).pack()

# Función para eliminar nodos
def DeleteNodeUI():
    if not graph or not graph.nodes:
        messagebox.showwarning("Aviso", "El grafo está vacío. Carga uno primero.")
        return
        
    def delete_node():
        name = entry_name.get()
        DeleteNodeGraphically(graph, name)
        plt.close()
        ShowGraph()

    window = tk.Toplevel()
    window.title("Eliminar Nodo")
    tk.Label(window, text="Nombre del Nodo:").pack()
    entry_name = tk.Entry(window)
    entry_name.pack()
    tk.Button(window, text="Eliminar Nodo", command=delete_node).pack()

# Función para guardar el grafo en un archivo de texto
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

# Ventana principal con botones
def MainInterface():
    root = tk.Tk()
    root.title("Gestión de Grafos")
    root.geometry("450x300")

    # Frame para organizar los botones
    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Sección 1: Cargar y visualizar el grafo
    load_frame = tk.LabelFrame(frame, text="Cargar y Visualizar Grafo")
    load_frame.pack(fill="x", pady=10)
    
    button_load_test = tk.Button(load_frame, text="Cargar Grafo de Prueba", command=LoadTestGraph)
    button_load_test.grid(row=0, column=0, padx=5, pady=5)
    
    button_load_file = tk.Button(load_frame, text="Cargar desde Archivo", command=LoadGraphFromFileUI)
    button_load_file.grid(row=0, column=1, padx=5, pady=5)
    
    button_show = tk.Button(load_frame, text="Visualizar Grafo", command=ShowGraph)
    button_show.grid(row=0, column=2, padx=5, pady=5)
    
    # Sección 2: Análisis del grafo
    analysis_frame = tk.LabelFrame(frame, text="Análisis del Grafo")
    analysis_frame.pack(fill="x", pady=10)
    
    button_neighbors = tk.Button(analysis_frame, text="Mostrar Vecinos", command=lambda: SelectNode(graph))
    button_neighbors.grid(row=0, column=0, padx=5, pady=5)
    
    button_reachable = tk.Button(analysis_frame, text="Mostrar Alcanzables", command=lambda: ShowReachableNodes(graph))
    button_reachable.grid(row=0, column=1, padx=5, pady=5)
    
    button_path = tk.Button(analysis_frame, text="Encontrar Camino", command=lambda: FindShortestPath(graph))
    button_path.grid(row=0, column=2, padx=5, pady=5)
    
    # Sección 3: Editar el grafo
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
    instructions = tk.Label(frame, text="Instrucciones: Primero carga un grafo o crea uno nuevo, luego utiliza las funciones de análisis.")
    instructions.pack(pady=10)
    
    root.mainloop()

# Ejecutar la interfaz principal
if __name__ == "__main__":
    MainInterface()
