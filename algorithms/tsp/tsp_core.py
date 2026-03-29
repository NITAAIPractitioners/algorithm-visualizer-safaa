"""
Euclidean TSP Algorithms Core Logic
Implements TSP MST (2-approx) and TSP Minimum Matching (1.5-approx Christofides)
"""

import math
import copy
import networkx as nx

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

class EuclideanTSPAlgorithm:
    """Base class for Euclidean TSP to share geometry and step recording logic."""
    def __init__(self, nodes_dict):
        # nodes_dict: { "A": (x, y), "B": (x, y), ... }
        self.nodes_dict = nodes_dict
        self.node_names = list(nodes_dict.keys())
        self.n = len(self.node_names)
        
        # Complete graph (all pairwise distances)
        self.G = nx.Graph()
        for u in self.node_names:
            self.G.add_node(u, pos=self.nodes_dict[u])
            for v in self.node_names:
                if u != v:
                    d = euclidean_distance(self.nodes_dict[u], self.nodes_dict[v])
                    self.G.add_edge(u, v, weight=d)
        
        self.steps = []
        
    def _record_step(self, step_type, current_edges=None, highlighted_edges=None, highlighted_nodes=None, explanation=""):
        """
        Types of steps:
        - 'init': Showing original complete graph or just nodes
        - 'mst': Minimum spanning tree found
        - 'multigraph': Doubled edges (MST alg)
        - 'odd_vertices': Identifying odd vertices (Matching alg)
        - 'matching': Min weight perfect matching (Matching alg)
        - 'eulerian': Eulerian tour traced
        - 'hamiltonian': Final TSP cycle
        
        current_edges: dict or list of edges to draw. Format: {(u, v): count} to track multigraphs.
        """
        if current_edges is None:
            current_edges = {}
        if highlighted_edges is None:
            highlighted_edges = []
        if highlighted_nodes is None:
            highlighted_nodes = []
            
        self.steps.append({
            'type': step_type,
            'nodes': copy.deepcopy(self.nodes_dict),
            'edges': copy.deepcopy(current_edges),  # {(u, v): multiplicity}
            'highlighted_edges': copy.deepcopy(highlighted_edges),
            'highlighted_nodes': copy.deepcopy(highlighted_nodes),
            'explanation': explanation
        })

    def get_steps(self):
        return self.steps
        
    def _get_mst(self):
        """Returns the Minimum Spanning Tree of the complete graph."""
        mst = nx.minimum_spanning_tree(self.G, weight='weight')
        return mst


