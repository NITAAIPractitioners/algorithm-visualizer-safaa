"""
Algorithm Visualizer Platform
Educational tool for algorithm visualization

FIXED for your directory structure:
algorithms/
  ford_fulkerson/
    __init__.py
    ff_core.py
    ff_visualization.py
    ui.py
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Algorithm Visualizer",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Clean typography */
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Main container */
.main {
    background-color: #f8f9fa;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 6rem 2rem;
    color: #6c757d;
}

.empty-state h2 {
    font-size: 2rem;
    margin-bottom: 1rem;
    color: #495057;
    font-weight: 600;
}

.empty-state p {
    font-size: 1.2rem;
    color: #6c757d;
    line-height: 1.6;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.sidebar-title {
    font-size: 1.4rem;
    font-weight: 700;
    padding: 1.5rem 0;
    text-align: center;
    border-bottom: 2px solid rgba(255,255,255,0.2);
    margin-bottom: 1.5rem;
}

.sidebar-section {
    margin: 1.5rem 0;
    padding: 0.5rem 0;
}

.sidebar-section h3 {
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.9;
}

/* Button styling */
.stButton > button {
    width: 100%;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-weight: 500;
    font-size: 0.95rem;
    transition: all 0.2s;
    border: 2px solid #ccc !important;
    text-align: left;
}

.stButton > button:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    background-color: rgba(255,255,255,0.2);
}

.stButton > button:active,
.stButton > button:focus {
    color: white !important;
    font-weight: 600 !important;
    border: 2px solid #667eea !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

.stButton > button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
}

[data-testid="stSidebar"] .stButton > button {
    background-color: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: white !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255,255,255,0.2);
}


</style>
""", unsafe_allow_html=True)


