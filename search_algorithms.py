"""
Search Algorithms Engine for Smart Campus Route Planner
Apex Institute of Technology & Science (AITS)
AI & Soft Computing Core

Supported 6 Algorithms:
1. A* Search (Euclidean Heuristic) - Informed Optimal
2. A* Search (Manhattan Heuristic) - Informed Grid
3. Dijkstra / Uniform-Cost Search (UCS) - Cost Optimal
4. Breadth-First Search (BFS) - Hop Optimal
5. Greedy Best-First Search (GBFS) - Heuristic Driven
6. Depth-First Search (DFS) - Uninformed Wandering

Features:
- Exact g(n) and h(n) for EVERY location on campus and along the route
- Prominent f(n) = g(n) + h(n) evaluation trace
- Multi-floor vertical transit (Elevators Left/Right/Both, Stairs, Balconies)
"""

import time
import heapq
import math
from collections import deque
from typing import Dict, List, Any, Optional, Tuple, Set
from campus_graph import (
    CAMPUS_NODES,
    ADJACENCY_GRAPH,
    calculate_euclidean_distance,
    calculate_manhattan_distance
)

def get_heuristic(u_id: str, goal_id: str, heuristic_type: str = "euclidean") -> float:
    """Computes admissible heuristic h(n) between node and goal."""
    if u_id == goal_id:
        return 0.0
    u = CAMPUS_NODES[u_id]
    goal = CAMPUS_NODES[goal_id]
    if heuristic_type == "manhattan":
        return calculate_manhattan_distance(u, goal)
    return calculate_euclidean_distance(u, goal)

def reconstruct_path(parent_map: Dict[str, Optional[str]], goal_id: str) -> List[str]:
    curr: Optional[str] = goal_id
    path = []
    while curr is not None:
        path.append(curr)
        curr = parent_map.get(curr)
    path.reverse()
    return path

def generate_floor_instructions(
    node_id: str,
    from_floor: int,
    to_floor: int,
    is_departure: bool = True
) -> Dict[str, Any]:
    node = CAMPUS_NODES.get(node_id, {})
    if not node.get("has_floors", False):
        return {
            "requires_vertical_transit": False,
            "summary": f"At {node.get('short_name', node_id)} (Ground Level)"
        }
    
    floors_data = node.get("floors", {})
    floor_info = floors_data.get(from_floor, {})
    target_floor_info = floors_data.get(to_floor, {})

    lift_side = node.get("lift_side", "both").upper()
    lift_summary = node.get("lift_summary", "")
    stairs_summary = node.get("stairs_summary", "")
    balcony_summary = node.get("balcony_summary", "")

    current_balcony = floor_info.get("balcony", {}).get("location", "Floor Balcony")
    current_lift = floor_info.get("lift", {}).get("details", f"{lift_side} elevator")
    current_stairs = floor_info.get("stairs", {}).get("location", "Main staircase")

    floor_diff = abs(to_floor - from_floor)
    vertical_time_s = floor_diff * 14.0

    if is_departure and from_floor != 1:
        text = (
            f"Start at Floor {from_floor}: Exit via {current_balcony}. "
            f"Take the {lift_side} elevator ({current_lift}) or {current_stairs} to descend to Ground Level (Floor 1)."
        )
    elif not is_departure and to_floor != 1:
        text = (
            f"Enter {node['short_name']} Ground Level: Proceed to the {lift_side} elevator ({current_lift}) "
            f"or take the {current_stairs}. Ascend {floor_diff} floor(s) to Floor {to_floor}. "
            f"Walk past the {target_floor_info.get('balcony', {}).get('location', 'Balcony')} to reach your room."
        )
    else:
        text = (
            f"At {node['short_name']} (Floor {from_floor}): "
            f"Elevator is on the {lift_side} side. "
            f"Stairs: {current_stairs}. "
            f"Balcony: {current_balcony}."
        )

    return {
        "requires_vertical_transit": from_floor != to_floor,
        "from_floor": from_floor,
        "to_floor": to_floor,
        "floor_diff": floor_diff,
        "vertical_time_s": vertical_time_s,
        "lift_side": lift_side,
        "lift_details": current_lift,
        "lift_summary": lift_summary,
        "stairs_details": current_stairs,
        "stairs_summary": stairs_summary,
        "balcony_details": current_balcony,
        "balcony_summary": balcony_summary,
        "instruction": text
    }