class TSPMSTAlgorithm(EuclideanTSPAlgorithm):
    """
    TSP Approximation using strictly the Minimum Spanning Tree.
    1. Construct MST T.
    2. Double all edges in T to make multigraph T'.
    3. Find Eulerian tour.
    4. Convert to Hamiltonian.
    """
    def run(self):
        self.steps = []
        
        if self.n <= 1:
            self._record_step('init', {}, [], [], "Not enough nodes to form a tour.")
            return []
            
        # Step 1: Initial state
        self._record_step(
            'init', {}, [], [],
            "**Step 1: Initialization**\n\n"
            f"Given {self.n} cities on a 2D plane.\n"
            "We implicitly assume a complete graph where the distance between any two cities is the straight-line Euclidean distance."
        )
        
        # Step 2: MST
        mst = self._get_mst()
        mst_edges = {(u, v): 1 for u, v in mst.edges()}
        mst_weight = sum(self.G[u][v]['weight'] for u, v in mst.edges())
        
        self._record_step(
            'mst', mst_edges, list(mst.edges()), [],
            "**Step 2: Construct Minimum Spanning Tree**\n\n"
            "We construct a Minimum Spanning Tree (MST) connecting all nodes with the minimum possible total distance.\n"
            f"- MST Weight: {mst_weight:.2f}"
        )
        
        # Step 3: Doubled Edges (Multigraph)
        multi_edges = {}
        for u, v in mst.edges():
            u, v = min(u, v), max(u, v)
            multi_edges[(u, v)] = 2
            
        self._record_step(
            'multigraph', multi_edges, [], [],
            "**Step 3: Double the MST Edges**\n\n"
            "To guarantee that every node has an *even* degree (allowing us to trace a continuous loop), "
            "we create a multigraph by making exactly two copies of every edge in the MST."
        )
        
        # Step 4: Eulerian Tour
        # NetworkX eulerian circuit requires a MultiGraph
        MG = nx.MultiGraph()
        for u in self.node_names:
            MG.add_node(u)
        for (u, v), count in multi_edges.items():
            for _ in range(count):
                MG.add_edge(u, v)
                
        eulerian_circuit = list(nx.eulerian_circuit(MG))
        # trace edges in order
        euler_edges = {}
        ordered_euler_edges = []
        for u, v in eulerian_circuit:
            e = (min(u, v), max(u, v))
            euler_edges[e] = euler_edges.get(e, 0) + 1
            ordered_euler_edges.append((u, v))
            
        self._record_step(
            'eulerian', euler_edges, [], [],
            "**Step 4: Find Eulerian Tour**\n\n"
            "Because every node now has an even degree, we can cleanly trace a path that visits every single *edge* exactly once, returning to the start.\n"
            f"- Edges Traced: {len(eulerian_circuit)}"
        )
        
        # Step 5: Hamiltonian Circuit (Shortcutting)
        visited = set()
        hamiltonian_tour = []
        
        # The circuit returns (u, v). The path of nodes is the first element of each tuple.
        for u, v in eulerian_circuit:
            if u not in visited:
                hamiltonian_tour.append(u)
                visited.add(u)
                
        # Connect back to start
        hamiltonian_tour.append(hamiltonian_tour[0])
        
        final_edges = {}
        final_highlight = []
        tour_weight = 0
        for i in range(len(hamiltonian_tour) - 1):
            u = hamiltonian_tour[i]
            v = hamiltonian_tour[i+1]
            e = (min(u, v), max(u, v))
            final_edges[e] = 1
            final_highlight.append((u, v))
            tour_weight += self.G[u][v]['weight']
            
        self._record_step(
            'hamiltonian', final_edges, final_highlight, [],
            "**Step 5: Convert to Hamiltonian Tour**\n\n"
            "We trace the Eulerian tour, but we **skip** any city we've already visited. Because of the Triangle Inequality (a straight line is always the shortest path), "
            "taking these shortcuts actually makes the overall tour *shorter*! This guarantees our tour is at most 2x the optimal TSP length.\n\n"
            f"**Final Tour Length:** {tour_weight:.2f}\n"
            f"**Path:** {' -> '.join(hamiltonian_tour)}"
        )
        
        return hamiltonian_tour, tour_weight


