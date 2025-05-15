import tkinter as tk
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from airSpace import AirSpace, get_navpoint_by_name, load_from_files, find_shortest_path
from navSegment import get_origin_number, get_destination_number, get_distance

espacio_aereo = None


def explorar_archivo(variable_texto):
    nombre_archivo = filedialog.askopenfilename(
        initialdir=".",
        title="Seleccione un archivo",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")))

    if nombre_archivo:
        variable_texto.set(nombre_archivo)


def explorar_archivo_nav(app, archivo_nav):
    explorar_archivo(archivo_nav)


def explorar_archivo_seg(app, archivo_seg):
    explorar_archivo(archivo_seg)


def explorar_archivo_aer(app, archivo_aer):
    explorar_archivo(archivo_aer)


def cargar_datos_wrapper(app, archivo_nav, archivo_seg, archivo_aer, ventana):
    nav = archivo_nav.get()
    seg = archivo_seg.get()
    aer = archivo_aer.get()
    cargar_datos(app, nav, seg, aer, ventana)


def cargar_datos(app, archivo_nav, archivo_seg, archivo_aer, ventana):
    global espacio_aereo

    try:
        espacio_aereo = AirSpace()

        exito = load_from_files(espacio_aereo, archivo_nav, archivo_seg, archivo_aer)

        if exito:
            messagebox.showinfo("Éxito",
                                f"Datos cargados correctamente.\n\nPuntos de navegación: {len(espacio_aereo.navpoints)}\nSegmentos: {len(espacio_aereo.navsegments)}\nAeropuertos: {len(espacio_aereo.navairports)}",
                                parent=ventana)
            ventana.destroy()

            app.status.config(
                text=f"Datos cargados: {len(espacio_aereo.navpoints)} puntos, {len(espacio_aereo.navsegments)} segmentos, {len(espacio_aereo.navairports)} aeropuertos")
        else:
            messagebox.showerror("Error", "No se pudieron cargar los datos correctamente.", parent=ventana)
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar datos: {str(e)}", parent=ventana)


def limpiar_contenido(app):
    content_window = tk.Toplevel(app)
    content_window.title("Contenido de Espacio Aéreo")
    content_window.geometry("700x500")
    return content_window


def cargar_espacio_aereo(app):
    global espacio_aereo

    load_window = tk.Toplevel(app)
    load_window.title("Cargar Datos de Espacio Aéreo")
    load_window.geometry("450x250")

    file_frame = tk.Frame(load_window)
    file_frame.pack(fill=tk.X, pady=10, padx=10)

    nav_label = tk.Label(file_frame, text="Archivo de Puntos de Navegación:")
    nav_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    nav_file = tk.StringVar(value="Cat_nav.txt")
    nav_entry = tk.Entry(file_frame, textvariable=nav_file, width=30)
    nav_entry.grid(row=0, column=1, padx=5, pady=5)

    nav_browse = tk.Button(file_frame, text="...",
                           command=lambda: explorar_archivo_nav(app, nav_file))
    nav_browse.grid(row=0, column=2, padx=5, pady=5)

    seg_label = tk.Label(file_frame, text="Archivo de Segmentos:")
    seg_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

    seg_file = tk.StringVar(value="Cat_seg.txt")
    seg_entry = tk.Entry(file_frame, textvariable=seg_file, width=30)
    seg_entry.grid(row=1, column=1, padx=5, pady=5)

    seg_browse = tk.Button(file_frame, text="...",
                           command=lambda: explorar_archivo_seg(app, seg_file))
    seg_browse.grid(row=1, column=2, padx=5, pady=5)

    air_label = tk.Label(file_frame, text="Archivo de Aeropuertos:")
    air_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)

    air_file = tk.StringVar(value="Cat_aer.txt")
    air_entry = tk.Entry(file_frame, textvariable=air_file, width=30)
    air_entry.grid(row=2, column=1, padx=5, pady=5)

    air_browse = tk.Button(file_frame, text="...",
                           command=lambda: explorar_archivo_aer(app, air_file))
    air_browse.grid(row=2, column=2, padx=5, pady=5)

    load_button = tk.Button(load_window, text="Cargar Datos",
                            command=lambda: cargar_datos_wrapper(app, nav_file, seg_file, air_file, load_window))
    load_button.pack(pady=10)


