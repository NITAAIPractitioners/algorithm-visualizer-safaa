"""
8-Queens Problem (Backtracking)
Visualizes the backtracking search for placing 8 non-attacking queens on a chessboard.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time

from .independent_set import _render_results_panel


# ==================================================
# CORE LOGIC
# ==================================================

def solve_eight_queens(n=8, stop_at_solution=1):
    """
    Solve N-Queens using backtracking.
    Records every placement, backtrack, and solution step.
    Returns: (solutions, steps)
    steps follow the same structure as verifiers.py
    """
    steps = []
    solutions = []
    board = [-1] * n  # board[col] = row of queen in that column

    steps.append({
        "description": f"Starting backtracking search for {n}-Queens problem",
        "board": list(board),
        "n": n,
        "current_col": 0,
        "conflict_cells": [],
        "solutions_found": 0,
        "phase": "init"
    })

    def is_safe(board, col, row):
        for c in range(col):
            r = board[c]
            if r == row or abs(r - row) == abs(c - col):
                return False
        return True

    def get_conflicts(board, col, row):
        conflicts = []
        for c in range(col):
            r = board[c]
            if r == row or abs(r - row) == abs(c - col):
                conflicts.append((r, c))
        return conflicts

    def backtrack(col):
        if len(solutions) >= stop_at_solution and stop_at_solution > 0:
            return
        if col == n:
            solutions.append(list(board))
            steps.append({
                "description": f"Solution {len(solutions)} found! All {n} queens placed without conflicts.",
                "board": list(board),
                "n": n,
                "current_col": col,
                "conflict_cells": [],
                "solutions_found": len(solutions),
                "phase": "complete" if len(solutions) >= stop_at_solution else "valid"
            })
            return

        for row in range(n):
            if len(solutions) >= stop_at_solution and stop_at_solution > 0:
                return
            conflicts = get_conflicts(board, col, row)

            if not conflicts:
                board[col] = row
                steps.append({
                    "description": f"Place queen at column {col + 1}, row {row + 1} - no conflicts",
                    "board": list(board),
                    "n": n,
                    "current_col": col,
                    "conflict_cells": [],
                    "solutions_found": len(solutions),
                    "phase": "valid"
                })
                backtrack(col + 1)
                if len(solutions) >= stop_at_solution and stop_at_solution > 0:
                    return
                board[col] = -1
                steps.append({
                    "description": f"Backtrack from column {col + 1}, row {row + 1} - trying next row",
                    "board": list(board),
                    "n": n,
                    "current_col": col,
                    "conflict_cells": [],
                    "solutions_found": len(solutions),
                    "phase": "violation"
                })
            else:
                steps.append({
                    "description": f"Conflict at column {col + 1}, row {row + 1} - queens at {[(r+1, c+1) for r, c in conflicts]} attack this position",
                    "board": list(board),
                    "n": n,
                    "current_col": col,
                    "conflict_cells": [(row, col)] + conflicts,
                    "solutions_found": len(solutions),
                    "phase": "violation"
                })

    backtrack(0)
    return solutions, steps


EIGHT_QUEENS_CODE = '''def is_safe(board, col, row):
    for c in range(col):
        r = board[c]
        if r == row or abs(r - row) == abs(c - col):
            return False
    return True

def solve_n_queens(n=8):
    board = [-1] * n
    solutions = []

    def backtrack(col):
        if col == n:
            solutions.append(board.copy())
            return
        for row in range(n):
            if is_safe(board, col, row):
                board[col] = row
                backtrack(col + 1)
                board[col] = -1  # Backtrack

    backtrack(0)
    return solutions  # 92 solutions for n=8
'''


# ==================================================
# VISUALIZATION
# ==================================================

def render_queens_step(step_data):
    board = step_data["board"]
    n = step_data.get("n", 8)
    conflict_cells = set(tuple(c) for c in step_data.get("conflict_cells", []))
    phase = step_data["phase"]

    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#FFFFFF")

    # Draw checkerboard
    for row in range(n):
        for col in range(n):
            light = (row + col) % 2 == 0
            color = "#F0D9B5" if light else "#B58863"
            ax.add_patch(mpatches.Rectangle((col, n - 1 - row), 1, 1, color=color, zorder=0))

    # Highlight conflict cells
    for (row, col) in conflict_cells:
        ax.add_patch(mpatches.Rectangle((col, n - 1 - row), 1, 1,
                                        color="#EF5350", alpha=0.6, zorder=1))

    # Draw queens
    for col in range(n):
        row = board[col]
        if row >= 0:
            is_conflict = any(c == col for _, c in conflict_cells)
            q_color = "#C62828" if is_conflict else "#1565C0"
            ax.text(col + 0.5, n - 1 - row + 0.5, "Q", ha="center", va="center",
                    fontsize=18, fontweight="bold", color=q_color, zorder=3)

    ax.set_xlim(0, n)
    ax.set_ylim(0, n)
    ax.set_xticks(range(n))
    ax.set_xticklabels([str(i + 1) for i in range(n)], fontsize=8)
    ax.set_yticks(range(n))
    ax.set_yticklabels([str(n - i) for i in range(n)], fontsize=8)
    ax.tick_params(length=0)
    ax.set_frame_on(True)

    phase_colors = {"init": "#1565C0", "valid": "#2E7D32", "violation": "#C62828", "complete": "#6A1B9A"}
    placed = sum(1 for r in board if r >= 0)
    ax.set_title(f"Queens placed: {placed}/{n}  |  Solutions found: {step_data.get('solutions_found', 0)}",
                 fontsize=10, color=phase_colors.get(phase, "#424242"), pad=8)

    for spine in ax.spines.values():
        spine.set_color("#424242")

    plt.tight_layout()
    return fig


# ==================================================
# UI
# ==================================================

def init_queens_state():
    if "queens_n" not in st.session_state:
        st.session_state.queens_n = 8
    if "queens_steps" not in st.session_state:
        st.session_state.queens_steps = []
    if "queens_step_idx" not in st.session_state:
        st.session_state.queens_step_idx = 0
    if "queens_autoplay" not in st.session_state:
        st.session_state.queens_autoplay = False
    if "queens_solutions" not in st.session_state:
        st.session_state.queens_solutions = []


def render_eight_queens():
    init_queens_state()
    st.markdown("## Backtracking: N-Queens Problem")

    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Configuration", "Run Solver", "Results"])

    with tab1:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.markdown("""
            ### N-Queens Backtracking Problem

            Place N queens on an N x N chessboard such that no two queens
            attack each other. Two queens attack each other if they share the same
            row, column, or diagonal.

            **Backtracking Algorithm:**
            1. Place a queen in column 1, trying each row from top to bottom.
            2. For each placement, check if it conflicts with any previously placed queen.
            3. If no conflict, move to the next column and repeat.
            4. If all rows in a column fail, **backtrack** to the previous column
               and try the next row there.
            5. Repeat until all N queens are placed (one solution found) or all
               possibilities are exhausted.

            **Known Results:**
            - 8-Queens: 92 distinct solutions exist.
            - The solver will animate step-by-step, including every backtrack.

            **Note on steps:** The full backtracking tree can be very long.
            For N=8, there are thousands of steps. Use a smaller N (4-6) to
            see a compact, clear animation.
            """)
        with col2:
            st.info("""
            **Workflow:**
            1. Configuration tab (choose N)
            2. Run Solver tab
            3. Results tab (watch backtracking)
            """)
            st.code(EIGHT_QUEENS_CODE, language="python")

    with tab2:
        st.markdown("### Board Configuration")
        n = st.slider("Board size (N)", min_value=4, max_value=8, value=st.session_state.queens_n,
                      key="queens_n_slider")
        if n != st.session_state.queens_n:
            st.session_state.queens_n = n
            st.session_state.queens_steps = []
            st.session_state.queens_solutions = []

        st.info(f"For N={n}, the solver will record every placement and backtrack step.")
        st.markdown("---")
        expected = {4: 2, 5: 10, 6: 4, 7: 40, 8: 92}
        st.metric("Known solutions", expected.get(n, "?"))

    with tab3:
        col1, col2 = st.columns([3, 7])
        with col1:
            st.metric("Board Size", f"{st.session_state.queens_n} x {st.session_state.queens_n}")
        with col2:
            if not st.session_state.queens_steps:
                if st.button("Run N-Queens Backtracking Solver", type="primary", use_container_width=True):
                    with st.spinner("Running backtracking search..."):
                        solutions, steps = solve_eight_queens(
                            n=st.session_state.queens_n,
                            stop_at_solution=1  # Show first solution journey only
                        )
                        st.session_state.queens_steps = steps
                        st.session_state.queens_solutions = solutions
                        st.session_state.queens_step_idx = 0
                    st.rerun()
            else:
                n_sol = len(st.session_state.queens_solutions)
                n_steps = len(st.session_state.queens_steps)
                if n_sol > 0:
                    st.success(f"First solution found! Total steps recorded: {n_steps}")
                else:
                    st.warning(f"No solution found ({n_steps} steps recorded)")
                if st.button("Run Again", use_container_width=True):
                    st.session_state.queens_steps = []
                    st.session_state.queens_solutions = []
                    st.rerun()

    with tab4:
        _render_results_panel(
            steps_key="queens_steps",
            idx_key="queens_step_idx",
            autoplay_key="queens_autoplay",
            render_fn=render_queens_step
        )