def compute_all_nodes_heuristics(
    start_id: str,
    goal_id: str,
    path: List[str],
    heuristic_type: str = "euclidean"
) -> Dict[str, Dict[str, float]]:
    """
    Computes exact g(n), h(n), and f(n) for EVERY location on the entire campus,
    anchoring path nodes with actual traveled distance g(n), and other nodes with
    straight-line approximation from origin.
    """
    result = {}
    path_set = set(path)
    
    # Calculate exact cumulative g along the path
    path_g_map = {}
    cum_g = 0.0
    for i in range(len(path)):
        nid = path[i]
        if i > 0:
            prev_id = path[i - 1]
            edge_dist = None
            for e in ADJACENCY_GRAPH.get(prev_id, []):
                if e["neighbor"] == nid:
                    edge_dist = e["distance"]
                    break
            if edge_dist is None:
                edge_dist = calculate_euclidean_distance(CAMPUS_NODES[prev_id], CAMPUS_NODES[nid])
            cum_g += edge_dist
        path_g_map[nid] = round(cum_g, 1)

    start_node = CAMPUS_NODES[start_id]
    goal_node = CAMPUS_NODES[goal_id]

    for nid, node in CAMPUS_NODES.items():
        if nid in path_g_map:
            g_val = path_g_map[nid]
        else:
            # Euclidean distance from start
            g_val = round(calculate_euclidean_distance(start_node, node), 1)

        h_val = round(get_heuristic(nid, goal_id, heuristic_type), 1)
        f_val = round(g_val + h_val, 1)

        result[nid] = {
            "node_id": nid,
            "short_name": node["short_name"],
            "name": node["name"],
            "g": g_val,
            "h": h_val,
            "f": f_val,
            "is_on_path": nid in path_set
        }

    return result