def mostrar_espacio_aereo(app, punto_destacado=None, vecinos=None, ruta=None):
    global espacio_aereo

    if not espacio_aereo or not espacio_aereo.navpoints:
        messagebox.showwarning("Advertencia",
                               "No hay datos de espacio aéreo cargados. Por favor cargue los datos primero.")
        return

    map_window = tk.Toplevel(app)
    map_window.title("Mapa de Espacio Aéreo")
    map_window.geometry("1200x900")

    fig = Figure(figsize=(15, 12), dpi=100)
    ax = fig.add_subplot(111)

    is_neighbor_view = bool(punto_destacado and vecinos)

    lon_values = []
    lat_values = []

    point_cache = {}

    for num, point in espacio_aereo.navpoints.items():
        lon_values.append(point.longitude)
        lat_values.append(point.latitude)
        point_cache[point.number] = point

    margin = 0.1
    lon_min = min(lon_values) - margin
    lon_max = max(lon_values) + margin
    lat_min = min(lat_values) - margin
    lat_max = max(lat_values) + margin

    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.set_autoscale_on(False)  # Disable autoscaling
    ax.set_clip_on(True)

    segment_color = 'cyan'
    point_color = 'black'
    highlight_color = 'red'
    neighbor_color = highlight_color
    path_color = '#00CCCC'

    for segment in espacio_aereo.navsegments:
        point1 = point_cache.get(segment.origin_number)
        point2 = point_cache.get(segment.destination_number)

        if point1 and point2:
            draw_this_segment = False
            current_line_color = segment_color
            current_line_width = 1.0

            if is_neighbor_view:
                neighbor_numbers = [n[0].number for n in vecinos]
                if (point1.number == punto_destacado.number and point2.number in neighbor_numbers) or \
                        (point2.number == punto_destacado.number and point1.number in neighbor_numbers):
                    current_line_color = segment_color
                    current_line_width = 1.0
                    draw_this_segment = True
            else:
                if ruta:
                    draw_this_segment = False
                    for i in range(len(ruta) - 1):
                        if ((ruta[i].number == point1.number and ruta[i + 1].number == point2.number) or
                                (ruta[i].number == point2.number and ruta[i + 1].number == point1.number)):
                            draw_this_segment = True
                            current_line_color = '#00CCCC'
                            current_line_width = 1.5

                            if ruta[i].number == point1.number and ruta[i + 1].number == point2.number:
                                start_point = (point1.longitude, point1.latitude)
                                end_point = (point2.longitude, point2.latitude)
                            else:
                                start_point = (point2.longitude, point2.latitude)
                                end_point = (point1.longitude, point1.latitude)
                            break
                else:
                    draw_this_segment = True
                    current_line_color = segment_color
                    current_line_width = 1.0

            if draw_this_segment:
                if ruta and 'start_point' in locals() and 'end_point' in locals():
                    ax.annotate("",
                                xy=end_point,
                                xytext=start_point,
                                arrowprops=dict(arrowstyle='->', color=current_line_color,
                                                lw=current_line_width, shrinkA=0, shrinkB=0, clip_on=True),
                                clip_on=True)
                else:
                    ax.plot([point1.longitude, point2.longitude],
                            [point1.latitude, point2.latitude],
                            color=current_line_color,
                            linewidth=current_line_width,
                            clip_on=True)

                mid_x = (point1.longitude + point2.longitude) / 2
                mid_y = (point1.latitude + point2.latitude) / 2
                ax.text(mid_x, mid_y, f"{segment.distance:.1f}",
                        fontsize=6, ha='center', va='center',
                        bbox=dict(facecolor='white', alpha=0.5, pad=0.5), zorder=2, clip_on=True)

    for num, point in espacio_aereo.navpoints.items():
        this_color = point_color
        this_size = 5
        this_alpha = 1.0
        this_zorder = 10

        if ruta and any(p.number == point.number for p in ruta):
            this_color = '#00CCCC'
            this_size = 10
            this_zorder = 20
        elif ruta:
            this_alpha = 0.5
            this_size = 4
        elif is_neighbor_view:
            neighbor_numbers = [n[0].number for n in vecinos]
            if point.number == punto_destacado.number:
                this_color = highlight_color
                this_size = 30
            elif point.number in neighbor_numbers:
                this_color = neighbor_color
                this_size = 20
            else:
                this_color = 'gray'
                this_size = 5

        ax.scatter(point.longitude, point.latitude, color=this_color, s=this_size, alpha=this_alpha, zorder=this_zorder,
                   clip_on=True)

        ax.text(point.longitude + 0.01, point.latitude + 0.01, point.name,
                fontsize=6, ha='left', va='bottom', zorder=6, clip_on=True)

    if not is_neighbor_view and not ruta:
        ax.grid(True, linestyle=':', alpha=0.7, color='red')

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor('black')
        spine.set_linewidth(0.5)

    if ruta:
        total_cost = 0
        for i in range(len(ruta)):
            point = ruta[i]
            if i > 0:
                prev_point = ruta[i - 1]
                for segment in espacio_aereo.navsegments:
                    if ((get_origin_number(segment) == prev_point.number and get_destination_number(
                            segment) == point.number) or
                            (get_origin_number(segment) == point.number and get_destination_number(
                                segment) == prev_point.number)):
                        total_cost += get_distance(segment)
                        break

        ax.set_title(f"Gráfico con camino. Coste = {total_cost:.8f}", pad=20, y=1.02)
    elif is_neighbor_view:
        ax.set_title(f"Grafico con los vecinos del nodo {punto_destacado.name}", fontsize=14, pad=20, y=1.02)
    else:
        ax.set_title("Gráfico con nodos y segmentos", fontsize=14, pad=20, y=1.02)

    fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

    canvas = FigureCanvasTkAgg(fig, master=map_window)  # A tk.DrawingArea.
    canvas.draw()

    # Create a proper layout for the canvas and toolbar
    canvas_frame = tk.Frame(map_window)
    canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, canvas_frame)
    toolbar.update()

    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    instructions_text = "Utilice la barra de herramientas para navegar por el mapa."
    instructions_label = tk.Label(map_window, text=instructions_text, font=("Arial", 10))
    instructions_label.pack(pady=5)

    status_message = "Mostrando mapa de espacio aéreo"
    if punto_destacado:
        status_message += f" - Destacando punto: {punto_destacado.name}"
    elif vecinos:
        status_message += f" - Mostrando {len(vecinos)} vecinos"
    elif ruta:
        status_message += f" - Mostrando ruta con {len(ruta)} puntos"

    app.status.config(text=status_message)

    return canvas, ax


