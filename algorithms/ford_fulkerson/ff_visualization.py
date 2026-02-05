"""
Ford-Fulkerson Visualization Layer
Graph rendering and layout logic (no Streamlit UI)
"""

import networkx as nx
import matplotlib.pyplot as plt
from collections import deque


# ============================================================================
# GRAPH LAYOUT
# ============================================================================

class GraphLayout:
    """Computes graph layout for visualization"""
    
    @staticmethod
    def hierarchical(graph, source, sink):
        """
        Create HORIZONTAL hierarchical layout (LEFT to RIGHT)
        Max 3 nodes per column, arranged vertically
        
        Args:
            graph: Graph structure
            source: Source node
            sink: Sink node
        
        Returns:
            Dictionary of positions {node: (x, y)}
        """
        # Build full node set
        all_nodes = set()
        for u in graph:
            all_nodes.add(u)
            for v in graph[u]:
                all_nodes.add(v)
        
        # BFS to assign columns (levels)
        columns_dict = {}
        visited = {source}
        queue = deque([(source, 0)])
        columns_dict[source] = 0
        
        while queue:
            node, col = queue.popleft()
            
            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        columns_dict[neighbor] = col + 1
                        queue.append((neighbor, col + 1))
        
        # Ensure sink is at the last column
        max_col = max(columns_dict.values())
        if columns_dict.get(sink, 0) < max_col:
            columns_dict[sink] = max_col
        
        # Add any unvisited nodes to middle columns
        for node in all_nodes:
            if node not in columns_dict:
                columns_dict[node] = max_col // 2
        
        # Group nodes by column
        columns = {}
        for node, col in columns_dict.items():
            if col not in columns:
                columns[col] = []
            columns[col].append(node)
        
        # Redistribute to ensure max 3 nodes per column
        final_columns = []
        for col_idx in sorted(columns.keys()):
            nodes_in_col = sorted(columns[col_idx])
            
            # Split into chunks of max 3 nodes
            for i in range(0, len(nodes_in_col), 3):
                chunk = nodes_in_col[i:i+3]
                final_columns.append(chunk)
        
        # Create positions (HORIZONTAL: x increases left to right)
        pos = {}
        x_spacing = 2.5  # HORIZONTAL distance between columns
        y_spacing = 1.8  # VERTICAL distance between nodes in same column
        
        for col_idx, nodes_in_col in enumerate(final_columns):
            x = col_idx * x_spacing
            
            # Center nodes vertically
            num_nodes = len(nodes_in_col)
            
            for node_idx, node in enumerate(nodes_in_col):
                # Calculate y position to center the nodes vertically
                if num_nodes == 1:
                    y = 0
                elif num_nodes == 2:
                    y = (node_idx - 0.5) * y_spacing
                else:  # 3 nodes
                    y = (node_idx - 1) * y_spacing
                
                pos[node] = (x, y)
        
        return pos


# ============================================================================
# GRAPH RENDERER
# ============================================================================