def compute_path_metrics(
    path: List[str],
    start_floor: int = 1,
    goal_floor: int = 1,
    goal_id: Optional[str] = None,
    heuristic_type: str = "euclidean"
) -> Dict[str, Any]:
    if not path:
        return {
            "total_distance_m": 0,
            "total_time_s": 0,
            "formatted_time": "0 min",
            "segments": [],
            "heuristic_trace": [],
            "all_nodes_heuristics": {}
        }

    # Standard visible walking speed: 4.8 km/h = 1.33 m/s
    speed_mps = (4.8 * 1000) / 3600

    total_dist = 0.0
    segments = []
    heuristic_trace = []
    effective_goal = goal_id if goal_id else path[-1]
    effective_start = path[0]

    cumulative_g = 0.0
    for i in range(len(path)):
        node_id = path[i]
        node = CAMPUS_NODES[node_id]
        
        if i > 0:
            prev_id = path[i - 1]
            prev_node = CAMPUS_NODES[prev_id]
            edge_info = None
            for edge in ADJACENCY_GRAPH.get(prev_id, []):
                if edge["neighbor"] == node_id:
                    edge_info = edge
                    break
            dist = edge_info["distance"] if edge_info else calculate_euclidean_distance(prev_node, node)
            cumulative_g += dist
        
        h_val = get_heuristic(node_id, effective_goal, heuristic_type)
        f_val = round(cumulative_g + h_val, 1)

        floor_assigned = start_floor if i == 0 else (goal_floor if i == len(path) - 1 else 1)

        heuristic_trace.append({
            "step_index": i,
            "node_id": node_id,
            "short_name": node["short_name"],
            "full_name": node["name"],
            "floor": floor_assigned,
            "g": round(cumulative_g, 1),
            "h": round(h_val, 1),
            "f": f_val,
            "equation": f"f({node['short_name']}) = g({round(cumulative_g, 1)}m) + h({round(h_val, 1)}m) = {f_val}m"
        })

    for i in range(len(path) - 1):
        u_id = path[i]
        v_id = path[i + 1]
        u_node = CAMPUS_NODES[u_id]
        v_node = CAMPUS_NODES[v_id]
        
        edge_info = None
        for edge in ADJACENCY_GRAPH.get(u_id, []):
            if edge["neighbor"] == v_id:
                edge_info = edge
                break
        
        dist = edge_info["distance"] if edge_info else calculate_euclidean_distance(u_node, v_node)
        surface = edge_info["surface"] if edge_info else "paved"
        scenic = edge_info["scenic_rating"] if edge_info else 0.5
        seg_time = round(dist / max(speed_mps, 0.1), 1)
        total_dist += dist

        segments.append({
            "from_id": u_id,
            "to_id": v_id,
            "from_name": u_node["short_name"],
            "to_name": v_node["short_name"],
            "distance_m": round(dist, 1),
            "estimated_time_s": seg_time,
            "surface": surface,
            "scenic_rating": scenic,
            "g_at_step": heuristic_trace[i+1]["g"],
            "h_at_step": heuristic_trace[i+1]["h"],
            "f_at_step": heuristic_trace[i+1]["f"]
        })

    total_dist = round(total_dist, 1)
    total_time_s = round(total_dist / speed_mps, 1)

    start_floor_instr = generate_floor_instructions(path[0], start_floor, 1, is_departure=True)
    goal_floor_instr = generate_floor_instructions(path[-1], 1, goal_floor, is_departure=False)

    total_time_s += start_floor_instr.get("vertical_time_s", 0)
    total_time_s += goal_floor_instr.get("vertical_time_s", 0)
    minutes = round(total_time_s / 60, 1)

    all_nodes_heuristics = compute_all_nodes_heuristics(effective_start, effective_goal, path, heuristic_type)

    return {
        "total_distance_m": total_dist,
        "total_time_s": total_time_s,
        "formatted_time": f"{minutes} min" if minutes >= 1 else f"{int(total_time_s)} sec",
        "segments": segments,
        "heuristic_trace": heuristic_trace,
        "all_nodes_heuristics": all_nodes_heuristics,
        "departure_floor_details": start_floor_instr,
        "destination_floor_details": goal_floor_instr
    }

def format_path_coords(path: List[str]) -> List[Dict[str, Any]]:
    result = []
    for node_id in path:
        node = CAMPUS_NODES[node_id]
        result.append({
            "id": node["id"],
            "name": node["name"],
            "short_name": node["short_name"],
            "category": node["category"],
            "zone": node["zone"],
            "x": node["x"],
            "y": node["y"],
            "icon": node["icon"],
            "has_floors": node.get("has_floors", False),
            "lift_side": node.get("lift_side", "both"),
            "lift_summary": node.get("lift_summary", ""),
            "stairs_summary": node.get("stairs_summary", ""),
            "balcony_summary": node.get("balcony_summary", ""),
            "floors": node.get("floors", {})
        })
    return result

