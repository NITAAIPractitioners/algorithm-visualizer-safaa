"""
Euclidean TSP Visualization Layer
Creates Matplotlib figures for the TSP algorithms
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class TSPRenderer:
    """Renders Euclidean TSP geometries and paths."""
    
    @staticmethod
    def render_step(step_data):
        """
        Render a single algorithm step
        
        Args:
            step_data: Step information dict from tsp_core
        
        Returns:
            Matplotlib figure
        """
        nodes = step_data.get('nodes', {})
        edges = step_data.get('edges', {})
        highlighted_edges = step_data.get('highlighted_edges', [])
        highlighted_nodes = step_data.get('highlighted_nodes', [])
        step_type = step_data.get('type')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Set clean background
        fig.patch.set_facecolor('#F8F9FA')
        ax.set_facecolor('#FFFFFF')
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Draw all nodes first to get bounds
        x_vals = [pos[0] for pos in nodes.values()]
        y_vals = [pos[1] for pos in nodes.values()]
        
        if x_vals:
            padding = 10
            ax.set_xlim(min(x_vals) - padding, max(x_vals) + padding)
            ax.set_ylim(min(y_vals) - padding, max(y_vals) + padding)
        
        # Helper to draw a line with offset for multigraphs
        def draw_edge(u, v, count, is_highlighted, step_type):
            x1, y1 = nodes[u]
            x2, y2 = nodes[v]
            
            color = '#BDBDBD'  # Default gray
            lw = 1.5
            style = '-'
            alpha = 0.6
            
            if step_type == 'mst':
                color = '#2196F3' if is_highlighted else '#E0E0E0'
                lw = 2.5 if is_highlighted else 1.0
                alpha = 1.0 if is_highlighted else 0.4
            elif step_type == 'multigraph':
                color = '#9C27B0'
                lw = 2.0
                alpha = 0.8
            elif step_type == 'matching':
                if is_highlighted:
                    color = '#E91E63' # Pink matching
                    lw = 3.0
                    alpha = 1.0
                    style = '--'
                else:
                    color = '#2196F3' # MST original
                    lw = 1.5
                    alpha = 0.5
            elif step_type == 'odd_vertices':
                color = '#2196F3' # MST original
                lw = 1.5
                alpha = 0.5
            elif step_type == 'eulerian':
                color = '#FF9800'
                lw = 2.0
                alpha = 0.7
            elif step_type == 'hamiltonian':
                if is_highlighted:
                    color = '#4CAF50' # Green final tour
                    lw = 3.0
                    alpha = 1.0
            
            if count == 1 or step_type == 'hamiltonian':
                ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, linestyle=style, alpha=alpha, zorder=1)
                
                # Add distance label
                dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
                ax.text(mid_x, mid_y, f"{dist:.0f}", color=color, fontsize=9, fontweight='bold', ha='center', va='center',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0.2), zorder=3)
                
            elif count == 2:
                # Multigraph: draw two parallel lines slightly offset
                nx = -(y2 - y1)
                ny = (x2 - x1)
                length = np.sqrt(nx**2 + ny**2)
                if length == 0: return
                nx, ny = nx / length * 1.5, ny / length * 1.5 # offset magnitude
                
                ax.plot([x1 + nx, x2 + nx], [y1 + ny, y2 + ny], color=color, linewidth=lw, alpha=alpha, zorder=1)
                ax.plot([x1 - nx, x2 - nx], [y1 - ny, y2 - ny], color=color, linewidth=lw, alpha=alpha, zorder=1)
                
                # Add distance label once
                dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
                ax.text(mid_x, mid_y, f"{dist:.0f}", color=color, fontsize=9, fontweight='bold', ha='center', va='center',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.8, pad=0.2), zorder=3)
        
        # For initial layout, we can draw a faint complete graph
        if step_type == 'init':
            for u in nodes:
                for v in nodes:
                    if u < v:
                        x1, y1 = nodes[u]
                        x2, y2 = nodes[v]
                        ax.plot([x1, x2], [y1, y2], color='#E0E0E0', lw=0.5, alpha=0.3, zorder=0)
                        
                        dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                        mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
                        ax.text(mid_x, mid_y, f"{dist:.0f}", color='#9E9E9E', fontsize=7, ha='center', va='center', alpha=0.6, zorder=0)

        # Draw the edges
        for (u, v), count in edges.items():
            is_hl = (u, v) in highlighted_edges or (v, u) in highlighted_edges
            draw_edge(u, v, count, is_hl, step_type)
            
        # Draw Nodes
        for node_name, (x, y) in nodes.items():
            is_odd = node_name in highlighted_nodes
            
            node_color = '#FFFFFF'
            edge_color = '#424242'
            lw = 2
            size = 300
            
            if is_odd and step_type == 'odd_vertices':
                node_color = '#FCE4EC'
                edge_color = '#E91E63'
                lw = 3
                size = 500
            elif step_type == 'hamiltonian':
                edge_color = '#4CAF50'
                lw = 3
                
            ax.scatter(x, y, s=size, c=node_color, edgecolors=edge_color, linewidths=lw, zorder=2)
            ax.text(x, y, str(node_name), ha='center', va='center', fontweight='bold', color='#212121', zorder=3)
            
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_frame_on(True)
        for spine in ax.spines.values():
            spine.set_color('#E0E0E0')
            
        plt.tight_layout()
        
        return fig
