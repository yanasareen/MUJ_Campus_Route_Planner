"""
Flask Web Application for AI Smart Campus Route Planner
Apex Institute of Technology & Science (AITS)
"""

import os
from flask import Flask, render_template, jsonify, request
from campus_graph import CAMPUS_NODES, CAMPUS_EDGES, ADJACENCY_GRAPH
import search_algorithms

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/campus", methods=["GET"])
def get_campus_data():
    return jsonify({
        "success": True,
        "nodes": CAMPUS_NODES,
        "edges": CAMPUS_EDGES,
        "total_nodes": len(CAMPUS_NODES),
        "total_edges": len(CAMPUS_EDGES),
        "campus_name": "Apex Institute of Technology & Science",
        "campus_code": "AITS-CAMPUS"
    })

@app.route("/api/route", methods=["POST"])
def calculate_route():
    data = request.get_json() or {}
    start = data.get("start", "AB1")
    goal = data.get("goal", "AB2")
    algo = data.get("algorithm", "ASTAR_EUC").upper()
    start_floor = int(data.get("start_floor", 1))
    goal_floor = int(data.get("goal_floor", 1))

    if start not in CAMPUS_NODES or goal not in CAMPUS_NODES:
        return jsonify({"success": False, "error": "Invalid start or destination location ID."}), 400

    if start == goal and start_floor == goal_floor:
        all_h = search_algorithms.compute_all_nodes_heuristics(start, goal, [start])
        return jsonify({
            "success": True,
            "algorithm": algo,
            "path": [start],
            "path_coords": search_algorithms.format_path_coords([start]),
            "visited_order": [],
            "nodes_expanded": 0,
            "execution_time_ms": 0.01,
            "metrics": {
                "total_distance_m": 0,
                "total_time_s": 0,
                "formatted_time": "0 min",
                "segments": [],
                "all_nodes_heuristics": all_h,
                "heuristic_trace": [{
                    "step_index": 0,
                    "node_id": start,
                    "short_name": CAMPUS_NODES[start]["short_name"],
                    "full_name": CAMPUS_NODES[start]["name"],
                    "floor": start_floor,
                    "g": 0.0,
                    "h": 0.0,
                    "f": 0.0,
                    "equation": "f(n) = 0m + 0m = 0m"
                }]
            }
        })

    # Dispatch to one of 6 algorithms
    if algo == "BFS":
        result = search_algorithms.breadth_first_search(start, goal, start_floor, goal_floor)
    elif algo == "DFS":
        result = search_algorithms.depth_first_search(start, goal, start_floor, goal_floor)
    elif algo == "UCS":
        result = search_algorithms.uniform_cost_search(start, goal, start_floor, goal_floor)
    elif algo == "ASTAR_EUC":
        result = search_algorithms.a_star_search(start, goal, heuristic_type="euclidean", start_floor=start_floor, goal_floor=goal_floor)
    elif algo == "ASTAR_MAN":
        result = search_algorithms.a_star_search(start, goal, heuristic_type="manhattan", start_floor=start_floor, goal_floor=goal_floor)
    elif algo == "GBFS":
        result = search_algorithms.greedy_best_first_search(start, goal, heuristic_type="euclidean", start_floor=start_floor, goal_floor=goal_floor)
    else:
        result = search_algorithms.a_star_search(start, goal, heuristic_type="euclidean", start_floor=start_floor, goal_floor=goal_floor)

    result["success"] = True
    result["start_floor"] = start_floor
    result["goal_floor"] = goal_floor

    return jsonify(result)

@app.route("/api/compare", methods=["POST"])
def compare_all():
    data = request.get_json() or {}
    start = data.get("start", "AB1")
    goal = data.get("goal", "AB2")
    start_floor = int(data.get("start_floor", 1))
    goal_floor = int(data.get("goal_floor", 1))

    if start not in CAMPUS_NODES or goal not in CAMPUS_NODES:
        return jsonify({"success": False, "error": "Invalid start or goal node."}), 400

    benchmark = search_algorithms.run_all_algorithms(
        start, goal, start_floor=start_floor, goal_floor=goal_floor
    )
    benchmark["success"] = True
    return jsonify(benchmark)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "Smart Campus AI Planner"})

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_available_port(preferred_port=5001):
    port = preferred_port
    while is_port_in_use(port) and port < preferred_port + 20:
        port += 1
    return port

if __name__ == "__main__":
    import threading, webbrowser
    target_port = int(os.environ.get("PORT", 5001))
    if "PORT" not in os.environ and is_port_in_use(target_port):
        target_port = find_available_port(target_port)
    
    url = f"http://127.0.0.1:{target_port}"
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    
    print(f"\n=======================================================")
    print(f"  🚀 Apex Smart Campus AI Route Planner is Live!")
    print(f"  👉 Opening in Browser: {url}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=target_port, debug=False)