# -------------------------------------------------------------
# 1. BREADTH-FIRST SEARCH (BFS)
# -------------------------------------------------------------
def breadth_first_search(start_id: str, goal_id: str, start_floor: int = 1, goal_floor: int = 1) -> Dict[str, Any]:
    t_start = time.perf_counter()
    queue = deque([start_id])
    visited: Set[str] = {start_id}
    parent: Dict[str, Optional[str]] = {start_id: None}
    visited_order: List[Dict[str, Any]] = []
    step = 0

    while queue:
        curr = queue.popleft()
        step += 1
        h_val = get_heuristic(curr, goal_id)
        visited_order.append({
            "step": step,
            "node_id": curr,
            "name": CAMPUS_NODES[curr]["short_name"],
            "parent_id": parent.get(curr),
            "g": 0.0,
            "h": round(h_val, 1),
            "f": round(h_val, 1)
        })

        if curr == goal_id:
            break

        for edge in ADJACENCY_GRAPH.get(curr, []):
            nbr = edge["neighbor"]
            if nbr not in visited:
                visited.add(nbr)
                parent[nbr] = curr
                queue.append(nbr)

    t_end = time.perf_counter()
    path = reconstruct_path(parent, goal_id) if goal_id in visited else []
    metrics = compute_path_metrics(path, start_floor=start_floor, goal_floor=goal_floor, goal_id=goal_id)

    return {
        "algorithm": "BFS",
        "name": "Breadth-First Search",
        "found": len(path) > 0,
        "path": path,
        "path_coords": format_path_coords(path),
        "visited_order": visited_order,
        "nodes_expanded": len(visited_order),
        "total_nodes_visited": len(visited),
        "execution_time_ms": round((t_end - t_start) * 1000, 3),
        "metrics": metrics,
        "optimality": "Hop-Optimal (Minimal Junctions)",
        "heuristic_formula": "f(n) = depth(n)",
        "description": "Explores shallowest unvisited nodes first using a FIFO queue."
    }

# -------------------------------------------------------------
# 2. DEPTH-FIRST SEARCH (DFS)
# -------------------------------------------------------------
def depth_first_search(start_id: str, goal_id: str, start_floor: int = 1, goal_floor: int = 1) -> Dict[str, Any]:
    t_start = time.perf_counter()
    stack = [start_id]
    visited: Set[str] = set()
    parent: Dict[str, Optional[str]] = {start_id: None}
    visited_order: List[Dict[str, Any]] = []
    step = 0

    while stack:
        curr = stack.pop()
        if curr in visited:
            continue
        visited.add(curr)
        step += 1
        h_val = get_heuristic(curr, goal_id)
        visited_order.append({
            "step": step,
            "node_id": curr,
            "name": CAMPUS_NODES[curr]["short_name"],
            "parent_id": parent.get(curr),
            "g": 0.0,
            "h": round(h_val, 1),
            "f": round(h_val, 1)
        })

        if curr == goal_id:
            break

        for edge in reversed(ADJACENCY_GRAPH.get(curr, [])):
            nbr = edge["neighbor"]
            if nbr not in visited:
                parent[nbr] = curr
                stack.append(nbr)

    t_end = time.perf_counter()
    path = reconstruct_path(parent, goal_id) if goal_id in visited else []
    metrics = compute_path_metrics(path, start_floor=start_floor, goal_floor=goal_floor, goal_id=goal_id)

    return {
        "algorithm": "DFS",
        "name": "Depth-First Search",
        "found": len(path) > 0,
        "path": path,
        "path_coords": format_path_coords(path),
        "visited_order": visited_order,
        "nodes_expanded": len(visited_order),
        "total_nodes_visited": len(visited),
        "execution_time_ms": round((t_end - t_start) * 1000, 3),
        "metrics": metrics,
        "optimality": "Non-Optimal (Wandering Detours)",
        "heuristic_formula": "LIFO Stack Search",
        "description": "Follows each corridor branch to the end before backtracking."
    }

