"""
Verifiers for Graph Problems:
1. K-Coloring Verifier
2. Clique Problem Verifier
3. Vertex Cover Verifier
4. Travelling Salesman Problem (TSP) Verifier
"""


# ==================================================
# K-COLORING VERIFIER
# ==================================================

def verify_k_coloring(graph, coloring, k):
    """
    Verify if a k-coloring is valid.
    Returns: (is_valid, violations, steps)
    """
    steps = []
    violations = []

    nodes = list(graph.keys())
    edges = []
    seen = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            edge = tuple(sorted([node, neighbor]))
            if edge not in seen:
                edges.append(edge)
                seen.add(edge)

    steps.append({
        "description": f"Verifying {k}-coloring for graph with {len(nodes)} nodes, {len(edges)} edges",
        "nodes": nodes,
        "edges": edges,
        "coloring": coloring.copy(),
        "current_edge": None,
        "violations": [],
        "phase": "init"
    })

    for u, v in edges:
        color_u = coloring.get(u, 0)
        color_v = coloring.get(v, 0)

        if color_u == color_v:
            violations.append({"edge": (u, v), "color": color_u})
            steps.append({
                "description": f"Edge ({u}, {v}): Both have color {color_u} - CONFLICT!",
                "nodes": nodes,
                "edges": edges,
                "coloring": coloring.copy(),
                "current_edge": (u, v),
                "violations": violations.copy(),
                "phase": "violation"
            })
        else:
            steps.append({
                "description": f"Edge ({u}, {v}): Colors {color_u} != {color_v} - OK",
                "nodes": nodes,
                "edges": edges,
                "coloring": coloring.copy(),
                "current_edge": (u, v),
                "violations": violations.copy(),
                "phase": "valid"
            })

    is_valid = len(violations) == 0
    final_msg = f"Valid {k}-coloring!" if is_valid else f"Invalid: {len(violations)} conflict(s)"

    steps.append({
        "description": final_msg,
        "nodes": nodes,
        "edges": edges,
        "coloring": coloring.copy(),
        "current_edge": None,
        "violations": violations,
        "phase": "complete"
    })

    return is_valid, violations, steps


# ==================================================
# CLIQUE VERIFIER
# ==================================================

def verify_clique(graph, clique_nodes):
    """
    Verify if a subset of nodes forms a clique.
    A clique is a subset where every two nodes are connected.
    """
    steps = []
    violations = []

    nodes = list(graph.keys())

    steps.append({
        "description": f"Verifying if {clique_nodes} forms a clique",
        "nodes": nodes,
        "clique_nodes": clique_nodes,
        "current_pair": None,
        "violations": [],
        "checked_pairs": [],
        "phase": "init"
    })

    checked_pairs = []
    for i in range(len(clique_nodes)):
        for j in range(i + 1, len(clique_nodes)):
            u, v = clique_nodes[i], clique_nodes[j]

            is_connected = v in graph.get(u, [])
            checked_pairs.append((u, v))

            if not is_connected:
                violations.append({"pair": (u, v)})
                steps.append({
                    "description": f"Nodes {u} and {v} are NOT connected - not a clique!",
                    "nodes": nodes,
                    "clique_nodes": clique_nodes,
                    "current_pair": (u, v),
                    "violations": violations.copy(),
                    "checked_pairs": checked_pairs.copy(),
                    "phase": "violation"
                })
            else:
                steps.append({
                    "description": f"Nodes {u} and {v} are connected",
                    "nodes": nodes,
                    "clique_nodes": clique_nodes,
                    "current_pair": (u, v),
                    "violations": violations.copy(),
                    "checked_pairs": checked_pairs.copy(),
                    "phase": "valid"
                })

    is_valid = len(violations) == 0
    final_msg = f"Valid clique of size {len(clique_nodes)}!" if is_valid else "Not a clique"

    steps.append({
        "description": final_msg,
        "nodes": nodes,
        "clique_nodes": clique_nodes,
        "current_pair": None,
        "violations": violations,
        "checked_pairs": checked_pairs,
        "phase": "complete"
    })

    return is_valid, violations, steps


# ==================================================
# VERTEX COVER VERIFIER
# ==================================================

def verify_vertex_cover(graph, cover_nodes):
    """
    Verify if a subset of nodes is a valid vertex cover.
    A vertex cover must contain at least one endpoint of every edge.
    """
    steps = []
    uncovered_edges = []

    nodes = list(graph.keys())
    edges = []
    seen = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            edge = tuple(sorted([node, neighbor]))
            if edge not in seen:
                edges.append(edge)
                seen.add(edge)

    cover_set = set(cover_nodes)

    steps.append({
        "description": f"Verifying if {list(cover_nodes)} is a vertex cover for {len(edges)} edges",
        "nodes": nodes,
        "edges": edges,
        "cover_nodes": list(cover_nodes),
        "current_edge": None,
        "uncovered": [],
        "phase": "init"
    })

    for u, v in edges:
        is_covered = u in cover_set or v in cover_set

        if not is_covered:
            uncovered_edges.append((u, v))
            steps.append({
                "description": f"Edge ({u}, {v}): Neither endpoint in cover!",
                "nodes": nodes,
                "edges": edges,
                "cover_nodes": list(cover_nodes),
                "current_edge": (u, v),
                "uncovered": uncovered_edges.copy(),
                "phase": "violation"
            })
        else:
            covered_by = u if u in cover_set else v
            steps.append({
                "description": f"Edge ({u}, {v}): Covered by node '{covered_by}'",
                "nodes": nodes,
                "edges": edges,
                "cover_nodes": list(cover_nodes),
                "current_edge": (u, v),
                "uncovered": uncovered_edges.copy(),
                "phase": "valid"
            })

    is_valid = len(uncovered_edges) == 0
    final_msg = f"Valid vertex cover of size {len(cover_nodes)}!" if is_valid else "Not a vertex cover"

    steps.append({
        "description": final_msg,
        "nodes": nodes,
        "edges": edges,
        "cover_nodes": list(cover_nodes),
        "current_edge": None,
        "uncovered": uncovered_edges,
        "phase": "complete"
    })

    return is_valid, uncovered_edges, steps


