"""
Ford-Fulkerson Algorithm - Core Logic (No UI)
Pure algorithm implementation separated from Streamlit UI
"""

from collections import defaultdict, deque
import copy


# ============================================================================
# GRAPH DATA STRUCTURES & VALIDATION
# ============================================================================

class GraphValidator:
    """Validates graph structure before processing"""
    
    @staticmethod
    def validate(graph_data):
        """
        Validate graph structure
        
        Args:
            graph_data: Dictionary with keys: nodes, edges, source, sink
        
        Returns:
            (is_valid, error_message)
        """
        # Check source and sink
        if not graph_data.get("source") or not graph_data.get("sink"):
            return False, "Source or sink node not specified"
        
        source = graph_data["source"]
        sink = graph_data["sink"]
        
        # Check if source and sink are different
        if source == sink:
            return False, "Source and sink must be different nodes"
        
        # Check if source and sink exist in nodes
        nodes = set(graph_data.get("nodes", []))
        if source not in nodes:
            return False, f"Source node '{source}' not found in graph"
        if sink not in nodes:
            return False, f"Sink node '{sink}' not found in graph"
        
        # Check edges
        edges = graph_data.get("edges", [])
        if not edges:
            return False, "Graph has no edges"
        
        # Validate each edge
        for edge in edges:
            if len(edge) == 3:
                u, v, capacity = edge
                initial_flow = 0
            elif len(edge) == 4:
                u, v, capacity, initial_flow = edge
            else:
                return False, f"Invalid edge format: {edge}"
            
            # Check nodes exist
            if u not in nodes:
                return False, f"Edge references unknown node: {u}"
            if v not in nodes:
                return False, f"Edge references unknown node: {v}"
            
            # Check capacity is positive
            if capacity <= 0:
                return False, f"Edge ({u}, {v}) has non-positive capacity: {capacity}"
            
            # Check initial flow is valid
            if initial_flow < 0:
                return False, f"Edge ({u}, {v}) has negative initial flow: {initial_flow}"
            if initial_flow > capacity:
                return False, f"Edge ({u}, {v}) has flow ({initial_flow}) exceeding capacity ({capacity})"
        
        return True, "Graph is valid"


class GraphBuilder:
    """Builds graph data structures from edge lists"""
    
    @staticmethod
    def from_edges(edges_list):
        """
        Convert edge list to adjacency dictionary
        
        Args:
            edges_list: [(u, v, capacity), ...] or [(u, v, capacity, initial_flow), ...]
        
        Returns:
            (graph, initial_flow_dict)
        """
        graph = defaultdict(lambda: defaultdict(int))
        flow = defaultdict(lambda: defaultdict(int))
        
        for edge in edges_list:
            if len(edge) == 3:
                u, v, capacity = edge
                initial_flow = 0
            else:  # len(edge) == 4
                u, v, capacity, initial_flow = edge
            
            graph[u][v] = capacity
            flow[u][v] = initial_flow
        
        return graph, flow


# ============================================================================
# EXAMPLE GRAPHS DATABASE
# ============================================================================

class ExampleGraphs:
    """Pre-built example graphs for testing and demonstration"""
    
    @staticmethod
    def get_all():
        """Return dictionary of all example graphs"""
        return {
            "Your Network - With Initial Flows (7 nodes)": {
                "description": "Network showing mid-computation state (will reset to 0 internally)",
                "nodes": ["s", "a", "b", "c", "d", "e", "t"],
                "edges": [
                    ("s", "a", 6, 4),
                    ("s", "c", 10, 2),
                    ("s", "b", 12, 0),
                    ("a", "d", 10, 4),
                    ("a", "c", 8, 0),
                    ("b", "c", 5, 0),
                    ("b", "e", 6, 0),
                    ("c", "d", 6, 2),
                    ("c", "e", 6, 0),
                    ("d", "e", 6, 0),
                    ("d", "t", 7, 6),
                    ("e", "t", 12, 0)
                ],
                "source": "s",
                "sink": "t",
                "initial_flow": 6,
                "expected_max_flow": 19
            },
            
            "Your Network - Zero Flows (7 nodes)": {
                "description": "Same network starting from zero",
                "nodes": ["s", "a", "b", "c", "d", "e", "t"],
                "edges": [
                    ("s", "a", 6, 0),
                    ("s", "c", 10, 0),
                    ("s", "b", 12, 0),
                    ("a", "d", 10, 0),
                    ("a", "c", 8, 0),
                    ("b", "c", 5, 0),
                    ("b", "e", 6, 0),
                    ("c", "d", 6, 0),
                    ("c", "e", 6, 0),
                    ("d", "e", 6, 0),
                    ("d", "t", 7, 0),
                    ("e", "t", 12, 0)
                ],
                "source": "s",
                "sink": "t",
                "initial_flow": 0,
                "expected_max_flow": 19
            },
            
            "Textbook Network (6 nodes)": {
                "description": "Classic Ford-Fulkerson example",
                "nodes": ["s", "a", "b", "c", "d", "t"],
                "edges": [
                    ("s", "a", 16, 0),
                    ("s", "b", 13, 0),
                    ("a", "b", 10, 0),
                    ("a", "c", 12, 0),
                    ("b", "c", 4, 0),
                    ("b", "d", 14, 0),
                    ("c", "d", 9, 0),
                    ("c", "t", 20, 0),
                    ("d", "t", 4, 0)
                ],
                "source": "s",
                "sink": "t",
                "initial_flow": 0,
                "expected_max_flow": None
            },
            
            "Diamond Network (4 nodes)": {
                "description": "Simple diamond network - perfect for testing",
                "nodes": ["s", "1", "2", "t"],
                "edges": [
                    ("s", "1", 2, 0),
                    ("s", "2", 4, 0),
                    ("1", "t", 1, 0),
                    ("1", "2", 3, 0),
                    ("2", "t", 5, 0)
                ],
                "source": "s",
                "sink": "t",
                "initial_flow": 0,
                "expected_max_flow": 6
            }
        }