def render_empty_state():
    """Render empty state when no algorithm is selected"""
    st.markdown("""
        <div class="empty-state">
            <h2>Select an Algorithm</h2>
            <p>Choose an algorithm from the sidebar to begin</p>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render sidebar with algorithm selection"""
    
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Algorithm Visualizer</div>', unsafe_allow_html=True)
        
        # ==============================================================
        # Chapter 3: Lower Bounds (FIRST in sidebar)
        # ==============================================================
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Chapter 3: Lower Bounds</h3>', unsafe_allow_html=True)
        st.markdown("""
            <div class="info-box" style="font-size: 0.8rem; margin-bottom: 0.8rem;">
            Techniques for proving that no algorithm can solve a problem 
            faster than a certain bound. Covers adversary arguments, 
            reductions, and approximation hardness.
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("MST with Minimum Matching", 
                 use_container_width=True,
                 key="btn_tsp_matching"):
            st.session_state.current_algorithm = "tsp_matching"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bin Packing - Chapter 6
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Chapter 6: Bin Packing</h3>', unsafe_allow_html=True)
        
        if st.button("First Fit", 
                 use_container_width=True,
                 key="btn_first_fit"):
            st.session_state.current_algorithm = "first_fit"
            st.rerun()
        
        if st.button("Best Fit", 
                 use_container_width=True,
                 key="btn_best_fit"):
            st.session_state.current_algorithm = "best_fit"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Euclidean TSP - Chapter 6
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Chapter 6: Euclidean TSP</h3>', unsafe_allow_html=True)
        
        if st.button("Using MST", 
                 use_container_width=True,
                 key="btn_tsp_mst"):
            st.session_state.current_algorithm = "tsp_mst"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Vertex Cover - Chapter 6
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Chapter 6: Vertex Cover</h3>', unsafe_allow_html=True)
        
        if st.button("Vertex Cover", 
                 use_container_width=True,
                 key="btn_vertex_cover"):
            st.session_state.current_algorithm = "vertex_cover"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Network Flow - Chapter 7
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Chapter 7: Network Flow</h3>', unsafe_allow_html=True)
        
        if st.button("Ford-Fulkerson Algorithm", 
                    use_container_width=True,
                    key="btn_ford_fulkerson"):
            st.session_state.current_algorithm = "ford_fulkerson"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ==============================================================
        # Verifiers Section
        # ==============================================================
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Verifiers</h3>', unsafe_allow_html=True)
        
        if st.button("Independent Set",
                 use_container_width=True,
                 key="btn_independent_set"):
            st.session_state.current_algorithm = "independent_set"
            st.rerun()

        if st.button("Satisfiability (SAT)",
                 use_container_width=True,
                 key="btn_satisfiability"):
            st.session_state.current_algorithm = "satisfiability"
            st.rerun()

        if st.button("Hamiltonian Cycle",
                 use_container_width=True,
                 key="btn_hamiltonian"):
            st.session_state.current_algorithm = "hamiltonian_cycle"
            st.rerun()

        if st.button("Element Uniqueness (Closest Pair)",
                 use_container_width=True,
                 key="btn_element_uniqueness"):
            st.session_state.current_algorithm = "element_uniqueness"
            st.rerun()

        if st.button("8-Queens (Backtracking)",
                 use_container_width=True,
                 key="btn_eight_queens"):
            st.session_state.current_algorithm = "eight_queens"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Current status
        if st.session_state.get('current_algorithm'):
            st.markdown("---")
            algo_name = st.session_state.current_algorithm.replace('_', ' ').title()
            st.markdown(f'<strong>Active:</strong><br>{algo_name}', unsafe_allow_html=True)


def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'current_algorithm' not in st.session_state:
        st.session_state.current_algorithm = None
    
    # Render sidebar
    render_sidebar()
    
    # Main content area
    if st.session_state.current_algorithm == "ford_fulkerson":
        # ====================================================================
        # FIXED: Import from your actual directory structure
        # ====================================================================
        # Your structure:
        # algorithms/ford_fulkerson/ui.py
        
        try:
            # Option 1: Import the ui module directly
            from algorithms.ford_fulkerson import ui
            ui.render_ford_fulkerson()
            
            # OR Option 2: Import the function directly
            # from algorithms.ford_fulkerson.ui import render_ford_fulkerson
            # render_ford_fulkerson()
            
        except ImportError as e:
            st.error("Error: Ford-Fulkerson module not found")
            st.code(str(e))
            st.info("""
            **Troubleshooting:**
            
            Make sure you have:
            1. algorithms/ford_fulkerson/__init__.py exists
            2. algorithms/ford_fulkerson/ui.py exists
            3. render_ford_fulkerson() function is in ui.py
            
            Your current structure should be:
            ```
            algorithms/
              ford_fulkerson/
                __init__.py
                ff_core.py
                ff_visualization.py
                ui.py
            ```
            """)
            
            # Show detailed error
            import traceback
            st.error("Full error traceback:")
            st.code(traceback.format_exc())
    
    elif st.session_state.current_algorithm == "first_fit":
        try:
            from algorithms.bin_packing.ui import render_first_fit
            render_first_fit()
        except ImportError as e:
            st.error("Error: Bin packing module not found")
            st.code(str(e))
            
    elif st.session_state.current_algorithm == "best_fit":
        try:
            from algorithms.bin_packing.ui import render_best_fit
            render_best_fit()
        except ImportError as e:
            st.error("Error: Bin packing module not found")
            st.code(str(e))
            
    elif st.session_state.current_algorithm == "tsp_mst":
        try:
            from algorithms.tsp.ui import render_tsp_mst
            render_tsp_mst()
        except ImportError as e:
            st.error("Error: TSP module not found")
            st.code(str(e))
            
    elif st.session_state.current_algorithm == "tsp_matching":
        try:
            from algorithms.tsp.ui import render_tsp_matching
            render_tsp_matching()
        except ImportError as e:
            st.error("Error: TSP module not found")
            st.code(str(e))
            
    elif st.session_state.current_algorithm == "vertex_cover":
        try:
            from algorithms.vertex_cover.ui import render_vertex_cover
            render_vertex_cover()
        except ImportError as e:
            st.error("Error: Vertex Cover module not found")
            st.code(str(e))
            
    elif st.session_state.current_algorithm == "independent_set":
        try:
            from algorithms.verifiers_ui.independent_set import render_independent_set
            render_independent_set()
        except ImportError as e:
            st.error("Error: Independent Set module not found"); st.code(str(e))

    elif st.session_state.current_algorithm == "satisfiability":
        try:
            from algorithms.verifiers_ui.satisfiability import render_satisfiability
            render_satisfiability()
        except ImportError as e:
            st.error("Error: SAT module not found"); st.code(str(e))

    elif st.session_state.current_algorithm == "hamiltonian_cycle":
        try:
            from algorithms.verifiers_ui.hamiltonian_cycle import render_hamiltonian_cycle
            render_hamiltonian_cycle()
        except ImportError as e:
            st.error("Error: Hamiltonian Cycle module not found"); st.code(str(e))

    elif st.session_state.current_algorithm == "element_uniqueness":
        try:
            from algorithms.verifiers_ui.element_uniqueness import render_element_uniqueness
            render_element_uniqueness()
        except ImportError as e:
            st.error("Error: Element Uniqueness module not found"); st.code(str(e))

    elif st.session_state.current_algorithm == "eight_queens":
        try:
            from algorithms.verifiers_ui.eight_queens import render_eight_queens
            render_eight_queens()
        except ImportError as e:
            st.error("Error: 8-Queens module not found"); st.code(str(e))

    else:
        # Show empty state
        render_empty_state()


if __name__ == "__main__":
    main()
