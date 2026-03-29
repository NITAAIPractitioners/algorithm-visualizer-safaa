"""
Euclidean TSP - MST and Matching UI
Minimalist 4-tab wizard (Introduction, Create Graph, Run, Results)
"""

import streamlit as st
import matplotlib.pyplot as plt
import time
import random

from .tsp_core import TSPMSTAlgorithm, TSPMatchingAlgorithm
from .tsp_visualization import TSPRenderer

# ============================================================================
# INITIALIZE STATE
# ============================================================================

def init_tsp_state(algo_type):
    # Clear state if switching between TSP algorithms
    if st.session_state.get('tsp_current_algo') != algo_type:
        # Default 4-node diamond
        st.session_state.tsp_nodes = {
            'A': (50, 90),
            'B': (10, 50),
            'C': (90, 50),
            'D': (50, 10)
        }
        st.session_state.tsp_steps_history = []
        st.session_state.tsp_current_step = 0
        st.session_state.tsp_trigger_autoplay = False
        st.session_state.tsp_current_algo = algo_type

    if 'tsp_nodes' not in st.session_state:
        st.session_state.tsp_nodes = {'A': (50, 90), 'B': (10, 50), 'C': (90, 50)}
    if 'tsp_steps_history' not in st.session_state:
        st.session_state.tsp_steps_history = []
    if 'tsp_current_step' not in st.session_state:
        st.session_state.tsp_current_step = 0
    if 'tsp_trigger_autoplay' not in st.session_state:
        st.session_state.tsp_trigger_autoplay = False
    if 'tsp_current_algo' not in st.session_state:
        st.session_state.tsp_current_algo = algo_type

# ============================================================================
# SHARED TAB GENERATORS
# ============================================================================

def render_tsp_introduction(algo_type):
    col1, col2 = st.columns([7, 3])
    
    with col1:
        if algo_type == "tsp_mst":
            st.markdown("""
            ### Euclidean TSP (Using Minimum Spanning Tree)
            
            **Concept:**
            The Traveling Salesman Problem (TSP) asks for the shortest possible route that visits every city exactly once and returns to the origin city. 
            Because this is *Euclidean* TSP, cities exist on a 2D map, and distances are strict straight lines (satisfying the Triangle Inequality).
            
            **2-Approximation Algorithm:**
            1. Construct a Minimum Spanning Tree (MST).
            2. Double every edge to form a multigraph (guaranteeing every node has an even degree).
            3. Find an Eulerian Tour across all edges.
            4. Shortcut the tour (skip already visited cities) to form a Hamiltonian Cycle.
            
            *Guarantee: The final tour is guaranteed to be no more than 2x the length of the absolute optimal tour.*
            """)
        else: # Matching
            st.markdown("""
            ### Euclidean TSP (Using Minimum Matching / Christofides)
            
            **Concept:**
            Instead of crudely doubling every edge in the MST, we can be much smarter about how we ensure every node has an even degree so we can trace a tour.
            
            **1.5-Approximation Algorithm:**
            1. Construct a Minimum Spanning Tree (MST).
            2. Identify the set of vertices that have an *odd degree* in the MST.
            3. Find a Minimum Weight Perfect Matching connecting those odd vertices.
            4. Add those matching edges to the MST.
            5. Find an Eulerian Tour and shortcut it to a Hamiltonian Cycle.
            
            *Guarantee: By only matching odd vertices, we save massive distance. The final tour is guaranteed to be no more than 1.5x the optimal tour!*
            """)
            
    with col2:
        st.info("""
        **Workflow:**
        
        1. **Create Graph** tab  
           Add up to 10 cities to the map.
        
        2. **Run Algorithm** tab  
           Execute the estimation.
        
        3. **Results** tab  
           Watch the mathematical steps visually construct the tour.
        """)

