from navPoint import NavPoint
from navSegment import NavSegment
from navAirport import NavAirport, add_sid, add_star
import math


class AirSpace:
    def __init__(self, name=""):
        self.name = name
        self.navpoints = {}  # Dictionary of NavPoints keyed by number
        self.navsegments = []  # List of NavSegments
        self.navairports = {}  # Dictionary of NavAirports keyed by name


def add_navpoint(airspace, navpoint):
    airspace.navpoints[navpoint.number] = navpoint


def add_navsegment(airspace, navsegment):
    airspace.navsegments.append(navsegment)


def add_navairport(airspace, navairport):
    airspace.navairports[navairport.name] = navairport


def get_navpoint_by_number(airspace, number):
    return airspace.navpoints.get(number)


def get_navpoint_by_name(airspace, name):
    for point in airspace.navpoints.values():
        if point.name == name:
            return point
    return None


def get_navairport_by_name(airspace, name):
    return airspace.navairports.get(name)


def load_from_files(airspace, nav_file, seg_file, aer_file):
    try:
        if nav_file.startswith(("Cat_", "cat_")):
            airspace.name = "Catalunya"
        elif nav_file.startswith(("Esp_", "esp_")):
            airspace.name = "España"
        elif nav_file.startswith(("Eur_", "eur_")):
            airspace.name = "Europe"

        with open(nav_file, 'r') as f:
            first_line = f.readline().strip()
            f.seek(0)

            try:
                parts = first_line.split()
                if len(parts) >= 4:
                    int(parts[0])
                    float(parts[2])
                    float(parts[3])
                    is_header = False
                else:
                    is_header = True
            except (ValueError, IndexError):
                is_header = True

            if is_header:
                next(f)

            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) >= 4:
                    number = int(parts[0])
                    name = parts[1]
                    latitude = float(parts[2])
                    longitude = float(parts[3])
                    add_navpoint(airspace, NavPoint(number, name, latitude, longitude))

        with open(seg_file, 'r') as f:
            first_line = f.readline().strip()
            f.seek(0)

            try:
                parts = first_line.split()
                if len(parts) >= 3:
                    int(parts[0])
                    int(parts[1])
                    float(parts[2])
                    is_header = False
                else:
                    is_header = True
            except (ValueError, IndexError):
                is_header = True

            if is_header:
                next(f)

            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) >= 3:
                    origin = int(parts[0])
                    destination = int(parts[1])
                    distance = float(parts[2])
                    add_navsegment(airspace, NavSegment(origin, destination, distance))

        with open(aer_file, 'r') as f:
            first_line = f.readline().strip()
            f.seek(0)

            try:
                parts = first_line.split()
                if len(parts) < 1 or parts[0].startswith('#'):
                    is_header = True
                else:
                    is_header = False
            except:
                is_header = True

            if is_header:
                next(f)
            current_airport = None
            reading_sids = True

            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.startswith(("LE", "LF")):
                    parts = line.split()
                    airport_code = parts[0]

                    if ',' in line:
                        continue
                    current_airport = NavAirport(airport_code)

                    point_numbers = [int(p) for p in parts[1:]]
                    mid_point = len(point_numbers) // 2

                    for sid in point_numbers[:mid_point]:
                        add_sid(current_airport, sid)

                    for star in point_numbers[mid_point:]:
                        add_star(current_airport, star)

                    add_navairport(airspace, current_airport)

        return True

    except Exception as e:
        print(f"Error loading airspace data: {e}")
        return False


def calculate_distance(airspace, point1, point2):
    R = 6371.0
    lat1 = math.radians(point1.latitude)
    lon1 = math.radians(point1.longitude)
    lat2 = math.radians(point2.latitude)
    lon2 = math.radians(point2.longitude)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


def find_neighbors(airspace, navpoint_number):
    neighbors = []

    for segment in airspace.navsegments:
        if segment.origin_number == navpoint_number:
            neighbors.append(segment.destination_number)
        elif segment.destination_number == navpoint_number:
            neighbors.append(segment.origin_number)

    return neighbors


def find_shortest_path(airspace, start_number, end_number):
    import heapq

    if start_number not in airspace.navpoints or end_number not in airspace.navpoints:
        return [], 0

    distances = {node: float('infinity') for node in airspace.navpoints}
    distances[start_number] = 0

    previous = {node: None for node in airspace.navpoints}

    priority_queue = [(0, start_number)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node == end_number:
            break

        if current_distance > distances[current_node]:
            continue

        neighbors = find_neighbors(airspace, current_node)

        for neighbor in neighbors:
            segment = None
            for seg in airspace.navsegments:
                if (seg.origin_number == current_node and seg.destination_number == neighbor) or \
                        (seg.destination_number == current_node and seg.origin_number == neighbor):
                    segment = seg
                    break

            if segment:
                distance = current_distance + segment.distance

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

    path = []
    current_node = end_number

    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]

    path.reverse()

    if not path or (len(path) == 1 and path[0] == start_number):
        return [], 0

    total_distance = distances[end_number]

    return path, total_distance
