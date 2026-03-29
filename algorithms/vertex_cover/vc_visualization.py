"""
Vertex Cover Visualization Layer
Graph rendering and layout logic
"""

import matplotlib.pyplot as plt
import networkx as nx

class VCRenderer:
    """Renders Vertex Cover visualizations"""
    
    @staticmethod
    def render_step(step_data):
        """
        Render a single algorithm step
        """
        pos = step_data.get('pos', {})
        original_edges = step_data.get('original_edges', [])
        e_prime = step_data.get('e_prime', [])
        vc = step_data.get('vc', [])
        active_edge = step_data.get('active_edge')
        pruned_edges = step_data.get('pruned_edges', [])
        step_type = step_data.get('type')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Background
        fig.patch.set_facecolor('#F8F9FA')
        ax.set_facecolor('#FFFFFF')
        
        if not pos:
            ax.text(0.5, 0.5, "Empty Graph", ha='center', va='center', fontsize=20, color='#BDBDBD')
            ax.axis('off')
            return fig
            
        # Draw background faint shadow of the entire original graph
        # so the user never loses track of the overall structure when edges get pruned
        for u, v in original_edges:
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            ax.plot([x1, x2], [y1, y2], color='#EEEEEE', linewidth=1, zorder=0)

        # Draw active E' edges
        for u, v in e_prime:
            if (u, v) == active_edge or (v, u) == active_edge:
                # The active picked edge
                color = '#2196F3' # Blue
                lw = 4
                style = '-'
                z = 2
            elif (u, v) in pruned_edges or (v, u) in pruned_edges:
                # Edges actively being pruned right now
                color = '#F44336' # Red
                lw = 2
                style = '--'
                z = 1
            else:
                # Standard active E' edge
                color = '#757575' # Dark Gray
                lw = 1.5
                style = '-'
                z = 1
                
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, linestyle=style, zorder=z)

        # Draw Nodes
        for node in pos:
            x, y = pos[node]
            
            in_vc = node in vc
            
            if in_vc:
                node_color = '#E8F5E9'
                edge_color = '#4CAF50' # Green cover
                lw = 3
            else:
                node_color = '#FFFFFF'
                edge_color = '#9E9E9E'
                lw = 2
                
            ax.scatter(x, y, s=500, c=node_color, edgecolors=edge_color, linewidths=lw, zorder=3)
            # Make text green if in VC for extra contrast, else black
            text_color = '#2E7D32' if in_vc else '#212121'
            ax.text(x, y, str(node), ha='center', va='center', fontweight='bold', color=text_color, zorder=4)
            
        ax.axis('off')
        
        # Add a minimal legend purely via text
        legend_text = f"|VC| Size: {len(vc)}    Edges Remaining in E': {len(e_prime)}"
        ax.set_title(legend_text, loc='left', fontsize=10, color='#616161', pad=10)
        
        plt.tight_layout()
        
        return fig
