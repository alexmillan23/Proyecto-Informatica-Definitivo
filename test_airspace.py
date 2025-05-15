from airSpace import AirSpace, load_from_files, get_navpoint_by_number, get_navpoint_by_name, get_navairport_by_name, \
    find_neighbors, find_shortest_path
from navPoint import get_coords, navpoint_to_str
from navSegment import get_origin_number, get_destination_number, get_distance
from navAirport import get_sids, get_stars
import matplotlib.pyplot as plt
import os


def test_catalonia_airspace():
    """Test loading and processing Catalonia airspace data."""
    # Create an airspace object for Catalonia
    catalonia = AirSpace("Catalonia")

    # Define the data file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nav_file = os.path.join(current_dir, "Cat_nav.txt")
    seg_file = os.path.join(current_dir, "Cat_seg.txt")
    aer_file = os.path.join(current_dir, "Cat_aer.txt")

    # Load data from files
    print("Loading Catalonia airspace data...")
    success = load_from_files(catalonia, nav_file, seg_file, aer_file)

    if not success:
        print("Failed to load airspace data.")
        return

    print(catalonia)
    print(f"Number of navigation points: {len(catalonia.navpoints)}")
    print(f"Number of segments: {len(catalonia.navsegments)}")
    print(f"Number of airports: {len(catalonia.navairports)}")

    # Display some navigation points
    print("\nSample navigation points:")
    count = 0
    for number, point in list(catalonia.navpoints.items())[:5]:
        print(f"  {navpoint_to_str(point)}")
        count += 1

    # Display some segments
    print("\nSample segments:")
    for segment in catalonia.navsegments[:5]:
        origin = get_navpoint_by_number(catalonia, get_origin_number(segment))
        dest = get_navpoint_by_number(catalonia, get_destination_number(segment))
        if origin and dest:
            print(f"  {origin.name} -> {dest.name}: {get_distance(segment):.2f} km")

    # Display some airports with their SIDs and STARs
    print("\nSample airports:")
    for name, airport in list(catalonia.navairports.items())[:3]:
        print(f"  {name}:")
        print(f"    SIDs: {', '.join(str(sid) for sid in get_sids(airport)[:3])}...")
        print(f"    STARs: {', '.join(str(star) for star in get_stars(airport)[:3])}...")

    # Find neighbors of a specific navigation point (GODOX)
    godox = get_navpoint_by_name(catalonia, "GODOX")
    if godox:
        print(f"\nNeighbors of {godox.name}:")
        neighbors = find_neighbors(catalonia, godox.number)
        for neighbor_num in neighbors:
            neighbor = get_navpoint_by_number(catalonia, neighbor_num)
            if neighbor:
                print(f"  {neighbor.name}")

    # Find shortest path between two airports (LEBL to LEZG)
    lebl = get_navairport_by_name(catalonia, "LEBL")
    lezg = get_navairport_by_name(catalonia, "LEZG")

    if lebl and lezg and get_sids(lebl) and get_stars(lezg):
        # Use the first SID from LEBL and first STAR to LEZG
        start_point = get_sids(lebl)[0]
        end_point = get_stars(lezg)[0]

        print(f"\nFinding shortest path from LEBL (via SID {start_point}) to LEZG (via STAR {end_point}):")
        path, distance = find_shortest_path(catalonia, start_point, end_point)

        if path:
            print(f"  Path length: {len(path)} points, Total distance: {distance:.2f} km")
            print("  Path:")
            for point_num in path:
                point = get_navpoint_by_number(catalonia, point_num)
                if point:
                    print(f"    {point.name}")
        else:
            print("  No path found.")

    # Plot the entire airspace
    plot_airspace(catalonia)

    # Plot neighbors of GODOX
    if godox:
        plot_neighbors(catalonia, godox.number)

    # Plot shortest path between LEBL and LEZG
    if lebl and lezg and get_sids(lebl) and get_stars(lezg):
        plot_shortest_path(catalonia, start_point, end_point)


