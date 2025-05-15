class NavPoint:
    def __init__(self, number, name, latitude, longitude):
        self.number = number
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


def navpoint_to_str(navpoint):
    return f"{navpoint.name}: ({navpoint.latitude}, {navpoint.longitude})"

def get_coords(navpoint):
    return (navpoint.latitude, navpoint.longitude)