class GraphRenderer:
    """Renders graph visualizations"""
    
    @staticmethod
    def create_networkx_graph(graph):
        """Create NetworkX graph from adjacency dict"""
        G = nx.DiGraph()
        
        all_nodes = set()
        for u in graph:
            all_nodes.add(u)
            for v in graph[u]:
                all_nodes.add(v)
        
        G.add_nodes_from(all_nodes)
        
        for u in graph:
            for v in graph[u]:
                G.add_edge(u, v)
        
        return G
    
    @staticmethod
    def get_node_colors(nodes, source, sink, source_partition=None, sink_partition=None):
        """
        Get node colors - light blue and light coral scheme
        
        Args:
            nodes: List of nodes
            source: Source node
            sink: Sink node
            source_partition: Optional source partition for min-cut viz
            sink_partition: Optional sink partition for min-cut viz
        
        Returns:
            List of colors
        """
        colors = []
        
        for node in nodes:
            if source_partition is not None and sink_partition is not None:
                # Min-cut visualization - light blue and light coral
                if node in source_partition:
                    colors.append('#E3F2FD')  # Light blue
                else:
                    colors.append('#FFEBEE')  # Light coral/pink
            else:
                # Normal visualization
                if node == source:
                    colors.append('#E3F2FD')  # Light blue for source
                elif node == sink:
                    colors.append('#FFEBEE')  # Light coral for sink
                else:
                    colors.append('#F5F5F5')  # Light gray for other nodes
        
        return colors
    
    @staticmethod
    def draw_edges(ax, graph, pos, highlighted_edges=None):
        """
        Draw graph edges with standard colors
        
        Args:
            ax: Matplotlib axis
            graph: Graph structure
            pos: Node positions
            highlighted_edges: Set of edges to highlight
        """
        if highlighted_edges is None:
            highlighted_edges = set()
        
        for u in graph:
            for v in graph[u]:
                is_highlighted = (u, v) in highlighted_edges
                
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                
                if is_highlighted:
                    edge_color = '#1976D2'  # Standard blue
                    edge_width = 3.0
                else:
                    edge_color = '#666666'  # Dark gray
                    edge_width = 1.5
                
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', color=edge_color,
                                         lw=edge_width,
                                         shrinkA=22, shrinkB=22))
    
    @staticmethod
    def draw_edge_labels(ax, graph, pos, flow=None, residual=None, 
                        highlighted_edges=None, cut_edges=None):
        """
        Draw edge labels
        
        Args:
            ax: Matplotlib axis
            graph: Graph structure
            pos: Node positions
            flow: Flow dict (for flow/capacity labels)
            residual: Residual dict (for residual capacity labels)
            highlighted_edges: Set of edges to highlight
            cut_edges: Set of cut edges
        """
        if highlighted_edges is None:
            highlighted_edges = set()
        if cut_edges is None:
            cut_edges = set()
        
        # Determine which edges to label
        if flow is not None:
            edges_to_label = graph
        elif residual is not None:
            edges_to_label = residual
        else:
            return  # Nothing to label
        
        for u in edges_to_label:
            for v in edges_to_label[u]:
                if residual is not None and edges_to_label[u][v] <= 0:
                    continue
                
                is_highlighted = (u, v) in highlighted_edges
                is_cut = (u, v) in cut_edges
                
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                
                # Determine label and style
                if is_cut:
                    capacity = graph[u][v]
                    label = f"{capacity}"  # Just show capacity
                    label_bg = '#EF5350'  # Red
                    edge_color = '#D32F2F'  # Dark red
                    text_color = 'white'
                elif flow is not None:
                    capacity = graph[u][v]
                    current_flow = flow[u][v] if u in flow and v in flow[u] else 0
                    label = f"{current_flow}/{capacity}"
                    label_bg = '#E3F2FD' if is_highlighted else '#FFFFFF'  # Light blue or white
                    edge_color = '#1976D2' if is_highlighted else '#666666'  # Blue or gray
                    text_color = '#000000'  # Black text
                else:  # residual
                    label = f"{residual[u][v]}"
                    label_bg = '#E3F2FD' if is_highlighted else '#F5F5F5'  # Light blue or gray
                    edge_color = '#1976D2' if is_highlighted else '#666666'
                    text_color = '#000000'  # Black text
                
                # Position at START of arrow (25% from source)
                label_x = x1 + 0.25 * (x2 - x1)
                label_y = y1 + 0.25 * (y2 - y1)
                
                # Small offset perpendicular to edge
                dx = x2 - x1
                dy = y2 - y1
                length = (dx**2 + dy**2)**0.5
                if length > 0:
                    offset_x = -dy / length * 0.12
                    offset_y = dx / length * 0.12
                else:
                    offset_x, offset_y = 0.08, 0.08
                
                label_x += offset_x
                label_y += offset_y
                
                bbox_props = dict(
                    boxstyle="round,pad=0.35" if not is_cut else "round,pad=0.4",
                    facecolor=label_bg,
                    edgecolor=edge_color,
                    linewidth=2.5 if is_cut else (2 if is_highlighted else 1)
                )
                
                ax.text(label_x, label_y, label, 
                       fontsize=10 if is_cut else 9,
                       ha='center', va='center',
                       bbox=bbox_props,
                       fontweight='bold' if (is_highlighted or is_cut) else 'normal',
                       color=text_color,
                       zorder=1000)
    
    @staticmethod
    def render_step(step_data, graph, source, sink):
        """
        Render a single algorithm step
        
        Args:
            step_data: Step information dict
            graph: Original graph
            source: Source node
            sink: Sink node
        
        Returns:
            Matplotlib figure
        """
        flow = step_data['flow']
        residual = step_data['residual']
        path = step_data.get('path', None)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
        
        # Set light gray background
        fig.patch.set_facecolor('#F5F5F5')
        ax1.set_facecolor('#FFFFFF')
        ax2.set_facecolor('#FFFFFF')
        
        # Set gray background
        fig.patch.set_facecolor('#F5F5F5')
        ax1.set_facecolor('#FAFAFA')
        ax2.set_facecolor('#FAFAFA')
        
        # Create NetworkX graph
        G = GraphRenderer.create_networkx_graph(graph)
        
        # Get layout
        pos = GraphLayout.hierarchical(graph, source, sink)
        
        # Get node colors
        node_colors = GraphRenderer.get_node_colors(G.nodes(), source, sink)
        
        # Highlighted edges from path
        highlighted_edges = set()
        if path:
            for i in range(len(path) - 1):
                highlighted_edges.add((path[i], path[i + 1]))
        
        # === LEFT SUBPLOT: FLOW NETWORK ===
        ax1.set_title("Flow Network (flow/capacity)",
                     fontsize=14, fontweight='bold', pad=5)
        
        # Draw edges
        GraphRenderer.draw_edges(ax1, graph, pos, highlighted_edges)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=1600, ax=ax1,
                              edgecolors='black', linewidths=3)
        
        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=13,
                               font_weight='bold', ax=ax1)
        
        # Draw edge labels
        GraphRenderer.draw_edge_labels(ax1, graph, pos, flow=flow,
                                      highlighted_edges=highlighted_edges)
        
        ax1.axis('off')
        ax1.margins(0.1)
        
        # === RIGHT SUBPLOT: RESIDUAL GRAPH ===
        ax2.set_title("Residual Graph (remaining capacity)",
                     fontsize=14, fontweight='bold', pad=5)
        
        # Draw residual edges
        GraphRenderer.draw_edges(ax2, residual, pos, highlighted_edges)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=1600, ax=ax2,
                              edgecolors='black', linewidths=3)
        
        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=13,
                               font_weight='bold', ax=ax2)
        
        # Draw residual edge labels
        GraphRenderer.draw_edge_labels(ax2, residual, pos, residual=residual,
                                      highlighted_edges=highlighted_edges)
        
        ax2.axis('off')
        ax2.margins(0.1)
        
        plt.tight_layout(pad=0.5)
        
        return fig
    
    @staticmethod
    def render_minimum_cut(step_data, graph, source, sink):
        """
        Render minimum cut visualization
        
        Args:
            step_data: Step information dict with cut data
            graph: Original graph
            source: Source node
            sink: Sink node
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        
        # Set light gray background
        fig.patch.set_facecolor('#F5F5F5')
        ax.set_facecolor('#FFFFFF')
        
        # Set gray background
        fig.patch.set_facecolor('#F5F5F5')
        ax.set_facecolor('#FAFAFA')
        
        cut_edges = step_data.get('min_cut_edges', [])
        source_partition = step_data.get('source_partition', set())
        sink_partition = step_data.get('sink_partition', set())
        
        # Create NetworkX graph
        G = GraphRenderer.create_networkx_graph(graph)
        
        # Get layout
        pos = GraphLayout.hierarchical(graph, source, sink)
        
        # Get node colors for partitions
        node_colors = GraphRenderer.get_node_colors(
            G.nodes(), source, sink,
            source_partition, sink_partition
        )
        
        # Draw edges with labels
        for u in graph:
            for v in graph[u]:
                is_cut_edge = (u, v) in cut_edges
                
                x1, y1 = pos[u]
                x2, y2 = pos[v]
                
                if is_cut_edge:
                    edge_color = '#F44336'  # Material red
                    edge_width = 5
                else:
                    edge_color = '#CCCCCC'
                    edge_width = 1.8
                
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', color=edge_color,
                                         lw=edge_width,
                                         shrinkA=22, shrinkB=22))
                
                # Draw label if it's a cut edge
                if is_cut_edge:
                    capacity = graph[u][v]
                    
                    # Position at START of arrow (25% from source) - like working code
                    label_x = x1 + 0.25 * (x2 - x1)
                    label_y = y1 + 0.25 * (y2 - y1)
                    
                    # Offset perpendicular to edge
                    dx = x2 - x1
                    dy = y2 - y1
                    length = (dx**2 + dy**2)**0.5
                    if length > 0:
                        offset_x = -dy / length * 0.12
                        offset_y = dx / length * 0.12
                    else:
                        offset_x, offset_y = 0.08, 0.08
                    
                    label_x += offset_x
                    label_y += offset_y
                    
                    bbox_props = dict(boxstyle="round,pad=0.4",
                                    facecolor='#FF6666',
                                    edgecolor='#FF0000',
                                    linewidth=2.5)
                    ax.text(label_x, label_y, f"{capacity}",
                           fontsize=10, ha='center', va='center',
                           bbox=bbox_props, fontweight='bold',
                           color='white', zorder=1000)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                              node_size=1600, ax=ax,
                              edgecolors='black', linewidths=3)
        
        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=13,
                               font_weight='bold', ax=ax)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#90EE90', edgecolor='black',
                  label=f'S = {{{", ".join(sorted(source_partition))}}}'),
            Patch(facecolor='#FFB6C1', edgecolor='black',
                  label=f'T = {{{", ".join(sorted(sink_partition))}}}')
        ]
        ax.legend(handles=legend_elements, loc='upper left',
                 fontsize=10, framealpha=0.9)
        
        ax.set_title("Minimum Cut",
                    fontsize=14, fontweight='bold', pad=5)
        
        ax.axis('off')
        ax.margins(0.1)
        
        plt.tight_layout(pad=0.5)
        
        return fig