# -------------------------------------------------------------
# 3. DIJKSTRA / UNIFORM-COST SEARCH (UCS)
# -------------------------------------------------------------
def uniform_cost_search(start_id: str, goal_id: str, start_floor: int = 1, goal_floor: int = 1) -> Dict[str, Any]:
    t_start = time.perf_counter()
    pq: List[Tuple[float, int, str]] = [(0.0, 0, start_id)]
    counter = 0
    g_costs: Dict[str, float] = {start_id: 0.0}
    parent: Dict[str, Optional[str]] = {start_id: None}
    visited: Set[str] = set()
    visited_order: List[Dict[str, Any]] = []
    step = 0

    while pq:
        curr_g, _, curr = heapq.heappop(pq)
        if curr in visited:
            continue
        visited.add(curr)
        step += 1
        h_val = get_heuristic(curr, goal_id)
        visited_order.append({
            "step": step,
            "node_id": curr,
            "name": CAMPUS_NODES[curr]["short_name"],
            "parent_id": parent.get(curr),
            "g": round(curr_g, 1),
            "h": 0.0,
            "f": round(curr_g, 1)
        })

        if curr == goal_id:
            break

        for edge in ADJACENCY_GRAPH.get(curr, []):
            nbr = edge["neighbor"]
            dist = edge["distance"]
            new_g = curr_g + dist
            if nbr not in g_costs or new_g < g_costs[nbr]:
                g_costs[nbr] = new_g
                parent[nbr] = curr
                counter += 1
                heapq.heappush(pq, (new_g, counter, nbr))

    t_end = time.perf_counter()
    path = reconstruct_path(parent, goal_id) if goal_id in visited else []
    metrics = compute_path_metrics(path, start_floor=start_floor, goal_floor=goal_floor, goal_id=goal_id)

    return {
        "algorithm": "UCS",
        "name": "Dijkstra (Uniform-Cost)",
        "found": len(path) > 0,
        "path": path,
        "path_coords": format_path_coords(path),
        "visited_order": visited_order,
        "nodes_expanded": len(visited_order),
        "total_nodes_visited": len(visited),
        "execution_time_ms": round((t_end - t_start) * 1000, 3),
        "metrics": metrics,
        "optimality": "Distance-Optimal (True Minimal Meters)",
        "heuristic_formula": "f(n) = g(n)",
        "description": "Expands lowest accumulated path distance g(n). Guarantees true shortest path."
    }

# -------------------------------------------------------------
# 4. A* SEARCH (Euclidean & Manhattan)
# -------------------------------------------------------------
def a_star_search(
    start_id: str,
    goal_id: str,
    heuristic_type: str = "euclidean",
    start_floor: int = 1,
    goal_floor: int = 1
) -> Dict[str, Any]:
    t_start = time.perf_counter()
    initial_h = get_heuristic(start_id, goal_id, heuristic_type)
    pq: List[Tuple[float, float, int, str]] = [(initial_h, 0.0, 0, start_id)]
    counter = 0
    g_costs: Dict[str, float] = {start_id: 0.0}
    parent: Dict[str, Optional[str]] = {start_id: None}
    visited: Set[str] = set()
    visited_order: List[Dict[str, Any]] = []
    step = 0

    while pq:
        f_val, curr_g, _, curr = heapq.heappop(pq)
        if curr in visited:
            continue
        visited.add(curr)
        step += 1
        h_val = get_heuristic(curr, goal_id, heuristic_type)
        visited_order.append({
            "step": step,
            "node_id": curr,
            "name": CAMPUS_NODES[curr]["short_name"],
            "parent_id": parent.get(curr),
            "g": round(curr_g, 1),
            "h": round(h_val, 1),
            "f": round(f_val, 1),
            "equation": f"f({CAMPUS_NODES[curr]['short_name']}) = g({round(curr_g, 1)}m) + h({round(h_val, 1)}m) = {round(f_val, 1)}m"
        })

        if curr == goal_id:
            break

        for edge in ADJACENCY_GRAPH.get(curr, []):
            nbr = edge["neighbor"]
            dist = edge["distance"]
            new_g = curr_g + dist
            if nbr not in g_costs or new_g < g_costs[nbr]:
                g_costs[nbr] = new_g
                parent[nbr] = curr
                counter += 1
                nbr_h = get_heuristic(nbr, goal_id, heuristic_type)
                nbr_f = new_g + nbr_h
                heapq.heappush(pq, (nbr_f, new_g, counter, nbr))

    t_end = time.perf_counter()
    path = reconstruct_path(parent, goal_id) if goal_id in visited else []
    metrics = compute_path_metrics(
        path,
        start_floor=start_floor,
        goal_floor=goal_floor,
        goal_id=goal_id,
        heuristic_type=heuristic_type
    )

    formula = (
        "f(n) = g(n) + sqrt(Δx² + Δy²)" if heuristic_type == "euclidean"
        else "f(n) = g(n) + (|Δx| + |Δy|)"
    )

    return {
        "algorithm": "ASTAR_EUC" if heuristic_type == "euclidean" else "ASTAR_MAN",
        "name": f"A* ({heuristic_type.capitalize()})",
        "heuristic": heuristic_type,
        "found": len(path) > 0,
        "path": path,
        "path_coords": format_path_coords(path),
        "visited_order": visited_order,
        "nodes_expanded": len(visited_order),
        "total_nodes_visited": len(visited),
        "execution_time_ms": round((t_end - t_start) * 1000, 3),
        "metrics": metrics,
        "optimality": "AISC Distance-Optimal",
        "heuristic_formula": formula,
        "description": f"Evaluates nodes using f(n) = g(n) + h(n) with admissible {heuristic_type} metric."
    }

