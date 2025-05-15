class NavSegment:
    def __init__(self, origin_number, destination_number, distance):
        self.origin_number = origin_number
        self.destination_number = destination_number
        self.distance = distance


def navsegment_to_str(navsegment):
    return f"Segment: {navsegment.origin_number} -> {navsegment.destination_number}, Distance: {navsegment.distance} km"


def get_origin_number(navsegment):
    return navsegment.origin_number


def get_destination_number(navsegment):
    return navsegment.destination_number


def get_distance(navsegment):
    return navsegment.distance