def render_tsp_input_tab():
    st.markdown("### 2D City Configuration")
    st.info("To perfectly preserve Euclidean geometry and prevent unrealistic mathematical errors, you simply add or remove cities, and the system automatically assigns their true map coordinates. (Max 10 Cities)")
    
    col1, col2 = st.columns([3, 7])
    
    with col1:
        st.markdown("**Manage Cities**")
        current_count = len(st.session_state.tsp_nodes)
        st.metric("Total Cities", current_count)
        
        c_add, c_sub = st.columns(2)
        with c_add:
            if st.button("➕ Add Node", use_container_width=True, disabled=current_count >= 10):
                # Find next available letter
                for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    if char not in st.session_state.tsp_nodes:
                        st.session_state.tsp_nodes[char] = (random.randint(5, 95), random.randint(5, 95))
                        st.session_state.tsp_steps_history = []
                        st.rerun()
                        break
        with c_sub:
            if st.button("➖ Remove", use_container_width=True, disabled=current_count <= 2):
                last_key = list(st.session_state.tsp_nodes.keys())[-1]
                del st.session_state.tsp_nodes[last_key]
                st.session_state.tsp_steps_history = []
                st.rerun()
                
        st.markdown("---")
        if st.button("🎲 Generate entirely new random map", use_container_width=True):
            st.session_state.tsp_nodes = {}
            # Generate random number of nodes between 5 and 10
            n = random.randint(5, 10)
            chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for i in range(n):
                st.session_state.tsp_nodes[chars[i]] = (random.randint(5, 95), random.randint(5, 95))
            st.session_state.tsp_steps_history = []
            st.rerun()

        st.markdown("---")
        st.write("**Adjust City Coordinates (0-100)**")
        col_lbl_name, col_lbl_x, col_lbl_y = st.columns([1, 2, 2])
        col_lbl_name.caption("City")
        col_lbl_x.caption("X-Axis")
        col_lbl_y.caption("Y-Axis")
        
        for name in list(st.session_state.tsp_nodes.keys()):
            x, y = st.session_state.tsp_nodes[name]
            col_n, col_x, col_y = st.columns([1, 2, 2])
            with col_n:
                st.markdown(f"<div style='margin-top: 5px'><strong>{name}</strong></div>", unsafe_allow_html=True)
            with col_x:
                new_x = st.number_input(f"X_{name}", min_value=0, max_value=100, value=int(x), key=f"x_val_{name}", label_visibility="collapsed")
            with col_y:
                new_y = st.number_input(f"Y_{name}", min_value=0, max_value=100, value=int(y), key=f"y_val_{name}", label_visibility="collapsed")
                
            if new_x != x or new_y != y:
                st.session_state.tsp_nodes[name] = (new_x, new_y)
                st.session_state.tsp_steps_history = []
                st.rerun()
                
    with col2:
        # Render a quick preview
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#F8F9FA')
        ax.set_facecolor('#FFFFFF')
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Draw complete graph preview with distance labels
        import math
        nodes_list = list(st.session_state.tsp_nodes.items())
        for i in range(len(nodes_list)):
            for j in range(i+1, len(nodes_list)):
                name1, (x1, y1) = nodes_list[i]
                name2, (x2, y2) = nodes_list[j]
                
                # Draw edge
                ax.plot([x1, x2], [y1, y2], color='#E0E0E0', lw=1, alpha=0.3, zorder=1)
                
                # Calculate and label distance
                dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                ax.text(mid_x, mid_y, f"{dist:.0f}", color='#9E9E9E', fontsize=8, ha='center', va='center',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0.1), zorder=2)
                        
        # Draw nodes
        for name, (x, y) in st.session_state.tsp_nodes.items():
            ax.scatter(x, y, s=300, c='#FFFFFF', edgecolors='#424242', linewidths=2, zorder=3)
            ax.text(x, y, str(name), ha='center', va='center', fontweight='bold', color='#212121', zorder=4)
            
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal', adjustable='box')
        for spine in ax.spines.values():
            spine.set_color('#E0E0E0')
            
        st.pyplot(fig)
        plt.close(fig)

def render_tsp_run_tab(algo_type):
    if len(st.session_state.tsp_nodes) < 3:
        st.warning("Please add at least 3 cities in the 'Create Graph' tab.")
        return
        
    col1, col2 = st.columns([3, 7])
    
    with col1:
        st.markdown("### Graph Info")
        st.metric("Total Cities (N)", len(st.session_state.tsp_nodes))
        st.caption("A fully connected map means examining $(N \\times (N-1))/2$ possible roads.")
        
    with col2:
        if not st.session_state.tsp_steps_history:
            st.markdown("### Ready to Run")
            name = "MST" if algo_type == "tsp_mst" else "Christofides (Matching)"
            if st.button(f"▶️ Run {name} Algorithm", type="primary", use_container_width=True):
                with st.spinner("Computing Tour..."):
                    if algo_type == "tsp_mst":
                        algo = TSPMSTAlgorithm(st.session_state.tsp_nodes)
                    else:
                        algo = TSPMatchingAlgorithm(st.session_state.tsp_nodes)
                    
                    algo.run()
                    st.session_state.tsp_steps_history = algo.get_steps()
                    st.session_state.tsp_current_step = 0
                st.rerun()
        else:
            st.markdown("### Algorithm Complete")
            st.success("Tour complete! Head to the Results tab to see the step-by-step logic.")
            if st.button("🔁 Run Again", use_container_width=True):
                st.session_state.tsp_steps_history = []
                st.rerun()