# ============================================================================
# FORD-FULKERSON ALGORITHM CORE
# ============================================================================

class PathFinder:
    """Finds augmenting paths in residual graphs"""
    
    @staticmethod
    def bfs_find_path(residual_graph, source, sink):
        """
        Use BFS to find an augmenting path (forward edges only)
        
        Args:
            residual_graph: Graph with remaining capacities
            source: Source node
            sink: Sink node
        
        Returns:
            (path_exists, parent_dict)
        """
        parent = {source: None}
        visited = set([source])
        queue = deque([source])
        
        while queue:
            u = queue.popleft()
            
            if u == sink:
                return True, parent
            
            if u in residual_graph:
                for v in residual_graph[u]:
                    if v not in visited and residual_graph[u][v] > 0:
                        visited.add(v)
                        parent[v] = u
                        queue.append(v)
        
        return False, parent
    
    @staticmethod
    def reconstruct_path(parent, source, sink):
        """
        Reconstruct path from source to sink
        
        Args:
            parent: Dictionary from BFS
            source: Source node
            sink: Sink node
        
        Returns:
            List of nodes representing the path
        """
        path = []
        current = sink
        
        while current is not None:
            path.append(current)
            current = parent.get(current)
        
        path.reverse()
        return path
    
    @staticmethod
    def compute_bottleneck(path, residual_graph):
        """
        Compute bottleneck capacity along a path
        
        Args:
            path: List of nodes in the path
            residual_graph: Graph with remaining capacities
        
        Returns:
            Minimum capacity along the path
        """
        bottleneck = float('inf')
        
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            bottleneck = min(bottleneck, residual_graph[u][v])
        
        return bottleneck


class ResidualGraph:
    """Manages residual graph computation"""
    
    @staticmethod
    def compute(graph, flow):
        """
        Compute residual graph using ONLY forward edges
        
        Args:
            graph: Original graph with capacities
            flow: Current flow
        
        Returns:
            Residual graph (only forward edges with remaining capacity)
        """
        residual = defaultdict(lambda: defaultdict(int))
        
        # Add ONLY forward edges with remaining capacity
        for u in graph:
            for v in graph[u]:
                capacity = graph[u][v]
                current_flow = flow[u][v] if u in flow and v in flow[u] else 0
                remaining = capacity - current_flow
                
                if remaining > 0:
                    residual[u][v] = remaining
        
        return residual


class MinimumCut:
    """Computes minimum cut after algorithm terminates"""
    
    @staticmethod
    def find(graph, flow, source):
        """
        Find minimum cut using ONLY forward edges
        
        Args:
            graph: Original graph with capacities
            flow: Final flow
            source: Source node
        
        Returns:
            (cut_edges, source_partition, sink_partition, cut_value)
        """
        # Build residual graph
        residual = ResidualGraph.compute(graph, flow)
        
        # BFS from source
        reachable = set([source])
        queue = deque([source])
        
        while queue:
            u = queue.popleft()
            
            if u in residual:
                for v in residual[u]:
                    if residual[u][v] > 0 and v not in reachable:
                        reachable.add(v)
                        queue.append(v)
        
        # Get all nodes
        all_nodes = set()
        for u in graph:
            all_nodes.add(u)
            for v in graph[u]:
                all_nodes.add(v)
        
        source_partition = reachable
        sink_partition = all_nodes - reachable
        
        # Calculate cut value using ORIGINAL graph capacities
        cut_edges = []
        cut_value = 0
        
        for u in source_partition:
            if u in graph:
                for v in graph[u]:
                    if v in sink_partition:
                        cut_edges.append((u, v))
                        cut_value += graph[u][v]
        
        return cut_edges, source_partition, sink_partition, cut_value


