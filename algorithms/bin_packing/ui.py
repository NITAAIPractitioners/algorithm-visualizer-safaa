"""
Bin Packing - First Fit and Best Fit UI
Minimalist 4-tab wizard (Introduction, Input, Run, Results)
"""

import streamlit as st
import matplotlib.pyplot as plt
import time
import random

from .bp_core import FirstFitAlgorithm, BestFitAlgorithm
from .bp_visualization import BinRenderer

# ============================================================================
# INITIALIZE STATE
# ============================================================================

def init_bp_state(algo_type):
    # Clear state if we switched between First Fit and Best Fit
    if st.session_state.get('bp_current_algo') != algo_type:
        st.session_state.bp_items = []
        st.session_state.bp_steps_history = []
        st.session_state.bp_current_step = 0
        st.session_state.bp_final_bins = []
        st.session_state.bp_trigger_autoplay = False
        st.session_state.bp_current_algo = algo_type

    if 'bp_items' not in st.session_state:
        st.session_state.bp_items = []
    if 'bp_steps_history' not in st.session_state:
        st.session_state.bp_steps_history = []
    if 'bp_current_step' not in st.session_state:
        st.session_state.bp_current_step = 0
    if 'bp_final_bins' not in st.session_state:
        st.session_state.bp_final_bins = []
    if 'bp_trigger_autoplay' not in st.session_state:
        st.session_state.bp_trigger_autoplay = False
    if 'bp_current_algo' not in st.session_state:
        st.session_state.bp_current_algo = algo_type

# ============================================================================
# SHARED TAB GENERATORS
# ============================================================================

def render_bp_introduction(algo_type):
    """Render Introduction Tab for the specific algorithm"""
    col1, col2 = st.columns([7, 3])
    
    with col1:
        if algo_type == "first_fit":
            st.markdown("""
            ### First Fit Algorithm (Bin Packing)
            
            **Concept:**
            The First Fit algorithm places each item into the **first available bin** that has enough remaining capacity to hold it. 
            If no existing bin has enough space, a new bin is created.
            
            **Rules:**
            - Bins are indexed 1, 2, ... and initially empty.
            - Bin Capacity is exactly 1.0.
            - Items arrive in order $u_1, u_2, \dots, u_n$.
            - To pack item $u_i$ with size $s_i$, find the *least index* $j$ such that bin $j$ contains at most $1 - s_i$.
            """)
        else: # Best Fit
            st.markdown("""
            ### Best Fit Algorithm (Bin Packing)
            
            **Concept:**
            The Best Fit algorithm considers all existing bins and places the item into the bin where it fits the **tightest** (leaving the least amount of empty space). 
            If it cannot fit in any existing bin, a new bin is created.
            
            **Rules:**
            - Bins are indexed 1, 2, ... and initially empty.
            - Bin Capacity is exactly 1.0.
            - Items arrive in order $u_1, u_2, \dots, u_n$.
            - To pack $u_i$ (size $s_i$), find the bin filled to level $l \le 1 - s_i$ where $l$ is as *large as possible*.
            """)
            
    with col2:
        st.info("""
        **Workflow:**
        
        1. **Input Items** tab  
           Provide the sizes of your items.
        
        2. **Run Algorithm** tab  
           Execute the simulation.
        
        3. **Results** tab  
           Watch the step-by-step bin assignment.
        """)