def mostrar_vecinos(app):
    global espacio_aereo

    if not espacio_aereo or not espacio_aereo.navpoints:
        messagebox.showwarning("Advertencia",
                               "No hay datos de espacio aéreo cargados. Por favor cargue los datos primero.")
        return

    neighbors_window = tk.Toplevel(app)
    neighbors_window.title("Encontrar Vecinos")
    neighbors_window.geometry("500x400")

    input_frame = tk.Frame(neighbors_window)
    input_frame.pack(fill=tk.X, pady=10, padx=10)

    point_label = tk.Label(input_frame, text="Punto de Navegación:")
    point_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    nav_point = tk.StringVar()
    point_entry = tk.Entry(input_frame, textvariable=nav_point, width=20)
    point_entry.grid(row=0, column=1, padx=5, pady=5)

    results_text = tk.Text(neighbors_window, width=50, height=15)
    results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(results_text)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    results_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=results_text.yview)

    find_button = tk.Button(neighbors_window, text="Encontrar Vecinos",
                            command=lambda: encontrar_y_mostrar_vecinos(app, results_text, nav_point))
    find_button.pack(pady=10)


def encontrar_y_mostrar_vecinos(app, results_text, nav_point):
    global espacio_aereo

    results_text.delete(1.0, tk.END)

    nav_name = nav_point.get().strip()

    if not nav_name:
        messagebox.showwarning("Advertencia", "Por favor ingrese un nombre de punto de navegación.")
        return

    found_point = get_navpoint_by_name(espacio_aereo, nav_name)

    if not found_point:
        results_text.insert(tk.END, f"Punto de navegación '{nav_name}' no encontrado.")
        return

    vecinos = []
    for segment in espacio_aereo.navsegments:
        if get_origin_number(segment) == found_point.number:
            destination_number = get_destination_number(segment)
            if destination_number in espacio_aereo.navpoints:
                vecino = espacio_aereo.navpoints[destination_number]
                distancia = get_distance(segment)
                vecinos.append((vecino, distancia))

    vecinos.sort(key=lambda x: x[0].name)

    result_text = f"Vecinos de {found_point.name} (Número: {found_point.number}):\n"
    result_text += f"Ubicación: ({found_point.latitude}, {found_point.longitude})\n\n"

    if vecinos:
        for neighbor_info in vecinos:
            neighbor = neighbor_info[0]
            distance = neighbor_info[1]
            result_text += f"{neighbor.name} (Número: {neighbor.number}) - Distancia: {distance:.2f}\n"
    else:
        result_text += "No se encontraron vecinos."

    results_text.insert(tk.END, result_text)

    mostrar_espacio_aereo(app, punto_destacado=found_point, vecinos=vecinos)

    app.status.config(text=f"Encontrados {len(vecinos)} vecinos para {found_point.name}")


