"""
Independent Set Verifier
Checks if a selected subset of nodes forms an independent set
(no two nodes in the subset are adjacent).
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import time


# ==================================================
# CORE LOGIC
# ==================================================

def verify_independent_set(nodes, edges, candidate):
    """
    Verify if candidate is a valid independent set.
    Returns: (is_valid, violations, steps)
    steps follow the same structure as verifiers.py
    """
    steps = []
    violations = []

    candidate_set = set(candidate)
    all_edges = [tuple(sorted(e)) for e in edges]

    steps.append({
        "description": f"Verifying Independent Set: {sorted(candidate)} on graph with {len(nodes)} nodes, {len(all_edges)} edges",
        "nodes": nodes,
        "edges": all_edges,
        "candidate": list(candidate_set),
        "current_edge": None,
        "violations": [],
        "phase": "init"
    })

    for u, v in all_edges:
        both_in = u in candidate_set and v in candidate_set

        if both_in:
            violations.append({"edge": (u, v)})
            steps.append({
                "description": f"Edge ({u}, {v}): Both endpoints are in the candidate set - CONFLICT",
                "nodes": nodes,
                "edges": all_edges,
                "candidate": list(candidate_set),
                "current_edge": (u, v),
                "violations": violations.copy(),
                "phase": "violation"
            })
        else:
            steps.append({
                "description": f"Edge ({u}, {v}): At most one endpoint in candidate - OK",
                "nodes": nodes,
                "edges": all_edges,
                "candidate": list(candidate_set),
                "current_edge": (u, v),
                "violations": violations.copy(),
                "phase": "valid"
            })

    is_valid = len(violations) == 0
    final_msg = (
        f"Valid Independent Set of size {len(candidate)}!"
        if is_valid
        else f"Not an Independent Set: {len(violations)} conflict(s) found"
    )

    steps.append({
        "description": final_msg,
        "nodes": nodes,
        "edges": all_edges,
        "candidate": list(candidate_set),
        "current_edge": None,
        "violations": violations,
        "phase": "complete"
    })

    return is_valid, violations, steps


INDEPENDENT_SET_CODE = '''def verify_independent_set(graph, candidate):
    """Check that no two nodes in candidate are adjacent."""
    candidate_set = set(candidate)
    for node in candidate_set:
        for neighbor in graph.get(node, []):
            if neighbor in candidate_set:
                return False  # Two adjacent nodes in the set
    return True
'''


# ==================================================
# VISUALIZATION
# ==================================================

def render_is_step(step_data, pos, G):
    nodes = step_data["nodes"]
    edges = step_data["edges"]
    candidate = set(step_data["candidate"])
    current_edge = step_data.get("current_edge")
    violations = {tuple(v["edge"]) for v in step_data.get("violations", [])}
    phase = step_data["phase"]

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#FFFFFF")

    node_colors = []
    node_edgecolors = []
    for n in G.nodes():
        if n in candidate:
            node_colors.append("#C8E6C9")
            node_edgecolors.append("#388E3C")
        else:
            node_colors.append("#FFFFFF")
            node_edgecolors.append("#9E9E9E")

    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        key = tuple(sorted((u, v)))
        rev = (current_edge == (u, v) or current_edge == (v, u))
        if key in violations:
            edge_colors.append("#F44336")
            edge_widths.append(3.0)
        elif rev:
            edge_colors.append("#2196F3")
            edge_widths.append(2.5)
        else:
            edge_colors.append("#BDBDBD")
            edge_widths.append(1.0)

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           linewidths=2.5, edgecolors=node_edgecolors, node_size=500)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_weight="bold")

    legend = [
        mpatches.Patch(color="#C8E6C9", label="In candidate set"),
        mpatches.Patch(color="#FFFFFF", label="Not in set"),
        mpatches.Patch(color="#F44336", label="Conflict edge"),
        mpatches.Patch(color="#2196F3", label="Current edge"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=8, framealpha=0.9)

    phase_color = {"init": "#1565C0", "valid": "#2E7D32", "violation": "#C62828", "complete": "#6A1B9A"}
    ax.set_title(f"Phase: {phase.title()}  |  Violations: {len(violations)}", fontsize=10,
                 color=phase_color.get(phase, "#000000"), pad=10)
    ax.axis("off")
    plt.tight_layout()
    return fig


# ==================================================
# UI
# ==================================================

def init_is_state():
    if "is_nodes" not in st.session_state:
        st.session_state.is_nodes = ["A", "B", "C", "D", "E"]
        st.session_state.is_edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("A", "E")]
    if "is_candidate" not in st.session_state:
        st.session_state.is_candidate = ["A", "C"]
    if "is_steps" not in st.session_state:
        st.session_state.is_steps = []
    if "is_step_idx" not in st.session_state:
        st.session_state.is_step_idx = 0
    if "is_autoplay" not in st.session_state:
        st.session_state.is_autoplay = False


def render_independent_set():
    init_is_state()
    st.markdown("## Independent Set Verifier")

    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Create Graph", "Run Verifier", "Results"])

    with tab1:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.markdown("""
            ### Independent Set Problem

            An **Independent Set** is a subset of vertices in a graph such that
            no two vertices in the subset are connected by an edge.

            **Verification Steps:**
            1. Start with all edges in the graph.
            2. For each edge (u, v), check if both u and v are in the candidate set.
            3. If both are in the set, that is a conflict — the set is NOT independent.
            4. If no edge has both endpoints in the set, it is a valid Independent Set.

            **Relationship to other problems:**
            - Independent Set is NP-Complete.
            - It is equivalent to Vertex Cover: a set S is an independent set
              if and only if V \\ S is a vertex cover.
            """)
        with col2:
            st.info("""
            **Workflow:**
            1. Create Graph tab
            2. Select candidate nodes
            3. Run Verifier tab
            4. Results tab
            """)
            st.code(INDEPENDENT_SET_CODE, language="python")

    with tab2:
        col1, col2 = st.columns([4, 6])
        with col1:
            st.markdown("### Graph Builder")
            n_rand = st.slider("Nodes", 3, 20, 5, key="is_rand_n")
            prob = st.slider("Edge probability", 0.1, 0.7, 0.4, key="is_rand_p")
            if st.button("Generate Random Graph", use_container_width=True):
                import random
                chars = "ABCDEFGHIJKLMNOPQRST"
                G = nx.erdos_renyi_graph(n_rand, prob, seed=random.randint(0, 999))
                st.session_state.is_nodes = [chars[i] for i in G.nodes()]
                st.session_state.is_edges = [(chars[u], chars[v]) for u, v in G.edges()]
                st.session_state.is_candidate = []
                st.session_state.is_steps = []
                st.rerun()

            st.markdown("---")
            st.markdown("**Add Edge Manually**")
            cu, cv = st.columns(2)
            with cu:
                nu = st.text_input("Node 1", max_chars=1, key="is_nu").upper()
            with cv:
                nv = st.text_input("Node 2", max_chars=1, key="is_nv").upper()
            if st.button("Add Edge", use_container_width=True, disabled=not nu or not nv or nu == nv):
                edge = tuple(sorted((nu, nv)))
                if len(st.session_state.is_nodes) < 20:
                    if nu not in st.session_state.is_nodes:
                        st.session_state.is_nodes.append(nu)
                    if nv not in st.session_state.is_nodes:
                        st.session_state.is_nodes.append(nv)
                if edge not in st.session_state.is_edges:
                    st.session_state.is_edges.append(edge)
                st.session_state.is_steps = []
                st.rerun()

            st.markdown("---")
            st.markdown("**Select Candidate Set**")
            st.session_state.is_candidate = st.multiselect(
                "Nodes in candidate set",
                options=sorted(st.session_state.is_nodes),
                default=[n for n in st.session_state.is_candidate if n in st.session_state.is_nodes],
                key="is_candidate_sel"
            )

            if st.button("Clear Graph", use_container_width=True):
                st.session_state.is_nodes = []
                st.session_state.is_edges = []
                st.session_state.is_candidate = []
                st.session_state.is_steps = []
                st.rerun()

        with col2:
            st.markdown("### Graph Preview")
            if st.session_state.is_nodes:
                G = nx.Graph()
                G.add_nodes_from(st.session_state.is_nodes)
                G.add_edges_from(st.session_state.is_edges)
                pos = nx.spring_layout(G, seed=42)
                fig, ax = plt.subplots(figsize=(6, 4))
                fig.patch.set_facecolor("#F8F9FA")
                ax.set_facecolor("#FFFFFF")
                cands = set(st.session_state.is_candidate)
                colors = ["#C8E6C9" if n in cands else "#FFFFFF" for n in G.nodes()]
                nx.draw_networkx(G, pos, ax=ax, node_color=colors, edgecolors="#424242",
                                 linewidths=2, node_size=400, font_weight="bold")
                ax.axis("off")
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.warning("Graph is empty.")

    with tab3:
        if not st.session_state.is_edges:
            st.warning("Add edges in the Create Graph tab first.")
        elif not st.session_state.is_candidate:
            st.warning("Select at least one candidate node in the Create Graph tab.")
        else:
            col1, col2 = st.columns([3, 7])
            with col1:
                st.metric("Nodes", len(st.session_state.is_nodes))
                st.metric("Edges", len(st.session_state.is_edges))
                st.metric("Candidate Size", len(st.session_state.is_candidate))
            with col2:
                if not st.session_state.is_steps:
                    if st.button("Run Independent Set Verifier", type="primary", use_container_width=True):
                        _, _, steps = verify_independent_set(
                            st.session_state.is_nodes,
                            st.session_state.is_edges,
                            st.session_state.is_candidate
                        )
                        st.session_state.is_steps = steps
                        st.session_state.is_step_idx = 0
                        st.rerun()
                else:
                    final = st.session_state.is_steps[-1]
                    if final["phase"] == "complete" and not final["violations"]:
                        st.success(final["description"])
                    else:
                        st.error(final["description"])
                    if st.button("Run Again", use_container_width=True):
                        st.session_state.is_steps = []
                        st.rerun()

    with tab4:
        _render_results_panel(
            steps_key="is_steps",
            idx_key="is_step_idx",
            autoplay_key="is_autoplay",
            render_fn=lambda step: render_is_step(
                step,
                nx.spring_layout(nx.Graph([(u, v) for u, v in step["edges"]],
                                          nodes=step["nodes"]), seed=42),
                _build_graph(step["nodes"], step["edges"], directed=False)
            )
        )


# ==================================================
# SHARED RESULTS HELPER (used by all 5 verifiers)
# ==================================================

def _build_graph(nodes, edges, directed=False):
    G = nx.DiGraph() if directed else nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def _render_results_panel(steps_key, idx_key, autoplay_key, render_fn):
    steps = st.session_state.get(steps_key, [])
    if not steps:
        st.warning("Run the verifier first.")
        return

    total = len(steps)
    idx = st.session_state.get(idx_key, 0)
    idx = max(0, min(idx, total - 1))
    st.session_state[idx_key] = idx

    c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1, 1, 1, 1])
    with c1:
        if st.button("Autoplay", type="primary", use_container_width=True, key=f"ap_{steps_key}"):
            st.session_state[autoplay_key] = True
    with c2:
        speed = st.select_slider("Speed", [0.5, 1.0, 2.0, 3.0],
                                 value=1.0, format_func=lambda x: f"{x}s",
                                 label_visibility="collapsed", key=f"sp_{steps_key}")
    with c3:
        if st.button("First", use_container_width=True, disabled=idx == 0, key=f"f_{steps_key}"):
            st.session_state[idx_key] = 0; st.rerun()
    with c4:
        if st.button("Prev", use_container_width=True, disabled=idx == 0, key=f"pv_{steps_key}"):
            st.session_state[idx_key] = idx - 1; st.rerun()
    with c5:
        if st.button("Next", use_container_width=True, disabled=idx == total - 1, key=f"nx_{steps_key}"):
            st.session_state[idx_key] = idx + 1; st.rerun()
    with c6:
        if st.button("Last", use_container_width=True, disabled=idx == total - 1, key=f"l_{steps_key}"):
            st.session_state[idx_key] = total - 1; st.rerun()

    st.progress((idx + 1) / total, text=f"Step {idx + 1} of {total}")
    container = st.empty()

    def _draw(i):
        step = steps[i]
        with container.container():
            cg, ce = st.columns([7, 3])
            with cg:
                fig = render_fn(step)
                st.pyplot(fig)
                plt.close(fig)
            with ce:
                st.markdown(f"**Step {i + 1}/{total}**")
                phase = step.get("phase", "")
                phase_label = {"init": "Initialization", "valid": "Valid", "violation": "Violation", "complete": "Complete"}.get(phase, phase.title())
                color = {"init": "blue", "valid": "green", "violation": "red", "complete": "violet"}.get(phase, "gray")
                st.markdown(f"**Phase:** :{color}[{phase_label}]")
                st.markdown(f"""
                <div style="background:#F8F9FA;padding:15px;border-radius:5px;
                            border:1px solid #DEE2E6;font-size:14px;line-height:1.6;min-height:300px;">
                {step.get("description", "")}
                </div>""", unsafe_allow_html=True)

    if st.session_state.get(autoplay_key):
        st.session_state[autoplay_key] = False
        for i in range(idx, total):
            _draw(i)
            if i < total - 1:
                time.sleep(speed)
        st.session_state[idx_key] = total - 1
        st.rerun()
    else:
        _draw(idx)