def render_bp_input_tab():
    """Render Input Items Tab"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Method 1: Random Generation**")
        n_items = st.slider("Number of items", min_value=3, max_value=15, value=7)
        if st.button("🎲 Generate Random Items", use_container_width=True, help="Randomly generate items to test the algorithm."):
            items = [round(random.uniform(0.1, 0.9), 2) for _ in range(n_items)]
            st.session_state.bp_items = items
            st.session_state.bp_steps_history = []
            st.success("Generated random array!")
            st.rerun()
            
    with col2:
        st.markdown("**Method 2: Manual Input**")
        text_input = st.text_input("Comma-separated values between 0.1 and 1.0", value="0.4, 0.8, 0.2, 0.2, 0.5")
        if st.button("📝 Load Manual Items", use_container_width=True, help="Load your custom sizes."):
            try:
                items = [float(x.strip()) for x in text_input.split(',')]
                if any(x <= 0 or x > 1.0 for x in items):
                    st.error("All values must be strictly greater than 0 and less than or equal to 1.0")
                else:
                    st.session_state.bp_items = items
                    st.session_state.bp_steps_history = []
                    st.success("Manual array loaded!")
                    st.rerun()
            except ValueError:
                st.error("Invalid input format. Use numbers separated by commas.")
                
    st.markdown("---")
    if st.session_state.bp_items:
        st.info(f"**Current Items ({len(st.session_state.bp_items)} total):** " + 
                ", ".join([str(x) for x in st.session_state.bp_items]))
    else:
        st.warning("No items loaded. Please generate or input items above.")

def render_bp_run_tab(algo_type):
    """Render Run Algorithm Tab"""
    if not st.session_state.bp_items:
        st.warning("Please input items first in the 'Input Items' tab.")
        return
        
    col1, col2 = st.columns([3, 7])
    
    with col1:
        st.markdown("### Problem Info")
        st.metric("Total Items", len(st.session_state.bp_items))
        total_sum = sum(st.session_state.bp_items)
        st.metric("Total Size Sum", round(total_sum, 2))
        st.caption(f"Theoretical Absolute Minimum Bins: {int(total_sum) + (1 if total_sum % 1 > 0 else 0)}")
        
    with col2:
        if not st.session_state.bp_steps_history:
            st.markdown("### Ready to Run")
            name = "First Fit" if algo_type == "first_fit" else "Best Fit"
            if st.button(f"▶️ Run {name} Algorithm", type="primary", use_container_width=True, help="Execute the algorithm using input items."):
                with st.spinner("Assigning bins..."):
                    if algo_type == "first_fit":
                        algo = FirstFitAlgorithm(st.session_state.bp_items)
                    else:
                        algo = BestFitAlgorithm(st.session_state.bp_items)
                    
                    st.session_state.bp_final_bins = algo.run()
                    st.session_state.bp_steps_history = algo.get_steps()
                    st.session_state.bp_current_step = 0
                st.rerun()
        else:
            st.markdown("### Algorithm Complete")
            st.success(f"Finished! Used {len(st.session_state.bp_final_bins)} bins. Go to the 'Results' tab to see step-by-step logic.")
            if st.button("🔁 Run Again", use_container_width=True, help="Clear results & start over."):
                st.session_state.bp_steps_history = []
                st.rerun()

def render_bp_results_tab():
    """Render Results Tab with GraphRenderer"""
    if not st.session_state.bp_steps_history:
        st.warning("Please run the algorithm first.")
        return
        
    total_steps = len(st.session_state.bp_steps_history)
    
    # Boundary checks
    if st.session_state.bp_current_step >= total_steps:
        st.session_state.bp_current_step = total_steps - 1
    if st.session_state.bp_current_step < 0:
        st.session_state.bp_current_step = 0
        
    # Controls
    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
    
    with col1:
        if st.button("▶️ Autoplay", use_container_width=True, type="primary", help="Play steps automatically."):
            st.session_state.bp_trigger_autoplay = True
    with col2:
        if 'bp_autoplay_speed' not in st.session_state:
            st.session_state.bp_autoplay_speed = 0.5
        speed = st.select_slider("Speed", options=[0.2, 0.5, 1.0, 1.5], value=st.session_state.bp_autoplay_speed, format_func=lambda x: f"{x}s", label_visibility="collapsed")
    with col3:
        if st.button("⏮️ First", use_container_width=True, help="Go to the very beginning.", disabled=st.session_state.bp_current_step == 0):
            st.session_state.bp_current_step = 0
            st.rerun()
    with col4:
        if st.button("⏪ Prev", use_container_width=True, help="Go back one step.", disabled=st.session_state.bp_current_step == 0):
            st.session_state.bp_current_step -= 1
            st.rerun()
    with col5:
        if st.button("Next ⏩", use_container_width=True, help="Advance one step.", disabled=st.session_state.bp_current_step == total_steps - 1):
            st.session_state.bp_current_step += 1
            st.rerun()
    with col6:
        if st.button("Last ⏭️", use_container_width=True, help="Skip to the final result.", disabled=st.session_state.bp_current_step == total_steps - 1):
            st.session_state.bp_current_step = total_steps - 1
            st.rerun()
            
    st.progress((st.session_state.bp_current_step + 1) / total_steps, text=f"Step {st.session_state.bp_current_step + 1} of {total_steps}")
    
    graph_container = st.empty()
    
    if st.session_state.bp_trigger_autoplay:
        st.session_state.bp_trigger_autoplay = False
        for i in range(st.session_state.bp_current_step, total_steps):
            step_data = st.session_state.bp_steps_history[i]
            with graph_container.container():
                col_graph, col_expl = st.columns([7, 3])
                with col_graph:
                    fig = BinRenderer.render_step(step_data)
                    st.pyplot(fig)
                    plt.close(fig)
                with col_expl:
                    st.markdown(f"**Step {i + 1}/{total_steps}**")
                    st.markdown(f"**Action:** {step_data['type'].replace('_', ' ').title()}")
                    explanation = step_data.get('explanation', '').replace('\n', '<br>')
                    st.markdown(f"""
                        <div style="background-color: #F8F9FA; padding: 15px; border-radius: 5px; border: 1px solid #DEE2E6; font-size: 14px; line-height: 1.5;">
                        {explanation}
                        </div>
                    """, unsafe_allow_html=True)
            if i < total_steps - 1:
                time.sleep(speed)
        
        st.session_state.bp_current_step = total_steps - 1
        st.rerun()
    else:
        step_data = st.session_state.bp_steps_history[st.session_state.bp_current_step]
        col_graph, col_expl = st.columns([7, 3])
        with col_graph:
            fig = BinRenderer.render_step(step_data)
            st.pyplot(fig)
            plt.close(fig)
        with col_expl:
            st.markdown(f"**Step {st.session_state.bp_current_step + 1}/{total_steps}**")
            st.markdown(f"**Action:** {step_data['type'].replace('_', ' ').title()}")
            explanation = step_data.get('explanation', '').replace('\n', '<br>')
            st.markdown(f"""
                <div style="background-color: #F8F9FA; padding: 15px; border-radius: 5px; border: 1px solid #DEE2E6; font-size: 14px; line-height: 1.5; height: 350px; overflow-y: auto;">
                {explanation}
                </div>
            """, unsafe_allow_html=True)


# ============================================================================
# EXPOSED RENDER FUNCTIONS
# ============================================================================

def render_first_fit():
    init_bp_state("first_fit")
    st.markdown("## First Fit Bin Packing")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Input Items", "Run Algorithm", "Results"])
    
    with tab1: render_bp_introduction("first_fit")
    with tab2: render_bp_input_tab()
    with tab3: render_bp_run_tab("first_fit")
    with tab4: render_bp_results_tab()

def render_best_fit():
    init_bp_state("best_fit")
    st.markdown("## Best Fit Bin Packing")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Input Items", "Run Algorithm", "Results"])
    
    with tab1: render_bp_introduction("best_fit")
    with tab2: render_bp_input_tab()
    with tab3: render_bp_run_tab("best_fit")
    with tab4: render_bp_results_tab()
