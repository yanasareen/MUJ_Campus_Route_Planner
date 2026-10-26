import math

# Campus locations with 2D spatial coordinates (x, y) on campus map
LOCATIONS = {
    "Hostel": (0, 0),
    "Classroom": (3, 4),
    "Canteen": (0, 2),
    "Library": (7, 4),
    "Gate": (7, 0)
}

# Weighted graph representing walking paths and distance weights
CAMPUS_GRAPH = {
    "Hostel": {"Classroom": 4, "Canteen": 2},
    "Classroom": {"Hostel": 4, "Library": 5, "Gate": 10},
    "Canteen": {"Hostel": 2, "Library": 8},
    "Library": {"Classroom": 5, "Canteen": 8, "Gate": 3},
    "Gate": {"Classroom": 10, "Library": 3}
}

def get_euclidean_heuristics(goal):
    """
    Dynamically computes Euclidean (straight-line) distance from every location to goal.
    Formula: h(n) = sqrt((x2 - x1)^2 + (y2 - y1)^2)
    This heuristic is strictly admissible (never overestimates real path cost).
    """
    if goal not in LOCATIONS:
        raise ValueError(f"Goal '{goal}' not found in campus locations.")
    
    gx, gy = LOCATIONS[goal]
    heuristics = {}
    
    for loc, (x, y) in LOCATIONS.items():
        # Euclidean distance formula
        heuristics[loc] = math.sqrt((gx - x) ** 2 + (gy - y) ** 2)
        
    return heuristics

def get_available_locations():
    """Returns list of available campus building names."""
    return list(LOCATIONS.keys())
