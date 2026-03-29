"""
Element Uniqueness via Closest Pair (Linear Reduction)
Demonstrates the reduction: Element Uniqueness <= Closest Pair
If the closest pair distance is 0, there are duplicates.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
import time

from .independent_set import _render_results_panel


# ==================================================
# CORE LOGIC
# ==================================================

def verify_element_uniqueness(elements):
    """
    Reduce element uniqueness to closest pair on a 1D number line.
    Returns: (all_unique, closest_pair, steps)
    steps follow the same structure as verifiers.py
    """
    steps = []

    steps.append({
        "description": f"Element Uniqueness via Closest Pair Reduction. Input: {elements}",
        "elements": list(elements),
        "sorted_elements": [],
        "pairs_checked": [],
        "closest_pair": None,
        "min_dist": None,
        "phase": "init"
    })

    # Step 1: Sort
    sorted_elems = sorted(enumerate(elements), key=lambda x: x[1])
    sorted_vals = [v for _, v in sorted_elems]

    steps.append({
        "description": f"Step 1 (Reduction): Map each number to a point on a 1D number line. Sort: {sorted_vals}",
        "elements": list(elements),
        "sorted_elements": sorted_vals,
        "pairs_checked": [],
        "closest_pair": None,
        "min_dist": None,
        "phase": "valid"
    })

    # Step 2: Find closest pair (adjacent in sorted order)
    min_dist = math.inf
    closest = None
    pairs_checked = []

    for i in range(len(sorted_vals) - 1):
        u, v = sorted_vals[i], sorted_vals[i + 1]
        dist = abs(v - u)
        pairs_checked.append(((u, v), dist))

        if dist < min_dist:
            min_dist = dist
            closest = (u, v)

        phase = "violation" if dist == 0 else "valid"
        steps.append({
            "description": (
                f"Closest pair check: |{v} - {u}| = {dist:.4g}  "
                + ("-> DUPLICATE FOUND" if dist == 0 else f"-> Running minimum: {min_dist:.4g}")
            ),
            "elements": list(elements),
            "sorted_elements": sorted_vals,
            "pairs_checked": pairs_checked.copy(),
            "closest_pair": (u, v),
            "min_dist": min_dist,
            "phase": phase
        })

    all_unique = (min_dist > 0 and min_dist != math.inf)
    final_msg = (
        f"Closest pair distance = {min_dist:.4g} > 0 -> All {len(elements)} elements are UNIQUE"
        if all_unique
        else f"Closest pair distance = 0 -> DUPLICATES found: {closest}"
    )

    steps.append({
        "description": final_msg,
        "elements": list(elements),
        "sorted_elements": sorted_vals,
        "pairs_checked": pairs_checked,
        "closest_pair": closest,
        "min_dist": min_dist,
        "phase": "complete"
    })

    return all_unique, closest, steps


UNIQUENESS_CODE = '''def element_uniqueness_via_closest_pair(elements):
    """
    Reduce to closest pair: sort, then check adjacent elements.
    If minimum distance == 0, there are duplicates.
    """
    sorted_e = sorted(elements)
    min_dist = float("inf")
    for i in range(len(sorted_e) - 1):
        dist = sorted_e[i+1] - sorted_e[i]
        if dist < min_dist:
            min_dist = dist
    return min_dist > 0  # True = all unique
'''


# ==================================================
# VISUALIZATION
# ==================================================

def render_uniqueness_step(step_data):
    elements = step_data["elements"]
    sorted_elements = step_data.get("sorted_elements", [])
    pairs_checked = step_data.get("pairs_checked", [])
    closest_pair = step_data.get("closest_pair")
    phase = step_data["phase"]

    fig, axes = plt.subplots(2, 1, figsize=(9, 5), gridspec_kw={"height_ratios": [1, 2]})
    fig.patch.set_facecolor("#F8F9FA")

    # Top: original elements
    ax1 = axes[0]
    ax1.set_facecolor("#FFFFFF")
    ax1.set_title("Original Input Elements", fontsize=10, color="#424242", pad=6)
    ax1.set_xlim(-0.5, max(len(elements), 1) - 0.5)
    ax1.set_ylim(-0.5, 1.5)
    ax1.axis("off")
    for i, val in enumerate(elements):
        ax1.text(i, 0.5, str(val), ha="center", va="center", fontsize=12,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#E8EAF6", edgecolor="#7986CB"))

    # Bottom: number line
    ax2 = axes[1]
    ax2.set_facecolor("#FFFFFF")
    ax2.set_title("Sorted 1D Number Line (Closest Pair Search)", fontsize=10, color="#424242", pad=6)

    if sorted_elements:
        mn, mx = min(sorted_elements), max(sorted_elements)
        padding = max(1, (mx - mn) * 0.15)
        ax2.set_xlim(mn - padding, mx + padding)
        ax2.set_ylim(-0.8, 1.5)

        # Draw axis line
        ax2.axhline(0, color="#BDBDBD", linewidth=1.5, zorder=0)

        # Draw checked pair spans
        for (u, v), dist in pairs_checked:
            color = "#FFCDD2" if dist == 0 else "#E8F5E9"
            if closest_pair and set((u, v)) == set(closest_pair):
                color = "#FFCDD2" if dist == 0 else "#C8E6C9"
            ax2.fill_betweenx([-0.2, 0.2], u, v, alpha=0.5, color=color, zorder=1)

        # Draw points
        for val in sorted_elements:
            is_in_closest = closest_pair and val in closest_pair
            color = "#EF5350" if (is_in_closest and phase in ("violation", "complete")) else "#1976D2"
            ax2.plot(val, 0, "o", markersize=12, color=color, zorder=3)
            ax2.text(val, 0.35, str(val), ha="center", va="bottom", fontsize=10, color=color, fontweight="bold")

        if closest_pair and phase != "init":
            u, v = closest_pair
            mid = (u + v) / 2
            dist_val = abs(v - u)
            dist_color = "#C62828" if dist_val == 0 else "#2E7D32"
            ax2.annotate("", xy=(v, -0.4), xytext=(u, -0.4),
                         arrowprops=dict(arrowstyle="<->", color=dist_color, lw=2))
            ax2.text(mid, -0.65, f"d = {dist_val:.4g}", ha="center", color=dist_color, fontsize=10, fontweight="bold")

    ax2.axis("off")
    plt.tight_layout()
    return fig


# ==================================================
# UI
# ==================================================

def init_uniqueness_state():
    if "uniq_elements" not in st.session_state:
        st.session_state.uniq_elements = [4, 2, 7, 1, 9, 3]
    if "uniq_steps" not in st.session_state:
        st.session_state.uniq_steps = []
    if "uniq_step_idx" not in st.session_state:
        st.session_state.uniq_step_idx = 0
    if "uniq_autoplay" not in st.session_state:
        st.session_state.uniq_autoplay = False


def render_element_uniqueness():
    init_uniqueness_state()
    st.markdown("## Element Uniqueness via Closest Pair (Linear Reduction)")

    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Input", "Run Verifier", "Results"])

    with tab1:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.markdown("""
            ### Element Uniqueness and Linear Reduction

            **Element Uniqueness Problem:**
            Given a list of numbers, determine if all elements are distinct.

            **The Reduction:**
            Element Uniqueness can be reduced to the **Closest Pair** problem.
            If the closest pair of points on a 1D number line has distance = 0,
            there must be a duplicate.

            **Algorithm:**
            1. Map each element to a point on a number line.
            2. Sort the elements — O(n log n).
            3. Scan adjacent pairs for the minimum distance — O(n).
            4. If minimum distance = 0, duplicates exist. Otherwise, all are unique.

            **Why this is important:**
            This is a textbook example of a **linear reduction** (Turing reduction):
            solving Element Uniqueness by transforming it into a Closest Pair instance.
            The reduction shows the two problems are computationally equivalent.
            """)
        with col2:
            st.info("""
            **Workflow:**
            1. Input tab (enter numbers)
            2. Run Verifier tab
            3. Results tab
            """)
            st.code(UNIQUENESS_CODE, language="python")

    with tab2:
        st.markdown("### Enter Elements")
        st.caption("Enter up to 20 numbers, comma-separated. Can include duplicates to test.")
        elements_text = st.text_input(
            "Elements",
            value=", ".join(str(e) for e in st.session_state.uniq_elements),
            key="uniq_input"
        )
        try:
            parsed = [float(x.strip()) for x in elements_text.split(",") if x.strip()]
            parsed = parsed[:20]
            if parsed != st.session_state.uniq_elements:
                st.session_state.uniq_elements = parsed
                st.session_state.uniq_steps = []
        except ValueError:
            st.error("Please enter valid numbers separated by commas.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load with Duplicates (test)", use_container_width=True):
                st.session_state.uniq_elements = [3, 7, 1, 7, 5, 2]
                st.session_state.uniq_steps = []
                st.rerun()
        with col2:
            if st.button("Load all Unique (test)", use_container_width=True):
                st.session_state.uniq_elements = [4, 2, 7, 1, 9, 3, 6]
                st.session_state.uniq_steps = []
                st.rerun()

        st.markdown("**Current elements:**")
        st.write(st.session_state.uniq_elements)

    with tab3:
        col1, col2 = st.columns([3, 7])
        with col1:
            st.metric("Count", len(st.session_state.uniq_elements))
        with col2:
            if not st.session_state.uniq_steps:
                if st.button("Run Uniqueness Verifier", type="primary", use_container_width=True):
                    all_unique, closest, steps = verify_element_uniqueness(st.session_state.uniq_elements)
                    st.session_state.uniq_steps = steps
                    st.session_state.uniq_step_idx = 0
                    st.rerun()
            else:
                final = st.session_state.uniq_steps[-1]
                all_unique = final["min_dist"] is not None and final["min_dist"] > 0
                if all_unique:
                    st.success(final["description"])
                else:
                    st.error(final["description"])
                if st.button("Run Again", use_container_width=True):
                    st.session_state.uniq_steps = []
                    st.rerun()

    with tab4:
        _render_results_panel(
            steps_key="uniq_steps",
            idx_key="uniq_step_idx",
            autoplay_key="uniq_autoplay",
            render_fn=render_uniqueness_step
        )
