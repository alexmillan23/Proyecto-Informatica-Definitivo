import tkinter as tk
from tkinter import filedialog, messagebox
from graph import *
import matplotlib.pyplot as plt
from test_graph import CreateGraph_1  # Importamos la función para crear el grafo de prueba

# Variable global para gestionar el grafo en la interfaz, iniciada vacía.
graph = None


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


# Función para cargar el grafo de prueba desde test_graph.py
def LoadTestGraph():
    global graph
    try:
        graph = CreateGraph_1()  # Crea el grafo de prueba
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
                                          filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if filename:
        new_graph = LoadGraphFromFile(filename)  # Carga el grafo de forma temporal
        if new_graph and new_graph.nodes:
            graph = new_graph  # Se asigna solo si el grafo tiene nodos
            ShowGraph()  # Se muestra el grafo cargado
        else:
            messagebox.showerror("Error", "El archivo seleccionado no contiene un grafo válido.")


# Función para añadir nodos
def AddNodeUI():
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
    filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")),
                                            title="Guardar Grafo")
    if filename:
        SaveGraphToFile(graph, filename)
        messagebox.showinfo("Guardado", f"Grafo guardado en {filename}")


# Ventana principal con botones
def MainInterface():
    global graph
    root = tk.Tk()
    root.title("Interfaz Gráfica - Gestión de Grafos")

    tk.Button(root, text="Cargar Grafo de Prueba", command=LoadTestGraph).pack()
    tk.Button(root, text="Mostrar Grafo desde Archivo", command=LoadGraphFromFileUI).pack()
    tk.Button(root, text="Seleccionar Nodo y Mostrar Vecinos", command=lambda: SelectNode(graph)).pack()
    tk.Button(root, text="Añadir Nodo", command=AddNodeUI).pack()
    tk.Button(root, text="Añadir Segmento", command=AddSegmentUI).pack()
    tk.Button(root, text="Eliminar Nodo", command=DeleteNodeUI).pack()
    tk.Button(root, text="Guardar Grafo", command=SaveGraphToFileUI).pack()

    root.mainloop()


if __name__ == "__main__":
    MainInterface()
