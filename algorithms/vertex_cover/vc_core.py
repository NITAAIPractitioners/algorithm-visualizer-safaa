"""
Vertex Cover Algorithm Core Engine
Implements the 2-approximation Maximal Matching algorithm
"""

import copy
import random
import networkx as nx

class VertexCoverAlgorithm:
    """
    Finds a Vertex Cover using the Maximal Matching 2-Approximation approach:
    1. Initialize VC to empty and E' to E.
    2. Pick an arbitrary edge e = (x, y) in E'.
    3. Add x and y to VC.
    4. Remove all edges incident to x or y from E'.
    5. Repeat 2 through 4 until E' is empty.
    """
    def __init__(self, nodes, edges):
        self.nodes = list(nodes)
        # Store edges uniquely as sorted tuples to avoid direction issues
        self.original_edges = [tuple(sorted((u, v))) for u, v in edges]
        self.steps = []
        
        # Build networkx graph purely to generate a fixed static layout once
        self.G = nx.Graph()
        self.G.add_nodes_from(self.nodes)
        self.G.add_edges_from(self.original_edges)
        
        if len(self.nodes) > 0:
            # We use spring layout with a fixed seed so the graph doesn't jump around visually between steps
            self.pos = nx.spring_layout(self.G, seed=42)
        else:
            self.pos = {}

    def _record_step(self, step_type, current_e_prime, current_vc, active_edge=None, pruned_edges=None, explanation=""):
        """Snapshot the exact state of the variables for the visualizer to render."""
        self.steps.append({
            'type': step_type,
            'pos': self.pos,
            'original_edges': copy.deepcopy(self.original_edges),
            'e_prime': copy.deepcopy(current_e_prime),
            'vc': copy.deepcopy(current_vc),
            'active_edge': active_edge,
            'pruned_edges': list(pruned_edges) if pruned_edges else [],
            'explanation': explanation
        })

    def get_steps(self):
        return self.steps

    def run(self):
        self.steps = []
        
        if not self.nodes:
            self._record_step('complete', [], set(), None, None, "Graph is empty.")
            return set()
            
        if not self.original_edges:
            self._record_step('complete', [], set(), None, None, "No edges in graph, Vertex Cover is empty.")
            return set()

        # Step 1: Initialize
        VC = set()
        E_prime = list(self.original_edges)
        
        self._record_step(
            'init', E_prime, VC, None, None,
            "**Step 1: Initialization**\n\n"
            f"- Define $VC = \\emptyset$ (Vertex Cover is empty).\n"
            f"- Define $E'$ as the set of all {len(E_prime)} active edges.\n\n"
            "We will repeatedly pick edges and add BOTH endpoints into the cover!"
        )

        iteration = 1
        
        while E_prime:
            # Step 2: Pick arbitrary edge
            # For deterministic visualization behavior if needed, we just pick the first one, or random.
            # Picking the first element is functionally arbitrary for this algorithm's bounds.
            e = E_prime[0]
            x, y = e
            
            self._record_step(
                'pick_edge', E_prime, VC, e, None,
                f"**Step 2: Pick an Arbitrary Edge (Iter {iteration})**\n\n"
                f"We select edge **`{x} - {y}`** from $E'$."
            )
            
            # Step 3: Add x and y to VC
            VC.add(x)
            VC.add(y)
            
            self._record_step(
                'add_vertices', E_prime, VC, e, None,
                f"**Step 3: Add Endpoints to VC (Iter {iteration})**\n\n"
                f"We add both **`{x}`** and **`{y}`** to the Vertex Cover."
            )
            
            # Step 4: Remove edges incident to x or y
            pruned_edges = set()
            new_E_prime = []
            
            for edge in E_prime:
                if edge == e:
                    pruned_edges.add(edge)
                elif x in edge or y in edge:
                    pruned_edges.add(edge)
                else:
                    new_E_prime.append(edge)
                    
            # Before actually removing them, show which ones are being targeted
            self._record_step(
                'remove_edges', E_prime, VC, e, pruned_edges,
                f"**Step 4: Remove Covered Edges (Iter {iteration})**\n\n"
                f"Any edge touching **`{x}`** or **`{y}`** is now legally \"covered\" by the $VC$.\n"
                f"We prune {len(pruned_edges)} edges from $E'$."
            )
            
            E_prime = new_E_prime
            iteration += 1

        # Step 5: Complete
        self._record_step(
            'complete', E_prime, VC, None, None,
            "**Algorithm Complete!**\n\n"
            "The active edge set $E'$ is completely empty! Every original edge is touching at least one vertex in our $VC$.\n\n"
            f"**Final VC Size:** {len(VC)} nodes.\n"
            f"**Nodes in VC:** {', '.join(sorted(list(VC)))}"
        )
        
        return VC
