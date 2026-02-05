"""
Ford-Fulkerson Algorithm Visualizer - Single Screen Horizontal Tabs
Complete with all 3 input methods
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, deque
import copy
import time

# Import from separated modules
from .ff_core import (
    FordFulkersonAlgorithm,
    GraphBuilder,
    GraphValidator,
    ExampleGraphs
)
from .ff_visualization import GraphRenderer, GraphLayout


# ============================================================================
# SESSION STATE
# ============================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    
    if 'ff_graph' not in st.session_state:
        st.session_state.ff_graph = None
    if 'ff_initial_flow' not in st.session_state:
        st.session_state.ff_initial_flow = None
    if 'ff_source' not in st.session_state:
        st.session_state.ff_source = None
    if 'ff_sink' not in st.session_state:
        st.session_state.ff_sink = None
    if 'ff_steps_history' not in st.session_state:
        st.session_state.ff_steps_history = []
    if 'ff_current_step' not in st.session_state:
        st.session_state.ff_current_step = 0
    if 'ff_max_flow_value' not in st.session_state:
        st.session_state.ff_max_flow_value = 0
    if 'ff_graph_built' not in st.session_state:
        st.session_state.ff_graph_built = False


# ============================================================================
# TAB 1: INTRODUCTION
# ============================================================================

def render_introduction_tab():
    """Render introduction - fits on one screen"""
    
    col1, col2 = st.columns([7, 3])
    
    with col1:
        st.markdown("""
        ### Maximum Flow & Minimum Cut Algorithm
        
        The Ford-Fulkerson algorithm finds the maximum flow in a flow network.
        
        **Key Concepts:**
        - **Flow Network**: Directed graph with edge capacities
        - **Source (s)**: Starting node where flow originates
        - **Sink (t)**: Ending node where flow terminates
        - **Capacity**: Maximum flow allowed on each edge
        - **Maximum Flow**: Largest amount from source to sink
        
        **Algorithm Steps:**
        1. Start with zero flow on all edges
        2. Find an augmenting path from source to sink
        3. Compute bottleneck (minimum capacity along path)
        4. Add bottleneck flow to all edges in path
        5. Repeat until no augmenting path exists
        
        **Max-Flow Min-Cut Theorem:**  
        The maximum flow equals the capacity of the minimum cut.
        """)
    
    with col2:
        st.info("""
        **How to Use:**
        
        1. **Create Graph** tab  
           Choose input method
        
        2. **Run Algorithm** tab  
           Execute Ford-Fulkerson
        
        3. **Results** tab  
           View step-by-step
        """)
        
        st.success("""
        **Features:**
        - 3 input methods
        - Step-by-step viz
        - Auto-play mode
        - Min-cut display
        """)


# ============================================================================
# TAB 2: CREATE GRAPH
# ============================================================================

def render_create_graph_tab():
    """Render graph creation with horizontal sub-tabs"""
    
    subtab1, subtab2, subtab3 = st.tabs([
        "📚 Load Example",
        "🎨 Visual Editor",
        "🎯 Build from Scratch"
    ])
    
    with subtab1:
        render_load_example_compact()
    
    with subtab2:
        render_visual_editor_compact()
    
    with subtab3:
        render_build_scratch_compact()


def render_load_example_compact():
    """Load example - 2 columns"""
    
    examples = ExampleGraphs.get_all()
    example_names = list(examples.keys())
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected = st.selectbox("Choose example:", example_names, key="example_selector")
        example_data = examples[selected]
        
        st.info(example_data['description'])
        st.markdown(f"""
        - **Nodes:** {len(example_data['nodes'])}
        - **Edges:** {len(example_data['edges'])}
        - **Source:** {example_data['source']}
        - **Sink:** {example_data['sink']}
        """)
        
        if example_data.get('expected_max_flow'):
            st.markdown(f"- **Expected Max Flow:** {example_data['expected_max_flow']}")
        
        if st.button("📥 Load This Graph", type="primary", use_container_width=True, key="load_example"):
            is_valid, message = GraphValidator.validate(example_data)
            if not is_valid:
                st.error(message)
                return
            
            graph, initial_flow = GraphBuilder.from_edges(example_data['edges'])
            st.session_state.ff_graph = graph
            st.session_state.ff_initial_flow = initial_flow
            st.session_state.ff_source = example_data['source']
            st.session_state.ff_sink = example_data['sink']
            st.session_state.ff_graph_built = True
            st.session_state.ff_steps_history = []
            st.success("✅ Graph loaded! Go to 'Run Algorithm' tab.")
            st.rerun()
    
    with col2:
        st.markdown("**Graph Preview:**")
        
        graph_dict = {}
        for edge in example_data['edges']:
            if len(edge) == 3:
                u, v, cap = edge
            else:
                u, v, cap, flow = edge
            if u not in graph_dict:
                graph_dict[u] = {}
            graph_dict[u][v] = cap
        
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#F5F5F5')
        ax.set_facecolor('#FFFFFF')
        
        G = nx.DiGraph()
        for node in example_data['nodes']:
            G.add_node(node)
        for edge in example_data['edges']:
            if len(edge) == 3:
                u, v, cap = edge
            else:
                u, v, cap, flow = edge
            G.add_edge(u, v)
        
        pos = GraphLayout.hierarchical(graph_dict, example_data['source'], example_data['sink'])
        
        node_colors = []
        for node in G.nodes():
            if node == example_data['source']:
                node_colors.append('#90EE90')
            elif node == example_data['sink']:
                node_colors.append('#FFB6C1')
            else:
                node_colors.append('#FFFFFF')
        
        for edge in example_data['edges']:
            if len(edge) == 3:
                u, v, cap = edge
            else:
                u, v, cap, flow = edge
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color='black', lw=1.5, shrinkA=15, shrinkB=15))
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, ax=ax,
                              edgecolors='black', linewidths=2)
        nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', ax=ax)
        
        for edge in example_data['edges']:
            if len(edge) == 3:
                u, v, cap = edge
            else:
                u, v, cap, flow = edge
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            label_x = x1 + 0.25 * (x2 - x1)
            label_y = y1 + 0.25 * (y2 - y1)
            dx = x2 - x1
            dy = y2 - y1
            length = (dx**2 + dy**2)**0.5
            if length > 0:
                offset_x = -dy / length * 0.1
                offset_y = dx / length * 0.1
            else:
                offset_x, offset_y = 0.05, 0.05
            label_x += offset_x
            label_y += offset_y
            bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='gray', linewidth=1)
            ax.text(label_x, label_y, f"{cap}", fontsize=8, ha='center', va='center',
                   bbox=bbox_props, zorder=1000)
        
        ax.axis('off')
        ax.margins(0.15)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


def render_visual_editor_compact():
    """Visual editor - load and edit"""
    
    examples = ExampleGraphs.get_all()
    example_names = list(examples.keys())
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("Choose graph to edit:", example_names, key="edit_selector")
    with col2:
        if st.button("📥 Load", type="primary", use_container_width=True):
            example_data = examples[selected]
            st.session_state.ff_edit_nodes = example_data['nodes'].copy()
            st.session_state.ff_edit_edges = []
            for edge in example_data['edges']:
                if len(edge) == 3:
                    st.session_state.ff_edit_edges.append([edge[0], edge[1], edge[2], 0])
                else:
                    st.session_state.ff_edit_edges.append([edge[0], edge[1], edge[2], edge[3]])
            st.session_state.ff_edit_source = example_data['source']
            st.session_state.ff_edit_sink = example_data['sink']
            st.success("✅ Loaded!")
            st.rerun()
    
    if 'ff_edit_edges' not in st.session_state:
        st.info("👆 Load an example to start editing")
        return
    
    # Graph preview
    graph_dict = {}
    for u, v, cap, flow in st.session_state.ff_edit_edges:
        if u not in graph_dict:
            graph_dict[u] = {}
        graph_dict[u][v] = cap
    
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#F5F5F5')
    ax.set_facecolor('#FFFFFF')
    G = nx.DiGraph()
    for node in st.session_state.ff_edit_nodes:
        G.add_node(node)
    for u, v, cap, flow in st.session_state.ff_edit_edges:
        G.add_edge(u, v)
    pos = GraphLayout.hierarchical(graph_dict, st.session_state.ff_edit_source, st.session_state.ff_edit_sink)
    node_colors = []
    for node in G.nodes():
        if node == st.session_state.ff_edit_source:
            node_colors.append('#90EE90')
        elif node == st.session_state.ff_edit_sink:
            node_colors.append('#FFB6C1')
        else:
            node_colors.append('#FFFFFF')
    for u, v, cap, flow in st.session_state.ff_edit_edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.5, shrinkA=15, shrinkB=15))
        label_x = x1 + 0.25 * (x2 - x1)
        label_y = y1 + 0.25 * (y2 - y1)
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            offset_x = -dy / length * 0.1
            offset_y = dx / length * 0.1
        else:
            offset_x, offset_y = 0.05, 0.05
        label_x += offset_x
        label_y += offset_y
        ax.text(label_x, label_y, f"{cap}", fontsize=8, ha='center', va='center',
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='gray', linewidth=1), zorder=1000)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1200, ax=ax, edgecolors='black', linewidths=2)
    nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold', ax=ax)
    ax.axis('off')
    ax.margins(0.15)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    
    st.markdown("---")
    st.markdown("### Edit Capacities")
    
    for idx, edge in enumerate(st.session_state.ff_edit_edges):
        u, v, cap, flow = edge
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        with col1:
            st.write(f"**{u} → {v}**")
        with col2:
            new_cap = st.number_input("Cap", min_value=1, max_value=100, value=cap,
                                     key=f"edit_cap_{idx}", label_visibility="collapsed")
            if new_cap != cap:
                st.session_state.ff_edit_edges[idx][2] = new_cap
                st.rerun()
        with col3:
            st.text("(flow = 0)")
        with col4:
            if st.button("🗑️", key=f"del_edit_{idx}"):
                st.session_state.ff_edit_edges.pop(idx)
                st.rerun()
    
    st.markdown("**Add Edge:**")
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        new_from = st.selectbox("From", st.session_state.ff_edit_nodes, key="edit_from")
    with col2:
        new_to = st.selectbox("To", st.session_state.ff_edit_nodes, key="edit_to")
    with col3:
        new_cap = st.number_input("Capacity", min_value=1, value=10, key="edit_cap")
    with col4:
        if st.button("➕"):
            if new_from != new_to:
                exists = any((e[0] == new_from and e[1] == new_to) for e in st.session_state.ff_edit_edges)
                if not exists:
                    st.session_state.ff_edit_edges.append([new_from, new_to, new_cap, 0])
                    st.rerun()
    
    if st.button("✅ Apply & Use Graph", type="primary", use_container_width=True):
        graph_data = {
            "nodes": st.session_state.ff_edit_nodes,
            "edges": [tuple(e) for e in st.session_state.ff_edit_edges],
            "source": st.session_state.ff_edit_source,
            "sink": st.session_state.ff_edit_sink
        }
        is_valid, message = GraphValidator.validate(graph_data)
        if is_valid:
            graph, initial_flow = GraphBuilder.from_edges(graph_data['edges'])
            st.session_state.ff_graph = graph
            st.session_state.ff_initial_flow = initial_flow
            st.session_state.ff_source = st.session_state.ff_edit_source
            st.session_state.ff_sink = st.session_state.ff_edit_sink
            st.session_state.ff_graph_built = True
            st.session_state.ff_steps_history = []
            st.success("✅ Graph ready! Go to 'Run Algorithm' tab.")
            st.rerun()
        else:
            st.error(message)



def render_build_scratch_compact():
    """Build from scratch - compact single-screen layout"""
    
    # Initialize with s and t by default
    if 'scratch_nodes' not in st.session_state:
        st.session_state.scratch_nodes = ['s', 't']
    if 'scratch_edges' not in st.session_state:
        st.session_state.scratch_edges = []  # (u, v, capacity)
    if 'scratch_edge_history' not in st.session_state:
        st.session_state.scratch_edge_history = []
    
    # Helper functions
    def edge_exists(u, v):
        for (a, b, c) in st.session_state.scratch_edges:
            if a == u and b == v:
                return True
        return False
    
    def update_edge(u, v, cap):
        new_edges = []
        for (a, b, c) in st.session_state.scratch_edges:
            if a == u and b == v:
                new_edges.append((a, b, cap))
            else:
                new_edges.append((a, b, c))
        st.session_state.scratch_edges = new_edges
    
    # THREE COLUMNS: Controls | Graph | Edges
    col_controls, col_graph, col_edges = st.columns([1, 2, 1])
    
    # ========================================================================
    # LEFT COLUMN: NODE & EDGE CONTROLS
    # ========================================================================
    with col_controls:
        # Nodes Section
        st.markdown("**Nodes** " + f"({len(st.session_state.scratch_nodes)}/10)")
        col_add, col_del = st.columns(2)
        with col_add:
            if st.button("➕", use_container_width=True, key="add_node_btn",
                        disabled=(len(st.session_state.scratch_nodes) >= 10)):
                for letter in 'abcdefgh':
                    if letter not in st.session_state.scratch_nodes:
                        st.session_state.scratch_nodes.append(letter)
                        break
                st.rerun()
        with col_del:
            if st.button("➖", use_container_width=True, key="del_node_btn",
                        disabled=(len(st.session_state.scratch_nodes) <= 2)):
                for node in reversed(st.session_state.scratch_nodes):
                    if node not in ['s', 't']:
                        st.session_state.scratch_nodes.remove(node)
                        st.session_state.scratch_edges = [
                            (u, v, c) for u, v, c in st.session_state.scratch_edges
                            if u != node and v != node
                        ]
                        st.session_state.scratch_edge_history = [
                            (u, v, c) for u, v, c in st.session_state.scratch_edge_history
                            if u != node and v != node
                        ]
                        break
                st.rerun()
        
        # Show nodes inline
        nodes_str = " ".join([f"🟢{n}" if n == 's' else f"🔴{n}" if n == 't' else n 
                             for n in st.session_state.scratch_nodes])
        st.caption(nodes_str)
        
        st.markdown("---")
        
        # Add Edge Section
        st.markdown("**Add Edge**")
        u = st.selectbox("From", st.session_state.scratch_nodes, key="scratch_from", label_visibility="collapsed")
        v = st.selectbox("To", st.session_state.scratch_nodes, key="scratch_to", label_visibility="collapsed")
        cap = st.number_input("Cap", min_value=1, step=1, value=10, key="scratch_cap", label_visibility="collapsed")
        
        if st.button("➕ Add Edge", key="scratch_add_edge", use_container_width=True):
            if u == v:
                st.error("No self-loops")
            elif v == "s":
                st.error("No edges into 's'")
            elif u == "t":
                st.error("No edges from 't'")
            else:
                if edge_exists(u, v):
                    update_edge(u, v, cap)
                else:
                    st.session_state.scratch_edges.append((u, v, cap))
                    st.session_state.scratch_edge_history.append((u, v, cap))
                st.rerun()
        
        st.markdown("---")
        
        # Action buttons
        col_undo, col_reset = st.columns(2)
        with col_undo:
            if st.button("↩", key="scratch_undo", use_container_width=True,
                        disabled=(len(st.session_state.scratch_edge_history) == 0)):
                last = st.session_state.scratch_edge_history.pop()
                if last in st.session_state.scratch_edges:
                    st.session_state.scratch_edges.remove(last)
                st.rerun()
        with col_reset:
            if st.button("🗑", key="scratch_reset", use_container_width=True):
                st.session_state.scratch_nodes = ["s", "t"]
                st.session_state.scratch_edges = []
                st.session_state.scratch_edge_history = []
                st.rerun()
        
        # Build button
        can_build = len(st.session_state.scratch_edges) > 0
        if st.button("🔨 BUILD", type="primary", use_container_width=True, 
                    disabled=not can_build, key="scratch_build"):
            graph = defaultdict(lambda: defaultdict(int))
            for u, v, cap in st.session_state.scratch_edges:
                graph[u][v] = cap
            
            st.session_state.ff_graph = graph
            st.session_state.ff_source = 's'
            st.session_state.ff_sink = 't'
            st.session_state.ff_graph_built = True
            st.session_state.ff_steps_history = []
            st.rerun()
    
    # ========================================================================
    # MIDDLE COLUMN: GRAPH VISUALIZATION
    # ========================================================================
    with col_graph:
        fig = draw_builder_graph_compact(st.session_state.scratch_nodes, st.session_state.scratch_edges)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        
        # Show next step prompt
        if st.session_state.get('ff_graph_built'):
            st.success("✅ Graph built! → Go to **'▶️ Run Algorithm'** tab")
        elif len(st.session_state.scratch_edges) == 0:
            st.info("💡 Add nodes, then create edges between them")
        else:
            st.info(f"💡 {len(st.session_state.scratch_edges)} edge(s) added. Click **BUILD** when ready")
    
    # ========================================================================
    # RIGHT COLUMN: EDGE LIST
    # ========================================================================
    with col_edges:
        st.markdown(f"**Edges** ({len(st.session_state.scratch_edges)})")
        if len(st.session_state.scratch_edges) == 0:
            st.caption("No edges yet")
        else:
            for (u, v, c) in st.session_state.scratch_edges:
                st.caption(f"{u}→{v}: {c}")


def draw_builder_graph_compact(nodes, edges, selected_node=None):
    """Draw compact graph for builder"""
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#F5F5F5')
    ax.set_facecolor('#FFFFFF')
    
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    for u, v, c in edges:
        G.add_edge(u, v)
    
    # Build graph dict for hierarchical layout
    graph_dict = {}
    for u, v, c in edges:
        if u not in graph_dict:
            graph_dict[u] = {}
        graph_dict[u][v] = c
    
    # Use hierarchical layout
    pos = GraphLayout.hierarchical(graph_dict, 's', 't')
    
    # Ensure all nodes have positions
    for node in nodes:
        if node not in pos:
            if node == 's':
                pos[node] = (0, 0)
            elif node == 't':
                pos[node] = (5, 0)
            else:
                existing_y = [p[1] for p in pos.values()]
                max_y = max(existing_y) if existing_y else 0
                pos[node] = (2.5, max_y + 1.8)
    
    # Draw edges
    for u, v, cap in edges:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                   arrowprops=dict(arrowstyle='->', color='black', lw=1.5, shrinkA=12, shrinkB=12))
        
        # Edge label
        label_x = x1 + 0.25 * (x2 - x1)
        label_y = y1 + 0.25 * (y2 - y1)
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            label_x += -dy / length * 0.1
            label_y += dx / length * 0.1
        ax.text(label_x, label_y, f"{cap}", fontsize=8, ha='center', va='center',
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='gray'), zorder=1000)
    
    # Draw nodes
    node_colors = []
    for node in nodes:
        if node == 's':
            node_colors.append('#90EE90')
        elif node == 't':
            node_colors.append('#FFB6C1')
        else:
            node_colors.append('#FFFFFF')
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, ax=ax,
                          edgecolors='black', linewidths=2)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
    
    ax.axis('off')
    ax.margins(0.15)
    plt.tight_layout()
    return fig



# ============================================================================
# TAB 3: RUN ALGORITHM
# ============================================================================

def render_run_algorithm_tab():
    """Render run algorithm"""
    
    if not st.session_state.get('ff_graph_built'):
        st.warning("⚠️ Please create a graph first (go to 'Create Graph' tab)")
        return
    
    col1, col2 = st.columns([3, 7])
    
    with col1:
        st.markdown("### Graph Info")
        st.info(f"""
        **Source:** {st.session_state.ff_source}  
        **Sink:** {st.session_state.ff_sink}
        """)
        all_nodes = set()
        for u in st.session_state.ff_graph:
            all_nodes.add(u)
            for v in st.session_state.ff_graph[u]:
                all_nodes.add(v)
        num_edges = sum(len(neighbors) for neighbors in st.session_state.ff_graph.values())
        st.metric("Nodes", len(all_nodes))
        st.metric("Edges", num_edges)
        if st.button("🔄 Load Different Graph", use_container_width=True):
            st.session_state.ff_graph_built = False
            st.session_state.ff_steps_history = []
            st.rerun()
    
    with col2:
        if not st.session_state.get('ff_steps_history'):
            st.markdown("### Ready to Run")
            st.info("Click the button below to execute the Ford-Fulkerson algorithm.")
            if st.button("▶️ Run Ford-Fulkerson Algorithm", type="primary", use_container_width=True, key="run_algo"):
                algo = FordFulkersonAlgorithm(st.session_state.ff_graph, st.session_state.ff_source, st.session_state.ff_sink)
                with st.spinner("Computing maximum flow..."):
                    max_flow = algo.run()
                st.session_state.ff_steps_history = algo.get_steps()
                st.session_state.ff_max_flow_value = max_flow
                st.session_state.ff_current_step = 0
                st.rerun()
        else:
            st.markdown("### Algorithm Complete ✅")
            final_step = st.session_state.ff_steps_history[-1]
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Max Flow", st.session_state.ff_max_flow_value)
            with col_b:
                st.metric("Min Cut", final_step.get('cut_value', 0))
            with col_c:
                st.metric("Steps", len(st.session_state.ff_steps_history))
            st.success("✅ Maximum flow found! Go to 'Results' tab to explore steps.")
            if st.button("🔄 Run Again", use_container_width=True):
                st.session_state.ff_steps_history = []
                st.rerun()


# ============================================================================
# TAB 4: RESULTS
# ============================================================================

def render_results_tab():
    """Render results with autoplay"""
    
    if not st.session_state.get('ff_steps_history'):
        st.warning("⚠️ Please run the algorithm first (go to 'Run Algorithm' tab)")
        return
    
    total_steps = len(st.session_state.ff_steps_history)
    if st.session_state.ff_current_step >= total_steps:
        st.session_state.ff_current_step = 0
    if st.session_state.ff_current_step < 0:
        st.session_state.ff_current_step = 0
    
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
    
    with col1:
        if st.button("🎬 Autoplay", use_container_width=True, type="primary", key="btn_autoplay"):
            st.session_state.ff_trigger_autoplay = True
    with col2:
        if 'autoplay_speed' not in st.session_state:
            st.session_state.autoplay_speed = 1.0
        speed = st.select_slider("Speed", options=[0.5, 1.0, 1.5, 2.0], value=st.session_state.autoplay_speed,
                                format_func=lambda x: f"{x}s", key="autoplay_speed", label_visibility="collapsed")
    with col3:
        if st.button("⏮️", use_container_width=True, disabled=(st.session_state.ff_current_step == 0)):
            st.session_state.ff_current_step = 0
            st.rerun()
    with col4:
        if st.button("⬅️", use_container_width=True, disabled=(st.session_state.ff_current_step == 0)):
            st.session_state.ff_current_step -= 1
            st.rerun()
    with col5:
        if st.button("➡️", use_container_width=True, disabled=(st.session_state.ff_current_step == total_steps - 1)):
            st.session_state.ff_current_step += 1
            st.rerun()
    with col6:
        if st.button("⏭️", use_container_width=True, disabled=(st.session_state.ff_current_step == total_steps - 1)):
            st.session_state.ff_current_step = total_steps - 1
            st.rerun()
    
    st.progress((st.session_state.ff_current_step + 1) / total_steps,
                text=f"Step {st.session_state.ff_current_step + 1} of {total_steps}")
    
    graph_placeholder = st.empty()
    
    if 'ff_trigger_autoplay' not in st.session_state:
        st.session_state.ff_trigger_autoplay = False
    
    if st.session_state.ff_trigger_autoplay:
        st.session_state.ff_trigger_autoplay = False
        for i in range(total_steps):
            current_step = st.session_state.ff_steps_history[i]
            with graph_placeholder.container():
                col_g, col_d = st.columns([7, 3])
                with col_g:
                    if current_step['type'] == 'complete':
                        fig = GraphRenderer.render_minimum_cut(current_step, st.session_state.ff_graph,
                                                               st.session_state.ff_source, st.session_state.ff_sink)
                    else:
                        fig = GraphRenderer.render_step(current_step, st.session_state.ff_graph,
                                                       st.session_state.ff_source, st.session_state.ff_sink)
                    fig.set_size_inches(10, 5)
                    st.pyplot(fig)
                    plt.close(fig)
                with col_d:
                    st.markdown(f"### Step {i + 1}/{total_steps}")
                    st.markdown(f"**Type:** {current_step['type'].replace('_', ' ').title()}")
                    if current_step.get('path'):
                        st.info(f"**Path:** {' → '.join(current_step['path'])}")
                        st.metric("Bottleneck", current_step.get('bottleneck', 0))
                    st.metric("Current Flow", current_step['max_flow'])
                    st.markdown(f"""
                        <div style="background-color: #F8F9FA; border: 1px solid #DEE2E6; border-radius: 4px;
                                    padding: 12px; margin-top: 8px; font-size: 14px; line-height: 1.6;">
                        <strong>💡 Explanation</strong><br><br>
                        {current_step['explanation'].replace(chr(10), '<br>')}
                        </div>
                    """, unsafe_allow_html=True)
            if i < total_steps - 1:
                time.sleep(speed)
        st.session_state.ff_current_step = total_steps - 1
        st.success("✅ Autoplay complete!")
    else:
        current_step = st.session_state.ff_steps_history[st.session_state.ff_current_step]
        col_graph, col_info, col_explanation = st.columns([6, 2, 2])
        with col_graph:
            if current_step['type'] == 'complete':
                fig = GraphRenderer.render_minimum_cut(current_step, st.session_state.ff_graph,
                                                       st.session_state.ff_source, st.session_state.ff_sink)
            else:
                fig = GraphRenderer.render_step(current_step, st.session_state.ff_graph,
                                               st.session_state.ff_source, st.session_state.ff_sink)
            fig.set_size_inches(9, 5)
            st.pyplot(fig)
            plt.close(fig)
        with col_info:
            st.markdown(f"### Step {st.session_state.ff_current_step + 1}/{total_steps}")
            st.markdown(f"**Type:** {current_step['type'].replace('_', ' ').title()}")
            if current_step.get('path'):
                st.info(f"**Path:**  \n{' → '.join(current_step['path'])}")
                st.metric("Bottleneck", current_step.get('bottleneck', 0))
            st.metric("Flow", current_step['max_flow'])
        with col_explanation:
            st.markdown("**💡 Explanation**")
            st.markdown(f"""
                <div style="background-color: #F8F9FA; border: 1px solid #DEE2E6; border-radius: 4px;
                            padding: 10px; margin-top: 8px; font-size: 13px; line-height: 1.5; height: 400px; overflow-y: auto;">
                {current_step['explanation'].replace(chr(10), '<br>')}
                </div>
            """, unsafe_allow_html=True)


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_ford_fulkerson():
    """Main function with horizontal tabs"""
    
    initialize_session_state()
    
    st.markdown("""
        <style>
        .stApp { background-color: #F8F9FA; }
        .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        .stMarkdown, .stText, p, span, div { color: #000000 !important; }
        h1, h2, h3, h4, h5, h6 { color: #000000 !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 2px; }
        .stTabs [data-baseweb="tab"] { background-color: transparent; color: #000000; }
        .stTabs [aria-selected="true"] { background-color: #1976D2; color: white !important; }
        .stButton > button { color: #000000; border: 1px solid #CCCCCC; background-color: #FFFFFF; }
        .stButton > button[kind="primary"] { background-color: #1976D2; color: white !important; border: none; }
        .stButton > button:hover { border-color: #1976D2; }
        .stAlert { color: #000000 !important; }
        [data-testid="stMetricLabel"] { color: #000000 !important; }
        [data-testid="stMetricValue"] { color: #1976D2 !important; }
        code { color: #000000 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🌊 Ford-Fulkerson Algorithm Visualizer")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Introduction", "🔨 Create Graph", "▶️ Run Algorithm", "📊 Results"])
    
    with tab1:
        render_introduction_tab()
    with tab2:
        render_create_graph_tab()
    with tab3:
        render_run_algorithm_tab()
    with tab4:
        render_results_tab()