def render_tsp_results_tab():
    if not st.session_state.tsp_steps_history:
        st.warning("Please run the algorithm first.")
        return
        
    total_steps = len(st.session_state.tsp_steps_history)
    
    # Boundary checks
    if st.session_state.tsp_current_step >= total_steps:
        st.session_state.tsp_current_step = total_steps - 1
    if st.session_state.tsp_current_step < 0:
        st.session_state.tsp_current_step = 0
        
    # Controls
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
    
    with col1:
        if st.button("▶️ Autoplay", use_container_width=True, type="primary"):
            st.session_state.tsp_trigger_autoplay = True
    with col2:
        if 'tsp_autoplay_speed' not in st.session_state:
            st.session_state.tsp_autoplay_speed = 1.0
        speed = st.select_slider("Speed", options=[0.5, 1.0, 2.0, 3.0], value=st.session_state.tsp_autoplay_speed, format_func=lambda x: f"{x}s", label_visibility="collapsed")
    with col3:
        if st.button("⏮️ First", use_container_width=True, help="Go to start", disabled=st.session_state.tsp_current_step == 0):
            st.session_state.tsp_current_step = 0
            st.rerun()
    with col4:
        if st.button("⏪ Prev", use_container_width=True, help="Back 1 step", disabled=st.session_state.tsp_current_step == 0):
            st.session_state.tsp_current_step -= 1
            st.rerun()
    with col5:
        if st.button("Next ⏩", use_container_width=True, help="Forward 1 step", disabled=st.session_state.tsp_current_step == total_steps - 1):
            st.session_state.tsp_current_step += 1
            st.rerun()
    with col6:
        if st.button("Last ⏭️", use_container_width=True, help="Go to end", disabled=st.session_state.tsp_current_step == total_steps - 1):
            st.session_state.tsp_current_step = total_steps - 1
            st.rerun()
            
    st.progress((st.session_state.tsp_current_step + 1) / total_steps, text=f"Step {st.session_state.tsp_current_step + 1} of {total_steps}")
    
    graph_container = st.empty()
    
    if st.session_state.tsp_trigger_autoplay:
        st.session_state.tsp_trigger_autoplay = False
        for i in range(st.session_state.tsp_current_step, total_steps):
            step_data = st.session_state.tsp_steps_history[i]
            with graph_container.container():
                col_graph, col_expl = st.columns([7, 3])
                with col_graph:
                    fig = TSPRenderer.render_step(step_data)
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
        
        st.session_state.tsp_current_step = total_steps - 1
        st.rerun()
    else:
        with graph_container.container():
            step_data = st.session_state.tsp_steps_history[st.session_state.tsp_current_step]
            col_graph, col_expl = st.columns([7, 3])
            with col_graph:
                fig = TSPRenderer.render_step(step_data)
                st.pyplot(fig)
                plt.close(fig)
            with col_expl:
                st.markdown(f"**Step {st.session_state.tsp_current_step + 1}/{total_steps}**")
                st.markdown(f"**Phase:** {step_data['type'].replace('_', ' ').title()}")
                explanation = step_data.get('explanation', '').replace('\n', '<br>')
                st.markdown(f"""
                    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 5px; border: 1px solid #DEE2E6; font-size: 14px; line-height: 1.5; min-height: 350px;">
                    {explanation}
                    </div>
                """, unsafe_allow_html=True)

# ============================================================================
# EXPOSED RENDER FUNCTIONS
# ============================================================================

def render_tsp_mst():
    init_tsp_state("tsp_mst")
    st.markdown("## Euclidean TSP (MST Approach)")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Create Graph", "Run Algorithm", "Results"])
    with tab1: render_tsp_introduction("tsp_mst")
    with tab2: render_tsp_input_tab()
    with tab3: render_tsp_run_tab("tsp_mst")
    with tab4: render_tsp_results_tab()

def render_tsp_matching():
    init_tsp_state("tsp_matching")
    st.markdown("## Euclidean TSP (Christofides Matching)")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Create Graph", "Run Algorithm", "Results"])
    with tab1: render_tsp_introduction("tsp_matching")
    with tab2: render_tsp_input_tab()
    with tab3: render_tsp_run_tab("tsp_matching")
    with tab4: render_tsp_results_tab()
