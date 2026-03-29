"""
Vertex Cover - Minimalist 4-tab wizard
"""

import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
import random
import time

from .vc_core import VertexCoverAlgorithm
from .vc_visualization import VCRenderer

def init_vc_state():
    if 'vc_nodes' not in st.session_state:
        st.session_state.vc_nodes = ['A', 'B', 'C', 'D', 'E']
    if 'vc_edges' not in st.session_state:
        st.session_state.vc_edges = [('A', 'B'), ('A', 'C'), ('A', 'D'), ('A', 'E')]
    if 'vc_steps_history' not in st.session_state:
        st.session_state.vc_steps_history = []
    if 'vc_current_step' not in st.session_state:
        st.session_state.vc_current_step = 0
    if 'vc_trigger_autoplay' not in st.session_state:
        st.session_state.vc_trigger_autoplay = False

def render_vc_introduction():
    col1, col2 = st.columns([7, 3])
    with col1:
        st.markdown("""
        ### Vertex Cover (Maximal Matching 2-Approximation)
        
        **Concept:**
        A **Vertex Cover** of a graph is a set of vertices such that every single edge in the graph touches at least one of those vertices. 
        Finding the *absolute minimum* Vertex Cover is NP-Hard! However, we can quickly find a "2-Approximation" (a cover that is guaranteed to be no more than twice the size of the optimal one) using a clever matching trick.
        
        **The Algorithm:**
        1. Initialize $VC = \\emptyset$ and track all active edges $E' = E$.
        2. Pick any arbitrary edge $e = (x, y)$ from $E'$.
        3. Drop BOTH endpoints $x$ and $y$ into our $VC$ bucket.
        4. Because $x$ and $y$ are now covered, we can safely prune ALL edges connected to $x$ or $y$ from $E'$.
        5. Repeat until there are no edges left in $E'$!
        """)
    with col2:
        st.info("""
        **Workflow:**
        1. **Create Graph** tab (Design your abstract network)
        2. **Run Algorithm** tab (Execute the solver)
        3. **Results** tab (Watch the pruning happen)
        """)

def render_vc_input_tab():
    col1, col2 = st.columns([4, 6])
    
    with col1:
        st.markdown("### Graph Builder")
        st.info("Vertex Cover operates on standard unweighted, undirected graphs.")
        
        # Generator
        st.markdown("**1. Generate Random Map**")
        n_rand = st.slider("Nodes", min_value=4, max_value=20, value=6)
        prob = st.slider("Edge Probability", min_value=0.2, max_value=0.8, value=0.4)
        if st.button("🎲 Generate Random Graph", use_container_width=True, help="Create a fresh random map"):
            G = nx.erdos_renyi_graph(n_rand, prob)
            # Create a string representation for nodes 0-19 to A-T
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            st.session_state.vc_nodes = [chars[i] for i in G.nodes()]
            st.session_state.vc_edges = [(chars[u], chars[v]) for u, v in G.edges()]
            st.session_state.vc_steps_history = []
            st.rerun()
            
        st.markdown("---")
        
        # Manual Edges
        st.markdown("**2. Add Manual Edge**")
        col_u, col_v = st.columns(2)
        with col_u:
            new_u = st.text_input("Node 1 (e.g. A)", max_chars=1).upper()
        with col_v:
            new_v = st.text_input("Node 2 (e.g. B)", max_chars=1).upper()
            
        if st.button("➕ Add Edge", use_container_width=True, disabled=(not new_u or not new_v or new_u == new_v)):
            edge = tuple(sorted((new_u, new_v)))
            will_add_u = new_u not in st.session_state.vc_nodes
            will_add_v = new_v not in st.session_state.vc_nodes
            
            if len(st.session_state.vc_nodes) + will_add_u + will_add_v > 20:
                st.error("Error: Maximum 20 nodes allowed.")
            elif edge not in st.session_state.vc_edges:
                st.session_state.vc_edges.append(edge)
                if will_add_u: st.session_state.vc_nodes.append(new_u)
                if will_add_v: st.session_state.vc_nodes.append(new_v)
                st.session_state.vc_steps_history = []
                st.rerun()
            
        st.markdown("---")
        if st.button("🗑️ Clear Graph", use_container_width=True):
            st.session_state.vc_nodes = []
            st.session_state.vc_edges = []
            st.session_state.vc_steps_history = []
            st.rerun()

    with col2:
        st.markdown("### Current Graph")
        if not st.session_state.vc_nodes:
            st.warning("Graph is empty.")
            return
            
        # Quick static preview
        G = nx.Graph()
        G.add_nodes_from(st.session_state.vc_nodes)
        G.add_edges_from(st.session_state.vc_edges)
        
        pos = nx.spring_layout(G, seed=42)
        fig, ax = plt.subplots(figsize=(6, 5))
        fig.patch.set_facecolor('#F8F9FA')
        ax.set_facecolor('#FFFFFF')
        
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#BDBDBD', width=1.5)
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#FFFFFF', edgecolors='#424242', linewidths=2, node_size=400)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight='bold')
        
        ax.set_frame_on(True)
        for spine in ax.spines.values():
            spine.set_color('#E0E0E0')
            
        st.pyplot(fig)
        plt.close(fig)

