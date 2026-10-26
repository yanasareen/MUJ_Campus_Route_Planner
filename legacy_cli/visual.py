import time
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import streamlit as st

# Import core project components
from algorithms import dijkstra, a_star
from campus import CAMPUS_GRAPH, LOCATIONS, get_available_locations, get_euclidean_heuristics

# -----------------------------------------------------------------------------
# 1. STREAMLIT PAGE CONFIG & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Smart Campus Route Planner", page_icon="📍", layout="centered")

st.title("📍 Smart Campus Route Planner")
st.write("Select a starting location and destination to compare **Dijkstra's Algorithm** and **A* Search Algorithm** with a visual campus map.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. MATPLOTLIB GRAPH PLOTTING FUNCTION
# -----------------------------------------------------------------------------
def plot_campus_map(start, goal, path=None):
    """Plots the campus graph network, node locations, edge weights, and highlighted route."""
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=120)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#f8fafc')

    # Draw Graph Edges & Distance Weights
    drawn_edges = set()
    for u, neighbors in CAMPUS_GRAPH.items():
        x1, y1 = LOCATIONS[u]
        for v, weight in neighbors.items():
            edge = tuple(sorted([u, v]))
            if edge not in drawn_edges:
                drawn_edges.add(edge)
                x2, y2 = LOCATIONS[v]
                ax.plot([x1, x2], [y1, y2], color='#94a3b8', linestyle='--', linewidth=2, zorder=1)
                
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ax.text(
                    mid_x, mid_y, str(weight),
                    fontsize=9, fontweight='bold', color='#334155',
                    ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#cbd5e1", lw=1),
                    zorder=2
                )

    # Highlight Shortest Path Line
    if path and len(path) > 1:
        path_x = [LOCATIONS[node][0] for node in path]
        path_y = [LOCATIONS[node][1] for node in path]
        ax.plot(path_x, path_y, color='#2563eb', linewidth=5, alpha=0.85, label='Shortest Route', zorder=3)
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            x1, y1 = LOCATIONS[u]
            x2, y2 = LOCATIONS[v]
            ax.annotate(
                '', xy=((x1 + x2)/2, (y1 + y2)/2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#1d4ed8", lw=3, mutation_scale=16),
                zorder=4
            )

    # Draw Nodes (Buildings)
    for node, (x, y) in LOCATIONS.items():
        if node == start and node == goal:
            color = '#9333ea'
            prefix = "🟢🔴 "
        elif node == start:
            color = '#16a34a'  # Green Start
            prefix = "🟢 Start: "
        elif node == goal:
            color = '#dc2626'  # Red Goal
            prefix = "🔴 Goal: "
        else:
            color = '#475569'  # Slate Building
            prefix = ""

        ax.scatter(x, y, s=1100, color=color, zorder=5, edgecolors='#ffffff', linewidths=2.5)
        ax.text(
            x, y + 0.55, f"{prefix}{node}\n({x}, {y})",
            fontsize=9, fontweight='bold', color='#0f172a',
            ha='center', va='bottom',
            bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#e2e8f0", alpha=0.9),
            zorder=6
        )

    ax.set_title(f"Campus Map Route: {start} ➔ {goal}", fontsize=12, fontweight='bold', pad=12, color='#0f172a')
    ax.set_xlabel("X Coordinate", fontsize=9, color='#475569')
    ax.set_ylabel("Y Coordinate", fontsize=9, color='#475569')
    ax.grid(True, linestyle=':', alpha=0.5, color='#cbd5e1')

    all_x = [pos[0] for pos in LOCATIONS.values()]
    all_y = [pos[1] for pos in LOCATIONS.values()]
    ax.set_xlim(min(all_x) - 1.5, max(all_x) + 1.5)
    ax.set_ylim(min(all_y) - 1.2, max(all_y) + 2.0)

    legend_patches = [
        mpatches.Patch(color='#16a34a', label='Start Location'),
        mpatches.Patch(color='#dc2626', label='Destination Goal'),
        mpatches.Patch(color='#2563eb', label='Shortest Route Path'),
        mpatches.Patch(color='#475569', label='Campus Building')
    ]
    ax.legend(handles=legend_patches, loc='upper left', framealpha=0.9, fontsize=8)
    plt.tight_layout()
    return fig

# -----------------------------------------------------------------------------
# 3. INTERFACE CONTROLS & COMPUTATION
# -----------------------------------------------------------------------------
locations = get_available_locations()

col1, col2 = st.columns(2)
with col1:
    start_location = st.selectbox("Select Start Location:", options=locations, index=0)

with col2:
    goal_location = st.selectbox("Select Destination Location:", options=locations, index=3)

st.markdown("---")

if start_location == goal_location:
    st.warning("⚠️ Start and Destination locations are identical! Distance = 0 units.")
    fig = plot_campus_map(start_location, goal_location, path=[start_location])
    st.pyplot(fig)
else:
    # 1. Run Dijkstra's Algorithm
    t0_d = time.perf_counter()
    d_path, d_dist, d_nodes = dijkstra(CAMPUS_GRAPH, start_location, goal_location)
    d_time = (time.perf_counter() - t0_d) * 1000  # ms

    # 2. Run A* Search Algorithm
    heuristics = get_euclidean_heuristics(goal_location)
    t0_a = time.perf_counter()
    a_path, a_dist, a_nodes = a_star(CAMPUS_GRAPH, start_location, goal_location, heuristics)
    a_time = (time.perf_counter() - t0_a) * 1000  # ms

    # Display Map Graph
    st.markdown("### 🗺️ Campus Map Graph")
    fig = plot_campus_map(start_location, goal_location, path=a_path)
    st.pyplot(fig)

    st.markdown("---")

    # Display Comparison Table
    st.markdown("### 📊 Algorithm Comparison Table")

    d_route_str = " ➔ ".join(d_path) if d_path else "No path found"
    a_route_str = " ➔ ".join(a_path) if a_path else "No path found"

    table_data = [
        {
            "Algorithm": "Dijkstra's Algorithm (Uninformed)",
            "Optimal Route": d_route_str,
            "Total Distance": f"{d_dist:.2f} units",
            "Nodes Explored": d_nodes,
            "Execution Time": f"{d_time:.3f} ms"
        },
        {
            "Algorithm": "A* Search Algorithm (Informed)",
            "Optimal Route": a_route_str,
            "Total Distance": f"{a_dist:.2f} units",
            "Nodes Explored": a_nodes,
            "Execution Time": f"{a_time:.3f} ms"
        }
    ]

    df = pd.DataFrame(table_data)
    st.table(df)

    st.markdown("---")

    diff = d_nodes - a_nodes
    if diff > 0:
        st.success(f"💡 **Efficiency Result:** A* Search explored **{diff} fewer node(s)** than Dijkstra because of the Euclidean straight-line heuristic!")
    elif diff == 0:
        st.info("💡 **Efficiency Result:** Both algorithms explored an equal number of nodes for this route.")
    else:
        st.info(f"💡 **Efficiency Result:** Dijkstra expanded {-diff} fewer nodes.")
