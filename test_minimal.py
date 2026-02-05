"""
Minimal Test App
Put this in your project root and run: streamlit run test_minimal.py
"""

import streamlit as st

st.set_page_config(page_title="Minimal Test", layout="wide")

st.title("🧪 Minimal Test")

st.write("Step 1: Testing import...")

try:
    from algorithms.ford_fulkerson.ui import render_ford_fulkerson
    st.success("✅ Import successful!")
    
    st.write("Step 2: Testing function call...")
    render_ford_fulkerson()
    
except Exception as e:
    st.error(f"❌ Error: {e}")
    import traceback
    st.code(traceback.format_exc())