def render_vc_run_tab():
    if not st.session_state.vc_edges:
        st.warning("Please add some edges in the 'Create Graph' tab first.")
        return
        
    col1, col2 = st.columns([3, 7])
    with col1:
        st.markdown("### Profile")
        st.metric("Total Vertices", len(st.session_state.vc_nodes))
        st.metric("Total Edges", len(st.session_state.vc_edges))
        
    with col2:
        if not st.session_state.vc_steps_history:
            st.markdown("### Ready to Run")
            if st.button("▶️ Run Vertex Cover Algorithm", type="primary", use_container_width=True):
                with st.spinner("Finding Maximal Cover..."):
                    algo = VertexCoverAlgorithm(st.session_state.vc_nodes, st.session_state.vc_edges)
                    vc_set = algo.run()
                    st.session_state.vc_steps_history = algo.get_steps()
                    st.session_state.vc_current_step = 0
                st.rerun()
        else:
            st.markdown("### Complete!")
            final_vc = st.session_state.vc_steps_history[-1]['vc']
            st.success(f"Algorithm finished. The guaranteed 2-Approximation Vertex Cover size is **{len(final_vc)}**.")
            if st.button("🔁 Run Again", use_container_width=True):
                st.session_state.vc_steps_history = []
                st.rerun()

def render_vc_results_tab():
    if not st.session_state.vc_steps_history:
        st.warning("Please run the algorithm first.")
        return
        
    total_steps = len(st.session_state.vc_steps_history)
    
    if st.session_state.vc_current_step >= total_steps:
        st.session_state.vc_current_step = total_steps - 1
    if st.session_state.vc_current_step < 0:
        st.session_state.vc_current_step = 0
        
    # Controls
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
    with col1:
        if st.button("▶️ Autoplay", use_container_width=True, type="primary"):
            st.session_state.vc_trigger_autoplay = True
    with col2:
        if 'vc_autoplay_speed' not in st.session_state:
            st.session_state.vc_autoplay_speed = 1.0
        speed = st.select_slider("Speed", options=[0.5, 1.0, 2.0, 3.0], value=st.session_state.vc_autoplay_speed, format_func=lambda x: f"{x}s", label_visibility="collapsed")
    with col3:
        if st.button("⏮️ First", use_container_width=True, disabled=st.session_state.vc_current_step == 0):
            st.session_state.vc_current_step = 0
            st.rerun()
    with col4:
        if st.button("⏪ Prev", use_container_width=True, disabled=st.session_state.vc_current_step == 0):
            st.session_state.vc_current_step -= 1
            st.rerun()
    with col5:
        if st.button("Next ⏩", use_container_width=True, disabled=st.session_state.vc_current_step == total_steps - 1):
            st.session_state.vc_current_step += 1
            st.rerun()
    with col6:
        if st.button("Last ⏭️", use_container_width=True, disabled=st.session_state.vc_current_step == total_steps - 1):
            st.session_state.vc_current_step = total_steps - 1
            st.rerun()
            
    st.progress((st.session_state.vc_current_step + 1) / total_steps, text=f"Step {st.session_state.vc_current_step + 1} of {total_steps}")
    
    graph_container = st.empty()
    
    if st.session_state.vc_trigger_autoplay:
        st.session_state.vc_trigger_autoplay = False
        for i in range(st.session_state.vc_current_step, total_steps):
            step_data = st.session_state.vc_steps_history[i]
            with graph_container.container():
                col_graph, col_expl = st.columns([7, 3])
                with col_graph:
                    fig = VCRenderer.render_step(step_data)
                    st.pyplot(fig)
                    plt.close(fig)
                with col_expl:
                    st.markdown(f"**Step {i + 1}/{total_steps}**")
                    st.markdown(f"**Phase:** {step_data['type'].replace('_', ' ').title()}")
                    explanation = step_data.get('explanation', '').replace('\n', '<br>')
                    st.markdown(f"""
                        <div style="background-color: #F8F9FA; padding: 15px; border-radius: 5px; border: 1px solid #DEE2E6; font-size: 14px; line-height: 1.5; min-height: 350px;">
                        {explanation}
                        </div>
                    """, unsafe_allow_html=True)
            if i < total_steps - 1:
                time.sleep(speed)
        
        st.session_state.vc_current_step = total_steps - 1
        st.rerun()
    else:
        with graph_container.container():
            step_data = st.session_state.vc_steps_history[st.session_state.vc_current_step]
            col_graph, col_expl = st.columns([7, 3])
            with col_graph:
                fig = VCRenderer.render_step(step_data)
                st.pyplot(fig)
                plt.close(fig)
            with col_expl:
                st.markdown(f"**Step {st.session_state.vc_current_step + 1}/{total_steps}**")
                st.markdown(f"**Phase:** {step_data['type'].replace('_', ' ').title()}")
                explanation = step_data.get('explanation', '').replace('\n', '<br>')
                st.markdown(f"""
                    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 5px; border: 1px solid #DEE2E6; font-size: 14px; line-height: 1.5; min-height: 350px;">
                    {explanation}
                    </div>
                """, unsafe_allow_html=True)


def render_vertex_cover():
    init_vc_state()
    st.markdown("## Vertex Cover Visualizer")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Create Graph", "Run Algorithm", "Results"])
    
    with tab1: render_vc_introduction()
    with tab2: render_vc_input_tab()
    with tab3: render_vc_run_tab()
    with tab4: render_vc_results_tab()