# -------------------------------------------------------------
# 5. GREEDY BEST-FIRST SEARCH (GBFS)
# -------------------------------------------------------------
def greedy_best_first_search(
    start_id: str,
    goal_id: str,
    heuristic_type: str = "euclidean",
    start_floor: int = 1,
    goal_floor: int = 1
) -> Dict[str, Any]:
    t_start = time.perf_counter()
    initial_h = get_heuristic(start_id, goal_id, heuristic_type)
    pq: List[Tuple[float, int, str]] = [(initial_h, 0, start_id)]
    counter = 0
    parent: Dict[str, Optional[str]] = {start_id: None}
    visited: Set[str] = set()
    visited_order: List[Dict[str, Any]] = []
    step = 0

    while pq:
        h_val, _, curr = heapq.heappop(pq)
        if curr in visited:
            continue
        visited.add(curr)
        step += 1
        visited_order.append({
            "step": step,
            "node_id": curr,
            "name": CAMPUS_NODES[curr]["short_name"],
            "parent_id": parent.get(curr),
            "g": 0.0,
            "h": round(h_val, 1),
            "f": round(h_val, 1)
        })

        if curr == goal_id:
            break

        for edge in ADJACENCY_GRAPH.get(curr, []):
            nbr = edge["neighbor"]
            if nbr not in visited:
                if nbr not in parent:
                    parent[nbr] = curr
                counter += 1
                nbr_h = get_heuristic(nbr, goal_id, heuristic_type)
                heapq.heappush(pq, (nbr_h, counter, nbr))

    t_end = time.perf_counter()
    path = reconstruct_path(parent, goal_id) if goal_id in visited else []
    metrics = compute_path_metrics(
        path,
        start_floor=start_floor,
        goal_floor=goal_floor,
        goal_id=goal_id,
        heuristic_type=heuristic_type
    )

    return {
        "algorithm": "GBFS",
        "name": "Greedy Best-First Search",
        "heuristic": heuristic_type,
        "found": len(path) > 0,
        "path": path,
        "path_coords": format_path_coords(path),
        "visited_order": visited_order,
        "nodes_expanded": len(visited_order),
        "total_nodes_visited": len(visited),
        "execution_time_ms": round((t_end - t_start) * 1000, 3),
        "metrics": metrics,
        "optimality": "Heuristic-Greedy",
        "heuristic_formula": "f(n) = h(n)",
        "description": "Always steps toward the node with lowest h(n) value."
    }

