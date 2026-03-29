"""
Bin Packing Visualization Layer
Graph rendering and layout logic (no Streamlit UI)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

class BinRenderer:
    """Renders Bin Packing visualizations"""
    
    @staticmethod
    def render_step(step_data):
        """
        Render a single algorithm step
        
        Args:
            step_data: Step information dict from bp_core
        
        Returns:
            Matplotlib figure
        """
        bins_state = step_data.get('bins_state', [])
        active_bin_idx = step_data.get('active_bin_idx')
        current_item_size = step_data.get('current_item_size')
        step_type = step_data.get('type')
        
        # Calculate how many bins to show (at least 3 for spacing, or len(bins)+1)
        num_bins = max(3, len(bins_state) + (1 if current_item_size and step_type == 'evaluate_item' else 0))
        
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Set light gray background
        fig.patch.set_facecolor('#F5F5F5')
        ax.set_facecolor('#FAFAFA')
        
        bin_width = 0.6
        bin_spacing = 1.0
        max_height = 1.0
        
        # Draw bins
        for i in range(num_bins):
            x_center = i * bin_spacing
            x_left = x_center - bin_width / 2
            
            # Draw standard bin outline
            is_active = (i == active_bin_idx)
            
            # Determine line color
            if is_active and step_type == 'place_item':
                line_color = '#4CAF50'  # Green success
                line_width = 3
            elif is_active and step_type == 'check_bin':
                line_color = '#2196F3'  # Blue checking
                line_width = 3
            else:
                line_color = '#9E9E9E'  # Gray default
                line_width = 2
                
            # Draw the U-shaped bin (left, bottom, right lines)
            ax.plot([x_left, x_left], [0, max_height], color=line_color, lw=line_width)
            ax.plot([x_left + bin_width, x_left + bin_width], [0, max_height], color=line_color, lw=line_width)
            ax.plot([x_left, x_left + bin_width], [0, 0], color=line_color, lw=line_width)
            
            # Bin Label
            bin_label = f"Bin {i+1}"
            ax.text(x_center, -0.05, bin_label, ha='center', va='top', fontweight='bold')
            
            # Draw items in the bin (if it exists)
            if i < len(bins_state):
                current_y = 0.0
                for item_val in bins_state[i]:
                    rect = patches.Rectangle((x_left + 0.05, current_y), 
                                             bin_width - 0.1, 
                                             item_val, 
                                             linewidth=1, edgecolor='black', facecolor='#E3F2FD')
                    ax.add_patch(rect)
                    
                    # Add item label
                    yloc = current_y + item_val / 2
                    ax.text(x_center, yloc, f"{item_val}", ha='center', va='center', fontsize=9, color='black')
                    
                    current_y += item_val
                
                # Show capacity remaining at top if bin is active
                if is_active:
                    remaining = round(max_height - current_y, 4)
                    ax.text(x_center, max_height + 0.05, f"Free: {remaining}", 
                            ha='center', va='bottom', fontsize=10, color=line_color, fontweight='bold')
        
        # Draw incoming item if applicable
        if current_item_size is not None and step_type != 'place_item' and step_type != 'new_bin' and step_type != 'complete':
            # Draw an "incoming" block
            incoming_x = num_bins * bin_spacing
            rect = patches.Rectangle((incoming_x - bin_width/2 + 0.05, 0.5), 
                                     bin_width - 0.1, 
                                     current_item_size, 
                                     linewidth=2, edgecolor='#FF9800', facecolor='#FFE0B2', linestyle='--')
            ax.add_patch(rect)
            
            yloc = 0.5 + current_item_size / 2
            ax.text(incoming_x, yloc, f"{current_item_size}", ha='center', va='center', fontsize=10, fontweight='bold', color='black')
            ax.text(incoming_x, 0.5 - 0.05, "Incoming\nItem", ha='center', va='top', fontsize=9, fontweight='bold', color='#FF9800')
        
        # Graph bounds
        total_width = (num_bins + 1) * bin_spacing
        ax.set_xlim(-bin_width, total_width)
        ax.set_ylim(-0.2, max_height + 0.2)
        
        ax.axis('off')
        plt.tight_layout()
        
        return fig