# ==================================================
# TSP VERIFIER
# ==================================================

def verify_tsp(graph, tour, max_cost=None):
    """
    Verify if a tour is valid for TSP.
    A valid tour visits every city exactly once and returns to start.
    graph: dict of { node: [(neighbor, weight), ...] }
    """
    steps = []
    violations = []

    nodes = list(graph.keys())

    steps.append({
        "description": f"Verifying TSP tour: {' -> '.join(str(c) for c in tour)}",
        "nodes": nodes,
        "tour": tour,
        "current_edge": None,
        "total_cost": 0,
        "violations": [],
        "phase": "init"
    })

    # Check all cities visited exactly once
    if set(tour[:-1]) != set(nodes):
        missing = set(nodes) - set(tour)
        extra = set(tour) - set(nodes)
        violations.append({"type": "cities", "missing": missing, "extra": extra})
        steps.append({
            "description": "Tour doesn't visit all cities exactly once",
            "nodes": nodes,
            "tour": tour,
            "current_edge": None,
            "total_cost": 0,
            "violations": violations.copy(),
            "phase": "violation"
        })

    # Check tour returns to start
    if len(tour) > 0 and tour[0] != tour[-1]:
        violations.append({"type": "not_cycle"})
        steps.append({
            "description": "Tour doesn't return to starting city",
            "nodes": nodes,
            "tour": tour,
            "current_edge": None,
            "total_cost": 0,
            "violations": violations.copy(),
            "phase": "violation"
        })

    # Calculate total cost
    total_cost = 0
    for i in range(len(tour) - 1):
        u, v = tour[i], tour[i + 1]

        edge_cost = None
        for neighbor, weight in graph.get(u, []):
            if neighbor == v:
                edge_cost = weight
                break

        if edge_cost is None:
            violations.append({"type": "no_edge", "edge": (u, v)})
            steps.append({
                "description": f"No edge between {u} and {v}!",
                "nodes": nodes,
                "tour": tour,
                "current_edge": (u, v),
                "total_cost": total_cost,
                "violations": violations.copy(),
                "phase": "violation"
            })
        else:
            total_cost += edge_cost
            steps.append({
                "description": f"Edge {u} -> {v}: Cost {edge_cost:.2f}, Running Total: {total_cost:.2f}",
                "nodes": nodes,
                "tour": tour,
                "current_edge": (u, v),
                "total_cost": total_cost,
                "violations": violations.copy(),
                "phase": "valid"
            })

    is_valid = len(violations) == 0
    if max_cost and total_cost > max_cost:
        is_valid = False
        violations.append({"type": "cost", "total": total_cost, "max": max_cost})

    final_msg = f"Valid tour! Total cost: {total_cost:.2f}" if is_valid else "Invalid tour"

    steps.append({
        "description": final_msg,
        "nodes": nodes,
        "tour": tour,
        "current_edge": None,
        "total_cost": total_cost,
        "violations": violations,
        "phase": "complete"
    })

    return is_valid, total_cost, violations, steps


# ==================================================
# CODE STRINGS (for display in UI)
# ==================================================

K_COLORING_CODE = '''def verify_k_coloring(graph, coloring, k):
    """Check if no adjacent vertices share the same color."""
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if coloring[node] == coloring[neighbor]:
                return False  # Adjacent nodes have same color
    return True
'''

CLIQUE_CODE = '''def verify_clique(graph, clique_nodes):
    """Check if every pair of nodes in subset is connected."""
    for i in range(len(clique_nodes)):
        for j in range(i + 1, len(clique_nodes)):
            u, v = clique_nodes[i], clique_nodes[j]
            if v not in graph[u]:
                return False  # Missing edge
    return True
'''

VERTEX_COVER_CODE = '''def verify_vertex_cover(graph, cover_nodes):
    """Check if at least one endpoint of every edge is in cover."""
    cover_set = set(cover_nodes)
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            if node not in cover_set and neighbor not in cover_set:
                return False  # Edge not covered
    return True
'''

TSP_CODE = '''def verify_tsp(graph, tour):
    """Check if tour visits all cities exactly once and returns to start."""
    nodes = set(graph.keys())

    # Must visit all cities
    if set(tour[:-1]) != nodes:
        return False

    # Must return to start
    if tour[0] != tour[-1]:
        return False

    # All edges must exist
    for i in range(len(tour) - 1):
        if tour[i+1] not in graph[tour[i]]:
            return False

    return True
'''