class TSPMatchingAlgorithm(EuclideanTSPAlgorithm):
    """
    TSP Approximation using Minimum Matching (Christofides 1.5-approx algorithm).
    1. Construct MST T.
    2. Identify set X of odd-degree vertices in T.
    3. Find minimum weight perfect matching MM on X.
    4. T' = T U MM.
    5. Find Eulerian tour.
    6. Convert to Hamiltonian.
    """
    def run(self):
        self.steps = []
        
        if self.n <= 1:
            self._record_step('init', {}, [], [], "Not enough nodes to form a tour.")
            return []
            
        # Step 1: Initial state
        self._record_step(
            'init', {}, [], [],
            "**Step 1: Initialization**\n\n"
            f"Given {self.n} cities on a 2D plane.\n"
            "We implicitly assume a complete graph where the distance between any two cities is the Euclidean straight-line distance."
        )
        
        # Step 2: MST
        mst = self._get_mst()
        mst_edges = {(min(u, v), max(u, v)): 1 for u, v in mst.edges()}
        mst_weight = sum(self.G[u][v]['weight'] for u, v in mst.edges())
        
        self._record_step(
            'mst', dict(mst_edges), list(mst.edges()), [],
            "**Step 2: Construct Minimum Spanning Tree**\n\n"
            "We construct a Minimum Spanning Tree (MST) connecting all nodes with the minimum possible total distance.\n"
            f"- MST Weight: {mst_weight:.2f}"
        )
        
        # Step 3: Odd Vertices
        odd_vertices = [v for v, d in mst.degree() if d % 2 != 0]
        
        self._record_step(
            'odd_vertices', dict(mst_edges), list(mst.edges()), odd_vertices,
            "**Step 3: Identify Odd-Degree Vertices**\n\n"
            "Instead of doubling *all* edges, we only look at cities with an odd number of connections in the MST. "
            "By graph theory rules, there is *always* an even number of these odd-degree vertices.\n"
            f"- Odd Vertices Identified: {len(odd_vertices)}"
        )
        
        # Step 4: Minimum Weight Perfect Matching on X
        odd_subgraph = nx.Graph()
        for i in range(len(odd_vertices)):
            for j in range(i+1, len(odd_vertices)):
                u = odd_vertices[i]
                v = odd_vertices[j]
                # We need the minimum weight matching, so we pass negative weights if using max_weight_matching
                # Or use min_weight_matching directly
                odd_subgraph.add_edge(u, v, weight=self.G[u][v]['weight'])
                
        # networkx min_weight_matching requires a full matching over provided nodes
        # If the version is slightly old, we can do max_weight_matching on negative weights
        # But latest networkx supports min_weight_matching
        matching = nx.min_weight_matching(odd_subgraph, weight='weight')
        
        matching_edges_list = list(matching)
        matching_weight = sum(self.G[u][v]['weight'] for u, v in matching_edges_list)
        
        combined_edges = dict(mst_edges)
        for u, v in matching_edges_list:
            e = (min(u, v), max(u, v))
            combined_edges[e] = combined_edges.get(e, 0) + 1
            
        self._record_step(
            'matching', combined_edges, matching_edges_list, [],
            "**Step 4: Minimum Weight Perfect Matching**\n\n"
            "We pair up these odd vertices in a way that minimizes the total distance added. "
            "Because we only add these specific edges, this is much cheaper than doubling the whole MST!\n"
            f"- Matching Weight Added: {matching_weight:.2f}"
        )
        
        # Step 5: Eulerian Tour on T' = T U MM
        MG = nx.MultiGraph()
        for u in self.node_names:
            MG.add_node(u)
        for (u, v), count in combined_edges.items():
            for _ in range(count):
                MG.add_edge(u, v)
                
        # Find eulerian circuit starting at some node
        eulerian_circuit = list(nx.eulerian_circuit(MG))
        
        euler_edges = {}
        for u, v in eulerian_circuit:
            e = (min(u, v), max(u, v))
            euler_edges[e] = euler_edges.get(e, 0) + 1
            
        self._record_step(
            'eulerian', euler_edges, [], [],
            "**Step 5: Find Eulerian Tour**\n\n"
            "Because every node now has an even degree, we can trace a continuous Eulerian Tour across our combined graph.\n"
            f"- Total Edges in Multigraph: {MG.number_of_edges()}"
        )
        
        # Step 6: Hamiltonian Circuit
        visited = set()
        hamiltonian_tour = []
        
        for u, v in eulerian_circuit:
            if u not in visited:
                hamiltonian_tour.append(u)
                visited.add(u)
                
        hamiltonian_tour.append(hamiltonian_tour[0])
        
        final_edges = {}
        final_highlight = []
        tour_weight = 0
        for i in range(len(hamiltonian_tour) - 1):
            u = hamiltonian_tour[i]
            v = hamiltonian_tour[i+1]
            e = (min(u, v), max(u, v))
            final_edges[e] = 1
            final_highlight.append((u, v))
            tour_weight += self.G[u][v]['weight']
            
        self._record_step(
            'hamiltonian', final_edges, final_highlight, [],
            "**Step 6: Convert to Hamiltonian Tour**\n\n"
            "We trace the Eulerian tour, skipping previously visited cities to create shortcuts. "
            "This Christofides methodology guarantees our tour is at most 1.5x the optimal TSP length!\n\n"
            f"**Final Tour Length:** {tour_weight:.2f}\n"
            f"**Path:** {' -> '.join(hamiltonian_tour)}"
        )
        
        return hamiltonian_tour, tour_weight