def encontrar_ruta(app):
    global espacio_aereo

    if not espacio_aereo or not espacio_aereo.navpoints:
        messagebox.showwarning("Advertencia",
                               "No hay datos de espacio aéreo cargados. Por favor cargue los datos primero.")
        return

    path_window = tk.Toplevel(app)
    path_window.title("Encontrar Ruta")
    path_window.geometry("500x400")

    input_frame = tk.Frame(path_window)
    input_frame.pack(fill=tk.X, pady=10, padx=10)

    origin_label = tk.Label(input_frame, text="Punto de Origen:")
    origin_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

    origin_point = tk.StringVar()
    origin_entry = tk.Entry(input_frame, textvariable=origin_point, width=20)
    origin_entry.grid(row=0, column=1, padx=5, pady=5)

    dest_label = tk.Label(input_frame, text="Punto de Destino:")
    dest_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)

    dest_point = tk.StringVar()
    dest_entry = tk.Entry(input_frame, textvariable=dest_point, width=20)
    dest_entry.grid(row=1, column=1, padx=5, pady=5)

    path_text = tk.Text(path_window, width=50, height=15)
    path_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(path_text)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    path_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=path_text.yview)

    find_button = tk.Button(path_window, text="Encontrar Ruta",
                            command=lambda: encontrar_y_mostrar_ruta(app, path_text, origin_point, dest_point))
    find_button.pack(pady=10)


