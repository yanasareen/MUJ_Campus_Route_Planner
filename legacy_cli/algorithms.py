import heapq

def dijkstra(graph, start, goal, return_visited_order=False):
    """
    Dijkstra's Algorithm implementation from scratch.
    Finds the shortest path from start to goal in a weighted graph using a min-heap priority queue.
    Cost function: f(n) = g(n)
    
    Returns:
        path (list): List of node names forming the shortest route, or None if unreachable.
        total_distance (float): Total path cost/distance to goal.
        explored_count (int): Total number of nodes popped from the priority queue.
        visited_order (list, optional): Order of nodes expanded (if return_visited_order=True).
    """
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    priority_queue = [(0, start)]
    visited = set()
    visited_order = []

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)
        visited_order.append(current_node)

        if current_node == goal:
            break

        for neighbor, weight in graph[current_node].items():
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbor))

    if distances[goal] == float("inf"):
        if return_visited_order:
            return None, float("inf"), len(visited), visited_order
        return None, float("inf"), len(visited)

    path = []
    current_node = goal
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()

    if return_visited_order:
        return path, distances[goal], len(visited), visited_order

    return path, distances[goal], len(visited)


def a_star(graph, start, goal, heuristics, return_visited_order=False):
    """
    A* Search Algorithm implementation from scratch.
    Finds the shortest path using g(n) + h(n) evaluation function with min-heap priority queue.
    Cost function: f(n) = g(n) + h(n)
    
    Returns:
        path (list): List of node names forming the shortest route, or None if unreachable.
        total_distance (float): Total path cost/distance to goal.
        explored_count (int): Total number of nodes popped from the priority queue.
        visited_order (list, optional): Order of nodes expanded (if return_visited_order=True).
    """
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}
    
    # Priority queue stores tuples of (f_score, node) where f_score = g_score + h(node)
    priority_queue = [(0 + heuristics.get(start, 0), start)]
    visited = set()
    visited_order = []

    while priority_queue:
        current_f, current_node = heapq.heappop(priority_queue)

        if current_node in visited:
            continue
        visited.add(current_node)
        visited_order.append(current_node)

        if current_node == goal:
            break

        for neighbor, weight in graph[current_node].items():
            new_g_distance = distances[current_node] + weight
            if new_g_distance < distances[neighbor]:
                distances[neighbor] = new_g_distance
                previous[neighbor] = current_node
                f_score = new_g_distance + heuristics.get(neighbor, 0)
                heapq.heappush(priority_queue, (f_score, neighbor))

    if distances[goal] == float("inf"):
        if return_visited_order:
            return None, float("inf"), len(visited), visited_order
        return None, float("inf"), len(visited)

    path = []
    current_node = goal
    while current_node is not None:
        path.append(current_node)
        current_node = previous[current_node]
    path.reverse()

    if return_visited_order:
        return path, distances[goal], len(visited), visited_order

    return path, distances[goal], len(visited)
