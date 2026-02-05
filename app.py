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
    border: none;
    text-align: left;
    background-color: rgba(255,255,255,0.1);
}

.stButton > button:hover {
    transform: translateX(5px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    background-color: rgba(255,255,255,0.2);
}

.stButton > button:active,
.stButton > button:focus {
    background-color: rgba(255,255,255,0.25) !important;
    color: white !important;
    font-weight: 600 !important;
    border-left: 4px solid white !important;
    box-shadow: 0 4px 12px rgba(255,255,255,0.2) !important;
}

.stButton > button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    background-color: rgba(255,255,255,0.05);
}

/* Info box */
.info-box {
    background: rgba(255,255,255,0.15);
    border-left: 4px solid white;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
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
        
        # Network Flow
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Network Flow</h3>', unsafe_allow_html=True)
        
        if st.button("Ford-Fulkerson Algorithm", 
                    use_container_width=True,
                    key="btn_ford_fulkerson"):
            st.session_state.current_algorithm = "ford_fulkerson"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Bin Packing
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Bin Packing Problem</h3>', unsafe_allow_html=True)
        
        st.button("First Fit", 
                 use_container_width=True,
                 disabled=True,
                 key="btn_first_fit")
        
        st.button("Best Fit", 
                 use_container_width=True,
                 disabled=True,
                 key="btn_best_fit")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Traveling Salesman
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Euclidean TSP</h3>', unsafe_allow_html=True)
        
        st.button("Using MST", 
                 use_container_width=True,
                 disabled=True,
                 key="btn_tsp_mst")
        
        st.button("MST with Minimum Matching", 
                 use_container_width=True,
                 disabled=True,
                 key="btn_tsp_matching")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Vertex Cover
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<h3>Graph Problems</h3>', unsafe_allow_html=True)
        
        st.button("Vertex Cover", 
                 use_container_width=True,
                 disabled=True,
                 key="btn_vertex_cover")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Current status
        if st.session_state.get('current_algorithm'):
            st.markdown("---")
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            algo_name = st.session_state.current_algorithm.replace('_', ' ').title()
            st.markdown(f'<strong>Active:</strong><br>{algo_name}', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


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
    
    else:
        # Show empty state
        render_empty_state()


if __name__ == "__main__":
    main()