def encontrar_y_mostrar_ruta(app, path_text, origin_point, dest_point):
    global espacio_aereo

    path_text.delete(1.0, tk.END)

    origin_name = origin_point.get().strip()
    dest_name = dest_point.get().strip()

    if not origin_name or not dest_name:
        messagebox.showwarning("Advertencia", "Por favor ingrese ambos puntos de origen y destino.")
        return

    origin = get_navpoint_by_name(espacio_aereo, origin_name)
    destination = get_navpoint_by_name(espacio_aereo, dest_name)

    if not origin:
        path_text.insert(tk.END, f"Punto de origen '{origin_name}' no encontrado.\n")
        return

    if not destination:
        path_text.insert(tk.END, f"Punto de destino '{dest_name}' no encontrado.\n")
        return

    resultado_ruta = find_shortest_path(espacio_aereo, origin.number, destination.number)

    if resultado_ruta and resultado_ruta[0]:
        lista_numeros, distancia_total = resultado_ruta

        ruta = []
        for num_punto in lista_numeros:
            if num_punto in espacio_aereo.navpoints:
                ruta.append(espacio_aereo.navpoints[num_punto])

        result_text = f"Ruta de {origin.name} a {destination.name}:\n\n"

        for i, punto in enumerate(ruta):
            result_text += f"{i + 1}. {punto.name} (Número: {punto.number})\n"

            if i < len(ruta) - 1:
                next_punto = ruta[i + 1]
                for segment in espacio_aereo.navsegments:
                    if ((get_origin_number(segment) == punto.number and get_destination_number(
                            segment) == next_punto.number) or
                            (get_destination_number(segment) == punto.number and get_origin_number(
                                segment) == next_punto.number)):
                        result_text += f"   Distancia al siguiente punto: {get_distance(segment):.2f}\n"
                        break

        result_text += f"\nDistancia total: {distancia_total:.2f}\n"

        path_text.insert(tk.END, result_text)

        mostrar_espacio_aereo(app, ruta=ruta)

        app.status.config(text=f"Ruta encontrada con {len(ruta)} puntos. Distancia total: {distancia_total:.2f}")
    else:
        path_text.insert(tk.END, f"No se encontró una ruta entre {origin.name} y {destination.name}.")


def calcular_distancia_ruta(ruta):
    total_distance = 0
    for i in range(len(ruta) - 1):
        total_distance += calcular_distancia_entre_puntos(ruta[i], ruta[i + 1])
    return total_distance


def calcular_distancia_entre_puntos(point1, point2):
    for segment in espacio_aereo.navsegments:
        if (segment.origin_number == point1.number and segment.destination_number == point2.number) or \
                (segment.origin_number == point2.number and segment.destination_number == point1.number):
            return segment.distance

    from math import radians, sin, cos, sqrt, atan2
    R = 3440.065

    lat1 = radians(point1.latitude)
    lon1 = radians(point1.longitude)
    lat2 = radians(point2.latitude)
    lon2 = radians(point2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c

    return distance


class AplicacionNavegacionEspacioAereo(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Navegación de Espacio Aéreo")
        self.geometry("550x400")  # Aumentar tamaño de ventana

        try:
            self.iconbitmap("aircraft.ico")
        except:
            pass

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        load_frame = tk.LabelFrame(self.main_frame, text="Cargar y Ver Datos")
        load_frame.pack(fill="x", pady=5)

        button_load = tk.Button(load_frame, text="Cargar Datos de Espacio Aéreo",
                                command=lambda: cargar_espacio_aereo(self))
        button_load.grid(row=0, column=0, padx=5, pady=5)

        button_show = tk.Button(load_frame, text="Mostrar Mapa de Espacio Aéreo",
                                command=lambda: mostrar_espacio_aereo(self))
        button_show.grid(row=0, column=1, padx=5, pady=5)

        analysis_frame = tk.LabelFrame(self.main_frame, text="Análisis de Espacio Aéreo")
        analysis_frame.pack(fill="x", pady=5)

        button_neighbors = tk.Button(analysis_frame, text="Mostrar Vecinos",
                                     command=lambda: mostrar_vecinos(self))
        button_neighbors.grid(row=0, column=0, padx=5, pady=5)

        button_path = tk.Button(analysis_frame, text="Encontrar Ruta",
                                command=lambda: encontrar_ruta(self))
        button_path.grid(row=0, column=1, padx=5, pady=5)

        instructions = tk.Label(self.main_frame,
                                text="Instrucciones: Primero cargue los datos de espacio aéreo, luego utilice las herramientas de análisis.",
                                wraplength=500,
                                justify=tk.LEFT)
        instructions.pack(pady=10, fill=tk.X, padx=10)

        self.status = tk.Label(self.main_frame, text="Listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        global espacio_aereo
        espacio_aereo = None


def main():
    app = AplicacionNavegacionEspacioAereo()
    app.mainloop()


if __name__ == "__main__":
    main()
