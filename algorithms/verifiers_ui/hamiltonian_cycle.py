"""
Hamiltonian Cycle Verifier
Checks if a proposed tour is a valid Hamiltonian Cycle.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import time

from .independent_set import _build_graph, _render_results_panel


# ==================================================
# CORE LOGIC
# ==================================================

def verify_hamiltonian_cycle(nodes, edges, proposed_tour):
    """
    Verify if proposed_tour is a valid Hamiltonian Cycle.
    proposed_tour: list of node names, e.g. ["A","B","C","A"]
    Returns: (is_valid, violations, steps)
    """
    steps = []
    violations = []

    edge_set = set(tuple(sorted(e)) for e in edges)
    node_set = set(nodes)

    steps.append({
        "description": f"Verifying Hamiltonian Cycle: {' -> '.join(proposed_tour)}",
        "nodes": nodes,
        "edges": list(edge_set),
        "tour": proposed_tour,
        "current_edge": None,
        "highlighted_nodes": [],
        "violations": [],
        "phase": "init"
    })

    # Check starts and ends at same node
    if len(proposed_tour) < 2 or proposed_tour[0] != proposed_tour[-1]:
        violations.append({"type": "not_cycle", "detail": "Tour does not start and end at the same node"})
        steps.append({
            "description": "Tour does not start and end at the same node - not a cycle",
            "nodes": nodes,
            "edges": list(edge_set),
            "tour": proposed_tour,
            "current_edge": None,
            "highlighted_nodes": [],
            "violations": violations.copy(),
            "phase": "violation"
        })

    # Check all nodes visited exactly once (excluding repeated start)
    visited = proposed_tour[:-1] if proposed_tour and proposed_tour[0] == proposed_tour[-1] else proposed_tour
    missing = node_set - set(visited)
    duplicates = [n for n in visited if visited.count(n) > 1]

    if missing:
        violations.append({"type": "missing_nodes", "nodes": list(missing)})
        steps.append({
            "description": f"Nodes not visited: {sorted(missing)} - not a Hamiltonian Cycle",
            "nodes": nodes,
            "edges": list(edge_set),
            "tour": proposed_tour,
            "current_edge": None,
            "highlighted_nodes": list(missing),
            "violations": violations.copy(),
            "phase": "violation"
        })
    elif duplicates:
        violations.append({"type": "duplicates", "nodes": list(set(duplicates))})
        steps.append({
            "description": f"Nodes visited more than once: {sorted(set(duplicates))} - not a Hamiltonian Cycle",
            "nodes": nodes,
            "edges": list(edge_set),
            "tour": proposed_tour,
            "current_edge": None,
            "highlighted_nodes": list(set(duplicates)),
            "violations": violations.copy(),
            "phase": "violation"
        })
    else:
        steps.append({
            "description": f"All {len(nodes)} nodes are visited exactly once",
            "nodes": nodes,
            "edges": list(edge_set),
            "tour": proposed_tour,
            "current_edge": None,
            "highlighted_nodes": list(visited),
            "violations": violations.copy(),
            "phase": "valid"
        })

    # Check each consecutive edge exists
    tour_edges_used = []
    for i in range(len(proposed_tour) - 1):
        u, v = proposed_tour[i], proposed_tour[i + 1]
        e = tuple(sorted((u, v)))
        tour_edges_used.append(e)

        if e not in edge_set:
            violations.append({"type": "missing_edge", "edge": (u, v)})
            steps.append({
                "description": f"Edge ({u}, {v}) does not exist in the graph",
                "nodes": nodes,
                "edges": list(edge_set),
                "tour": proposed_tour,
                "current_edge": (u, v),
                "highlighted_nodes": [],
                "violations": violations.copy(),
                "phase": "violation"
            })
        else:
            steps.append({
                "description": f"Edge ({u}, {v}) exists in the graph - OK",
                "nodes": nodes,
                "edges": list(edge_set),
                "tour": proposed_tour,
                "current_edge": (u, v),
                "highlighted_nodes": [],
                "violations": violations.copy(),
                "phase": "valid"
            })

    is_valid = len(violations) == 0
    final_msg = (
        f"Valid Hamiltonian Cycle of length {len(proposed_tour) - 1}!"
        if is_valid
        else f"Invalid Hamiltonian Cycle: {len(violations)} issue(s) found"
    )

    steps.append({
        "description": final_msg,
        "nodes": nodes,
        "edges": list(edge_set),
        "tour": proposed_tour,
        "current_edge": None,
        "highlighted_nodes": [],
        "violations": violations,
        "phase": "complete"
    })

    return is_valid, violations, steps


HAMILTONIAN_CODE = '''def verify_hamiltonian_cycle(graph, tour):
    """Check if tour is a valid Hamiltonian Cycle."""
    nodes = set(graph.keys())

    # Must return to start
    if tour[0] != tour[-1]:
        return False

    visited = tour[:-1]

    # Must visit every node exactly once
    if set(visited) != nodes or len(visited) != len(nodes):
        return False

    # Every consecutive pair must be connected
    for i in range(len(tour) - 1):
        if tour[i+1] not in graph[tour[i]]:
            return False

    return True
'''


# ==================================================
# VISUALIZATION
# ==================================================

def render_ham_step(step_data, pos, G):
    nodes = step_data["nodes"]
    edges = step_data["edges"]
    tour = step_data["tour"]
    current_edge = step_data.get("current_edge")
    highlighted_nodes = set(step_data.get("highlighted_nodes", []))
    violations = step_data.get("violations", [])
    phase = step_data["phase"]

    # Build set of tour edges up to current
    tour_edges = set()
    if current_edge:
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i + 1]
            e = tuple(sorted((u, v)))
            tour_edges.add(e)
            if (u, v) == current_edge or (v, u) == current_edge:
                break

    bad_edges = {tuple(sorted(v["edge"])) for v in violations if v.get("type") == "missing_edge"}

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#FFFFFF")

    edge_colors, edge_widths = [], []
    for u, v in G.edges():
        e = tuple(sorted((u, v)))
        is_cur = (current_edge and tuple(sorted(current_edge)) == e)
        if is_cur and e in bad_edges:
            edge_colors.append("#EF5350"); edge_widths.append(3.0)
        elif is_cur:
            edge_colors.append("#2196F3"); edge_widths.append(3.0)
        elif e in tour_edges:
            edge_colors.append("#43A047"); edge_widths.append(2.5)
        else:
            edge_colors.append("#BDBDBD"); edge_widths.append(1.0)

    node_colors, node_ec = [], []
    for n in G.nodes():
        if n in highlighted_nodes:
            node_colors.append("#FFE082"); node_ec.append("#F57F17")
        else:
            node_colors.append("#FFFFFF"); node_ec.append("#616161")

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           edgecolors=node_ec, linewidths=2.5, node_size=500)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_weight="bold")

    legend = [
        mpatches.Patch(color="#43A047", label="Tour edge (OK)"),
        mpatches.Patch(color="#2196F3", label="Current edge"),
        mpatches.Patch(color="#EF5350", label="Missing edge"),
        mpatches.Patch(color="#FFE082", label="Problem node"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=8, framealpha=0.9)
    ax.axis("off")
    plt.tight_layout()
    return fig


# ==================================================
# UI
# ==================================================

def init_ham_state():
    if "ham_nodes" not in st.session_state:
        st.session_state.ham_nodes = ["A", "B", "C", "D", "E"]
        st.session_state.ham_edges = [("A","B"),("B","C"),("C","D"),("D","E"),("E","A"),("A","C")]
    if "ham_tour" not in st.session_state:
        st.session_state.ham_tour = "A, B, C, D, E, A"
    if "ham_steps" not in st.session_state:
        st.session_state.ham_steps = []
    if "ham_step_idx" not in st.session_state:
        st.session_state.ham_step_idx = 0
    if "ham_autoplay" not in st.session_state:
        st.session_state.ham_autoplay = False


def render_hamiltonian_cycle():
    init_ham_state()
    st.markdown("## Hamiltonian Cycle Verifier")

    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Create Graph", "Run Verifier", "Results"])

    with tab1:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.markdown("""
            ### Hamiltonian Cycle Problem

            A **Hamiltonian Cycle** is a closed path in a graph that visits every vertex
            exactly once and returns to the starting vertex.

            **Verification Steps:**
            1. Confirm the tour starts and ends at the same node.
            2. Confirm every node in the graph appears exactly once in the tour.
            3. Confirm every consecutive pair in the tour is connected by an edge.

            **Complexity:**
            - Verifying a proposed tour is **O(n)** — trivially easy.
            - Finding a Hamiltonian Cycle is NP-Complete.
            """)
        with col2:
            st.info("""
            **Workflow:**
            1. Create Graph tab
            2. Enter proposed tour
            3. Run Verifier tab
            4. Results tab
            """)
            st.code(HAMILTONIAN_CODE, language="python")

    with tab2:
        col1, col2 = st.columns([4, 6])
        with col1:
            st.markdown("### Graph Builder")
            import random
            n_rand = st.slider("Nodes", 3, 20, 5, key="ham_rand_n")
            prob = st.slider("Edge probability", 0.2, 0.9, 0.5, key="ham_rand_p")
            if st.button("Generate Random Graph", use_container_width=True):
                chars = "ABCDEFGHIJKLMNOPQRST"
                G = nx.erdos_renyi_graph(n_rand, prob, seed=random.randint(0, 999))
                st.session_state.ham_nodes = [chars[i] for i in G.nodes()]
                st.session_state.ham_edges = [(chars[u], chars[v]) for u, v in G.edges()]
                st.session_state.ham_steps = []
                st.rerun()

            st.markdown("---")
            st.markdown("**Add Edge**")
            cu, cv = st.columns(2)
            with cu: nu = st.text_input("Node 1", max_chars=1, key="ham_nu").upper()
            with cv: nv = st.text_input("Node 2", max_chars=1, key="ham_nv").upper()
            if st.button("Add Edge", use_container_width=True, disabled=not nu or not nv or nu == nv):
                edge = tuple(sorted((nu, nv)))
                if len(st.session_state.ham_nodes) < 20:
                    if nu not in st.session_state.ham_nodes: st.session_state.ham_nodes.append(nu)
                    if nv not in st.session_state.ham_nodes: st.session_state.ham_nodes.append(nv)
                if edge not in st.session_state.ham_edges:
                    st.session_state.ham_edges.append(edge)
                st.session_state.ham_steps = []
                st.rerun()

            st.markdown("---")
            st.markdown("**Proposed Tour**")
            st.caption("Enter node names separated by commas. Must start and end at same node.")
            tour_text = st.text_input("Tour", value=st.session_state.ham_tour, key="ham_tour_input")
            st.session_state.ham_tour = tour_text

            if st.button("Clear Graph", use_container_width=True):
                st.session_state.ham_nodes = []
                st.session_state.ham_edges = []
                st.session_state.ham_steps = []
                st.rerun()

        with col2:
            st.markdown("### Graph Preview")
            if st.session_state.ham_nodes:
                G = _build_graph(st.session_state.ham_nodes, st.session_state.ham_edges, directed=False)
                pos = nx.spring_layout(G, seed=42)
                fig, ax = plt.subplots(figsize=(6, 4))
                fig.patch.set_facecolor("#F8F9FA")
                ax.set_facecolor("#FFFFFF")
                nx.draw_networkx(G, pos, ax=ax, node_color="#FFFFFF", edgecolors="#424242",
                                 linewidths=2, node_size=400, font_weight="bold")
                ax.axis("off")
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.warning("Graph is empty.")

    with tab3:
        col1, col2 = st.columns([3, 7])
        with col1:
            st.metric("Nodes", len(st.session_state.ham_nodes))
            st.metric("Edges", len(st.session_state.ham_edges))
        with col2:
            if not st.session_state.ham_steps:
                if st.button("Run Hamiltonian Cycle Verifier", type="primary", use_container_width=True):
                    tour = [t.strip() for t in st.session_state.ham_tour.split(",") if t.strip()]
                    _, _, steps = verify_hamiltonian_cycle(
                        st.session_state.ham_nodes,
                        st.session_state.ham_edges,
                        tour
                    )
                    st.session_state.ham_steps = steps
                    st.session_state.ham_step_idx = 0
                    st.rerun()
            else:
                final = st.session_state.ham_steps[-1]
                if not final["violations"]:
                    st.success(final["description"])
                else:
                    st.error(final["description"])
                if st.button("Run Again", use_container_width=True):
                    st.session_state.ham_steps = []
                    st.rerun()

    with tab4:
        G_ref = _build_graph(st.session_state.ham_nodes, st.session_state.ham_edges, directed=False)
        pos_ref = nx.spring_layout(G_ref, seed=42)
        _render_results_panel(
            steps_key="ham_steps",
            idx_key="ham_step_idx",
            autoplay_key="ham_autoplay",
            render_fn=lambda step: render_ham_step(step, pos_ref, G_ref)
        )