class FordFulkersonAlgorithm:
    """
    Ford-Fulkerson Algorithm using FORWARD EDGES ONLY
    
    Pure algorithm implementation - no UI dependencies
    """
    
    def __init__(self, graph, source, sink):
        """
        Initialize the algorithm
        
        Args:
            graph: Original graph (adjacency dict with capacities)
            source: Source node
            sink: Sink node
        """
        self.original_graph = copy.deepcopy(graph)
        self.source = source
        self.sink = sink
        
        # Initialize all flows to zero
        self.flow = defaultdict(lambda: defaultdict(int))
        for u in graph:
            for v in graph[u]:
                self.flow[u][v] = 0
        
        # For recording steps
        self.steps = []
    
    def run(self):
        """
        Execute Ford-Fulkerson algorithm
        
        Returns:
            Maximum flow value
        """
        max_flow = 0
        iteration = 0
        
        # Record initial state
        residual = ResidualGraph.compute(self.original_graph, self.flow)
        self.steps.append({
            'type': 'initial',
            'iteration': 0,
            'flow': copy.deepcopy(self.flow),
            'residual': copy.deepcopy(residual),
            'path': None,
            'bottleneck': 0,
            'max_flow': 0,
            'explanation': (
                "**Step 1-2: Initialize**\n\n"
                "• Residual graph R ← Original graph G\n"
                "• All flows ← 0\n\n"
                f"Source: {self.source}, Sink: {self.sink}\n\n"
                "**Note**: Using FORWARD EDGES ONLY (no backward edges)"
            )
        })
        
        # Main loop
        while True:
            iteration += 1
            
            # Build current residual graph
            residual = ResidualGraph.compute(self.original_graph, self.flow)
            
            # Find augmenting path
            path_exists, parent = PathFinder.bfs_find_path(residual, self.source, self.sink)
            
            # Stop when no path exists
            if not path_exists:
                # Compute minimum cut
                cut_edges, S, T, cut_capacity = MinimumCut.find(
                    self.original_graph, self.flow, self.source
                )
                
                self.steps.append({
                    'type': 'complete',
                    'iteration': iteration,
                    'flow': copy.deepcopy(self.flow),
                    'residual': copy.deepcopy(residual),
                    'path': None,
                    'bottleneck': 0,
                    'max_flow': max_flow,
                    'min_cut_edges': cut_edges,
                    'source_partition': S,
                    'sink_partition': T,
                    'cut_value': cut_capacity,
                    'explanation': (
                        "**Algorithm Complete**\n\n"
                        "No forward-only augmenting path exists\n\n"
                        f"**Final Flow Value: {max_flow}**\n\n"
                        f"**Minimum Cut:**\n"
                        f"• S = {{{', '.join(sorted(S))}}}\n"
                        f"• T = {{{', '.join(sorted(T))}}}\n"
                        f"• Cut edges: {cut_edges}\n"
                        f"• Cut capacity: {cut_capacity}\n\n"
                        f"**Verification: {max_flow} = {cut_capacity} "
                        f"{'✓' if max_flow == cut_capacity else '✗'}**"
                    )
                })
                break
            
            # Reconstruct the path
            path = PathFinder.reconstruct_path(parent, self.source, self.sink)
            
            # Compute bottleneck
            bottleneck = PathFinder.compute_bottleneck(path, residual)
            
            # Record path found
            self.steps.append({
                'type': 'path_found',
                'iteration': iteration,
                'flow': copy.deepcopy(self.flow),
                'residual': copy.deepcopy(residual),
                'path': path,
                'bottleneck': bottleneck,
                'max_flow': max_flow,
                'explanation': (
                    f"**Iteration {iteration}: Augmenting Path Found**\n\n"
                    f"Path: {' → '.join(path)}\n"
                    f"Bottleneck Δ = {bottleneck}"
                )
            })
            
            # Increase flow along path
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                self.flow[u][v] += bottleneck
            
            max_flow += bottleneck
            
            # Record flow update
            residual = ResidualGraph.compute(self.original_graph, self.flow)
            self.steps.append({
                'type': 'flow_updated',
                'iteration': iteration,
                'flow': copy.deepcopy(self.flow),
                'residual': copy.deepcopy(residual),
                'path': path,
                'bottleneck': bottleneck,
                'max_flow': max_flow,
                'explanation': (
                    f"**Flow Updated**\n\n"
                    f"Added {bottleneck} units along path\n"
                    f"Current total flow: {max_flow}\n"
                    f"Residual capacities updated"
                )
            })
        
        return max_flow
    
    def get_steps(self):
        """Return algorithm execution steps"""
        return self.steps
    
    def get_final_flow(self):
        """Return final flow"""
        return self.flow