def plot_airspace(airspace):
    """Plot the entire airspace with all navigation points and segments."""
    plt.figure(figsize=(12, 10))
    plt.title(f"Graph of the {airspace.name} airspace")

    # Plot all navigation points
    for number, point in airspace.navpoints.items():
        plt.plot(point.longitude, point.latitude, 'k.', markersize=2)

        # Only show some labels to avoid clutter
        if number % 5 == 0:  # Show every 5th label
            plt.text(point.longitude, point.latitude, point.name, fontsize=6)

    # Plot all segments
    for segment in airspace.navsegments:
        origin = get_navpoint_by_number(airspace, get_origin_number(segment))
        dest = get_navpoint_by_number(airspace, get_destination_number(segment))
        if origin and dest:
            plt.plot([origin.longitude, dest.longitude],
                     [origin.latitude, dest.latitude],
                     'c-', linewidth=0.5, alpha=0.6)

    # Plot airports with different marker
    for name, airport in airspace.navairports.items():
        # Use the first SID point to represent the airport location
        if get_sids(airport):
            point = get_navpoint_by_number(airspace, get_sids(airport)[0])
            if point:
                plt.plot(point.longitude, point.latitude, 'ro', markersize=5)
                plt.text(point.longitude, point.latitude, name, fontsize=8,
                         weight='bold', ha='right', va='bottom')

    plt.grid(True, alpha=0.3)
    plt.savefig('catalonia_airspace.png', dpi=300)
    plt.show()


def plot_neighbors(airspace, point_number):
    """Plot a specific navigation point and its neighbors."""
    plt.figure(figsize=(12, 10))

    center_point = get_navpoint_by_number(airspace, point_number)
    if not center_point:
        print(f"Navigation point {point_number} not found.")
        return

    plt.title(f"Graph with neighbors of node {center_point.name}")

    # Plot all navigation points in gray
    for number, point in airspace.navpoints.items():
        plt.plot(point.longitude, point.latitude, '.', color='gray', markersize=2)
        plt.text(point.longitude, point.latitude, point.name, fontsize=6, color='gray')

    # Find neighbors
    neighbors = find_neighbors(airspace, point_number)

    # Plot neighbors in blue
    for neighbor_num in neighbors:
        neighbor = get_navpoint_by_number(airspace, neighbor_num)
        if neighbor:
            plt.plot(neighbor.longitude, neighbor.latitude, 'b.', markersize=4)
            plt.text(neighbor.longitude, neighbor.latitude, neighbor.name,
                     fontsize=8, color='blue', weight='bold')

            # Plot connection to center point
            plt.plot([center_point.longitude, neighbor.longitude],
                     [center_point.latitude, neighbor.latitude],
                     'c-', linewidth=1.5)

    # Plot center point in red
    plt.plot(center_point.longitude, center_point.latitude, 'ro', markersize=6)
    plt.text(center_point.longitude, center_point.latitude, center_point.name,
             fontsize=10, color='red', weight='bold')

    plt.grid(True, alpha=0.3)
    plt.savefig(f'neighbors_{center_point.name}.png', dpi=300)
    plt.show()


def plot_shortest_path(airspace, start_point, end_point):
    """Plot the shortest path between two navigation points."""
    plt.figure(figsize=(12, 10))

    path, distance = find_shortest_path(airspace, start_point, end_point)
    if not path:
        print(f"No path found between points {start_point} and {end_point}.")
        return

    start = get_navpoint_by_number(airspace, start_point)
    end = get_navpoint_by_number(airspace, end_point)

    plt.title(f"Graph with shortest path, Cost = {distance:.8f}")

    # Plot all navigation points in gray
    for number, point in airspace.navpoints.items():
        plt.plot(point.longitude, point.latitude, '.', color='gray', markersize=2)
        plt.text(point.longitude, point.latitude, point.name, fontsize=6, color='gray')

    # Plot points in the path
    path_points = [get_navpoint_by_number(airspace, num) for num in path]
    path_points = [p for p in path_points if p]  # Filter out None values

    # Plot path segments
    for i in range(len(path_points) - 1):
        plt.plot([path_points[i].longitude, path_points[i + 1].longitude],
                 [path_points[i].latitude, path_points[i + 1].latitude],
                 'c-', linewidth=2)

    # Plot path points
    for point in path_points:
        plt.plot(point.longitude, point.latitude, 'c.', markersize=6)
        plt.text(point.longitude, point.latitude, point.name,
                 fontsize=8, color='blue', weight='bold')

    # Highlight start and end points
    plt.plot(start.longitude, start.latitude, 'go', markersize=8)
    plt.plot(end.longitude, end.latitude, 'ro', markersize=8)

    plt.grid(True, alpha=0.3)
    plt.savefig(f'shortest_path_{start.name}_to_{end.name}.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    test_catalonia_airspace()
