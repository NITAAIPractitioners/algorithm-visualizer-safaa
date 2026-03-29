"""
Satisfiability (SAT) Verifier
Verifies if a variable assignment satisfies all clauses of a CNF formula.
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import time

from .independent_set import _render_results_panel


# ==================================================
# CORE LOGIC
# ==================================================

def verify_sat(variables, clauses, assignment):
    """
    Verify if the assignment satisfies all CNF clauses.
    clauses: list of lists of literals, e.g. [["X1", "NOT X2"], ["X2", "X3"]]
    assignment: dict of {variable: True/False}
    Returns: (is_valid, unsatisfied, steps)
    """
    steps = []
    unsatisfied = []

    steps.append({
        "description": f"Verifying SAT assignment for {len(clauses)} clause(s) over {len(variables)} variable(s)",
        "variables": variables,
        "clauses": clauses,
        "assignment": dict(assignment),
        "current_clause_idx": None,
        "unsatisfied": [],
        "phase": "init"
    })

    for i, clause in enumerate(clauses):
        clause_value = False
        eval_details = []

        for literal in clause:
            if literal.startswith("NOT "):
                var = literal[4:]
                val = not assignment.get(var, False)
            else:
                var = literal
                val = assignment.get(var, False)
            eval_details.append(f"{literal}={val}")
            if val:
                clause_value = True

        if not clause_value:
            unsatisfied.append(i)
            steps.append({
                "description": f"Clause {i + 1} ({' OR '.join(clause)}): UNSATISFIED  [{', '.join(eval_details)}]",
                "variables": variables,
                "clauses": clauses,
                "assignment": dict(assignment),
                "current_clause_idx": i,
                "unsatisfied": unsatisfied.copy(),
                "phase": "violation"
            })
        else:
            steps.append({
                "description": f"Clause {i + 1} ({' OR '.join(clause)}): SATISFIED  [{', '.join(eval_details)}]",
                "variables": variables,
                "clauses": clauses,
                "assignment": dict(assignment),
                "current_clause_idx": i,
                "unsatisfied": unsatisfied.copy(),
                "phase": "valid"
            })

    is_valid = len(unsatisfied) == 0
    final_msg = (
        "All clauses satisfied - formula is SATISFIABLE"
        if is_valid
        else f"Formula is UNSATISFIABLE: {len(unsatisfied)} clause(s) not satisfied"
    )

    steps.append({
        "description": final_msg,
        "variables": variables,
        "clauses": clauses,
        "assignment": dict(assignment),
        "current_clause_idx": None,
        "unsatisfied": unsatisfied,
        "phase": "complete"
    })

    return is_valid, unsatisfied, steps


SAT_CODE = '''def verify_sat(clauses, assignment):
    """Check if assignment satisfies every clause in CNF formula."""
    for clause in clauses:
        clause_satisfied = False
        for literal in clause:
            if literal.startswith("NOT "):
                val = not assignment[literal[4:]]
            else:
                val = assignment[literal]
            if val:
                clause_satisfied = True
                break
        if not clause_satisfied:
            return False  # At least one clause is unsatisfied
    return True
'''


# ==================================================
# VISUALIZATION
# ==================================================

def render_sat_step(step_data):
    clauses = step_data["clauses"]
    assignment = step_data["assignment"]
    unsatisfied = set(step_data.get("unsatisfied", []))
    current = step_data.get("current_clause_idx")
    phase = step_data["phase"]

    n = len(clauses)
    fig, ax = plt.subplots(figsize=(9, max(4, n * 0.7 + 1.5)))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#FFFFFF")
    ax.axis("off")

    # Header
    header = "  |  ".join([f"{v}={'T' if assignment.get(v) else 'F'}" for v in step_data["variables"]])
    ax.text(0.5, 1.02, f"Assignment:  {header}", ha="center", va="bottom",
            transform=ax.transAxes, fontsize=10, color="#424242",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#E8EAF6", edgecolor="#9FA8DA"))

    row_height = 1.0 / max(n, 1)
    for i, clause in enumerate(clauses):
        y = 1.0 - (i + 0.5) * row_height
        is_current = (i == current)
        is_unsat = (i in unsatisfied)

        if is_unsat:
            bg_color = "#FFCDD2"
            text_color = "#B71C1C"
            label = "FAIL"
        elif is_current and phase == "valid":
            bg_color = "#C8E6C9"
            text_color = "#1B5E20"
            label = "PASS"
        elif is_current:
            bg_color = "#E3F2FD"
            text_color = "#0D47A1"
            label = "Checking"
        else:
            bg_color = "#F5F5F5"
            text_color = "#616161"
            label = ""

        clause_str = " OR ".join(clause)
        ax.text(0.05, y, f"Clause {i + 1}: ( {clause_str} )", va="center", ha="left",
                fontsize=11, color=text_color,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_color, edgecolor="#BDBDBD", linewidth=1.5),
                transform=ax.transAxes)
        if label:
            ax.text(0.92, y, label, va="center", ha="center", fontsize=10,
                    fontweight="bold", color=text_color, transform=ax.transAxes)

    legend = [
        mpatches.Patch(color="#C8E6C9", label="Satisfied"),
        mpatches.Patch(color="#FFCDD2", label="Unsatisfied"),
        mpatches.Patch(color="#E3F2FD", label="Currently Checking"),
    ]
    ax.legend(handles=legend, loc="lower right", fontsize=8, framealpha=0.9, bbox_to_anchor=(1, 0))
    plt.tight_layout()
    return fig


# ==================================================
# UI
# ==================================================

def _default_clauses():
    return [["X1", "NOT X2"], ["X2", "X3"], ["NOT X1", "NOT X3"]]


def init_sat_state():
    if "sat_variables" not in st.session_state:
        st.session_state.sat_variables = ["X1", "X2", "X3"]
    if "sat_clauses" not in st.session_state:
        st.session_state.sat_clauses = _default_clauses()
    if "sat_assignment" not in st.session_state:
        st.session_state.sat_assignment = {"X1": True, "X2": False, "X3": True}
    if "sat_steps" not in st.session_state:
        st.session_state.sat_steps = []
    if "sat_step_idx" not in st.session_state:
        st.session_state.sat_step_idx = 0
    if "sat_autoplay" not in st.session_state:
        st.session_state.sat_autoplay = False


def render_satisfiability():
    init_sat_state()
    st.markdown("## Satisfiability (SAT) Verifier")

    tab1, tab2, tab3, tab4 = st.tabs(["Introduction", "Build Formula", "Run Verifier", "Results"])

    with tab1:
        col1, col2 = st.columns([7, 3])
        with col1:
            st.markdown("""
            ### Boolean Satisfiability Problem (SAT)

            Given a Boolean formula in **Conjunctive Normal Form (CNF)** — a conjunction (AND) of
            one or more **clauses**, where each clause is a disjunction (OR) of **literals** —
            does there exist an assignment of True/False to variables that makes the formula True?

            **Example CNF Formula:**
            ```
            (X1 OR NOT X2) AND (X2 OR X3) AND (NOT X1 OR NOT X3)
            ```

            **Verification Process:**
            1. Take a proposed True/False assignment for each variable.
            2. For each clause, evaluate whether at least one literal is True.
            3. If ALL clauses are satisfied, the assignment is a valid solution.
            4. If ANY clause evaluates to False, the assignment fails.

            **Why it matters:**
            SAT was the first problem proven to be NP-Complete (Cook-Levin theorem, 1971).
            """)
        with col2:
            st.info("""
            **Workflow:**
            1. Build Formula tab
            2. Set variable assignments
            3. Run Verifier tab
            4. Results tab
            """)
            st.code(SAT_CODE, language="python")

    with tab2:
        col1, col2 = st.columns([5, 5])

        with col1:
            st.markdown("### Variables")
            vars_input = st.text_input(
                "Variables (comma-separated)",
                value=", ".join(st.session_state.sat_variables),
                key="sat_vars_input"
            )
            new_vars = [v.strip() for v in vars_input.split(",") if v.strip()]
            if new_vars != st.session_state.sat_variables:
                st.session_state.sat_variables = new_vars
                st.session_state.sat_assignment = {v: False for v in new_vars}
                st.session_state.sat_steps = []

            st.markdown("### Assignment")
            for v in st.session_state.sat_variables:
                st.session_state.sat_assignment[v] = st.checkbox(
                    f"{v} = True", value=st.session_state.sat_assignment.get(v, False), key=f"sat_assign_{v}"
                )

        with col2:
            st.markdown("### Clauses (CNF)")
            st.caption("Each clause is a list of literals. Use NOT X1 for negation.")

            clause_texts = []
            for i, clause in enumerate(st.session_state.sat_clauses):
                default_text = ", ".join(clause)
                text = st.text_input(f"Clause {i + 1}", value=default_text, key=f"sat_clause_{i}")
                clause_texts.append([lit.strip() for lit in text.split(",") if lit.strip()])

            c_add, c_rem = st.columns(2)
            with c_add:
                if st.button("Add Clause", use_container_width=True):
                    clause_texts.append(["X1"])
            with c_rem:
                if st.button("Remove Last", use_container_width=True, disabled=len(clause_texts) <= 1):
                    clause_texts = clause_texts[:-1]

            if clause_texts != st.session_state.sat_clauses:
                st.session_state.sat_clauses = clause_texts
                st.session_state.sat_steps = []
                st.rerun()

    with tab3:
        col1, col2 = st.columns([3, 7])
        with col1:
            st.metric("Variables", len(st.session_state.sat_variables))
            st.metric("Clauses", len(st.session_state.sat_clauses))
        with col2:
            if not st.session_state.sat_steps:
                if st.button("Run SAT Verifier", type="primary", use_container_width=True):
                    _, _, steps = verify_sat(
                        st.session_state.sat_variables,
                        st.session_state.sat_clauses,
                        st.session_state.sat_assignment
                    )
                    st.session_state.sat_steps = steps
                    st.session_state.sat_step_idx = 0
                    st.rerun()
            else:
                final = st.session_state.sat_steps[-1]
                if not final["unsatisfied"]:
                    st.success(final["description"])
                else:
                    st.error(final["description"])
                if st.button("Run Again", use_container_width=True):
                    st.session_state.sat_steps = []
                    st.rerun()

    with tab4:
        _render_results_panel(
            steps_key="sat_steps",
            idx_key="sat_step_idx",
            autoplay_key="sat_autoplay",
            render_fn=render_sat_step
        )
