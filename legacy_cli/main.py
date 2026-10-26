import sys
from algorithms import dijkstra, a_star
from campus import CAMPUS_GRAPH, LOCATIONS, get_available_locations, get_euclidean_heuristics

def display_locations():
    print("\nAvailable Campus Buildings:")
    locations = get_available_locations()
    for idx, loc in enumerate(locations, 1):
        coords = LOCATIONS[loc]
        print(f"  {idx}. {loc:<10} (x={coords[0]}, y={coords[1]})")
    return locations

def run_planner(start_location, goal_location):
    print(f"\n==================================================")
    print(f" ROUTE SEARCH: {start_location} -> {goal_location}")
    print(f"==================================================\n")

    # 1. Run Dijkstra
    d_path, d_dist, d_nodes = dijkstra(CAMPUS_GRAPH, start_location, goal_location)

    # 2. Run A* Search with Dynamic Euclidean Heuristics
    heuristics = get_euclidean_heuristics(goal_location)
    a_path, a_dist, a_nodes = a_star(CAMPUS_GRAPH, start_location, goal_location, heuristics)

    print("--------------------------------------------------")
    print(" 1. DIJKSTRA'S ALGORITHM (UNINFORMED SEARCH)")
    print("--------------------------------------------------")
    if d_path:
        print(f"Optimal Route   : {' -> '.join(d_path)}")
        print(f"Total Distance  : {d_dist:.2f} units")
        print(f"Nodes Explored  : {d_nodes}")
    else:
        print("No route found.")

    print("\n--------------------------------------------------")
    print(" 2. A* SEARCH ALGORITHM (INFORMED HEURISTIC SEARCH)")
    print("--------------------------------------------------")
    if a_path:
        print(f"Optimal Route   : {' -> '.join(a_path)}")
        print(f"Total Distance  : {a_dist:.2f} units")
        print(f"Nodes Explored  : {a_nodes}")
    else:
        print("No route found.")

    print("\n==================================================")
    print(" EFFICIENCY ANALYSIS")
    print("==================================================")
    print(f"Dijkstra Nodes Explored : {d_nodes}")
    print(f"A* Search Nodes Explored: {a_nodes}")
    diff = d_nodes - a_nodes
    if diff > 0:
        print(f"Efficiency Gain         : A* saved {diff} node exploration(s)!")
    elif diff == 0:
        print("Efficiency Gain         : Equal node exploration count.")
    else:
        print(f"Efficiency Gain         : Dijkstra expanded {-diff} fewer nodes.")
    print("==================================================\n")

def interactive_menu():
    locations = display_locations()
    print("\n--------------------------------------------------")
    
    try:
        start_idx = int(input(f"Select START location (1-{len(locations)}) [Default=1 Hostel]: ") or "1")
        goal_idx = int(input(f"Select GOAL location (1-{len(locations)})  [Default=4 Library]: ") or "4")
        
        start_loc = locations[start_idx - 1]
        goal_loc = locations[goal_idx - 1]
        run_planner(start_loc, goal_loc)
    except (ValueError, IndexError):
        print("\nInvalid selection! Running default (Hostel -> Library)...")
        run_planner("Hostel", "Library")

def main():
    print("==================================================")
    print("        SMART CAMPUS ROUTE PLANNER v1.0")
    print("==================================================")
    
    # Check if non-interactive terminal execution
    if not sys.stdin.isatty():
        run_planner("Hostel", "Library")
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