# -------------------------------------------------------------
# Comparison Matrix (Exactly 6 Algorithms)
# -------------------------------------------------------------
def run_all_algorithms(
    start_id: str,
    goal_id: str,
    start_floor: int = 1,
    goal_floor: int = 1
) -> Dict[str, Any]:
    astar_euc = a_star_search(start_id, goal_id, "euclidean", start_floor, goal_floor)
    astar_man = a_star_search(start_id, goal_id, "manhattan", start_floor, goal_floor)
    ucs_res = uniform_cost_search(start_id, goal_id, start_floor, goal_floor)
    bfs_res = breadth_first_search(start_id, goal_id, start_floor, goal_floor)
    gbfs_res = greedy_best_first_search(start_id, goal_id, "euclidean", start_floor, goal_floor)
    dfs_res = depth_first_search(start_id, goal_id, start_floor, goal_floor)

    summary_table = [
        {
            "id": "ASTAR_EUC",
            "name": "A* (Euclidean)",
            "type": "Informed AI",
            "formula": "f = g + h_euc",
            "distance_m": astar_euc["metrics"]["total_distance_m"],
            "time_formatted": astar_euc["metrics"]["formatted_time"],
            "nodes_expanded": astar_euc["nodes_expanded"],
            "path_hops": len(astar_euc["path"]) - 1,
            "exec_ms": astar_euc["execution_time_ms"],
            "optimal": "Optimal"
        },
        {
            "id": "ASTAR_MAN",
            "name": "A* (Manhattan)",
            "type": "Informed AI",
            "formula": "f = g + h_man",
            "distance_m": astar_man["metrics"]["total_distance_m"],
            "time_formatted": astar_man["metrics"]["formatted_time"],
            "nodes_expanded": astar_man["nodes_expanded"],
            "path_hops": len(astar_man["path"]) - 1,
            "exec_ms": astar_man["execution_time_ms"],
            "optimal": "Optimal"
        },
        {
            "id": "UCS",
            "name": "Dijkstra (Uniform-Cost)",
            "type": "Cost-Optimal",
            "formula": "f = g",
            "distance_m": ucs_res["metrics"]["total_distance_m"],
            "time_formatted": ucs_res["metrics"]["formatted_time"],
            "nodes_expanded": ucs_res["nodes_expanded"],
            "path_hops": len(ucs_res["path"]) - 1,
            "exec_ms": ucs_res["execution_time_ms"],
            "optimal": "Distance Optimal"
        },
        {
            "id": "BFS",
            "name": "Breadth-First Search (BFS)",
            "type": "Uninformed",
            "formula": "f = depth",
            "distance_m": bfs_res["metrics"]["total_distance_m"],
            "time_formatted": bfs_res["metrics"]["formatted_time"],
            "nodes_expanded": bfs_res["nodes_expanded"],
            "path_hops": len(bfs_res["path"]) - 1,
            "exec_ms": bfs_res["execution_time_ms"],
            "optimal": "Hop Optimal"
        },
        {
            "id": "GBFS",
            "name": "Greedy Best-First Search",
            "type": "Informed Greedy",
            "formula": "f = h",
            "distance_m": gbfs_res["metrics"]["total_distance_m"],
            "time_formatted": gbfs_res["metrics"]["formatted_time"],
            "nodes_expanded": gbfs_res["nodes_expanded"],
            "path_hops": len(gbfs_res["path"]) - 1,
            "exec_ms": gbfs_res["execution_time_ms"],
            "optimal": "Suboptimal"
        },
        {
            "id": "DFS",
            "name": "Depth-First Search (DFS)",
            "type": "Uninformed",
            "formula": "LIFO stack",
            "distance_m": dfs_res["metrics"]["total_distance_m"],
            "time_formatted": dfs_res["metrics"]["formatted_time"],
            "nodes_expanded": dfs_res["nodes_expanded"],
            "path_hops": len(dfs_res["path"]) - 1,
            "exec_ms": dfs_res["execution_time_ms"],
            "optimal": "Suboptimal Wandering"
        }
    ]

    return {
        "start": CAMPUS_NODES[start_id],
        "goal": CAMPUS_NODES[goal_id],
        "summary": summary_table,
        "results": {
            "ASTAR_EUC": astar_euc,
            "ASTAR_MAN": astar_man,
            "UCS": ucs_res,
            "BFS": bfs_res,
            "GBFS": gbfs_res,
            "DFS": dfs_res
        }
    }
