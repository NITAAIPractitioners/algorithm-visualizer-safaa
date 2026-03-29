"""
Bin Packing Algorithms Core Logic
Implements First Fit and Best Fit algorithms with step-by-step recording.
"""
import copy

class BinPackingAlgorithm:
    """Base class for Bin Packing algorithms to share step recording logic."""
    def __init__(self, items, capacity=1.0):
        # Items is a list of floats, e.g., [0.2, 0.5, 0.8]
        self.items = items
        self.capacity = capacity
        # Bins is a list of lists, where each inner list contains the items in that bin
        self.bins = []
        # History of steps for visualization
        self.steps = []
    
    def _record_step(self, step_type, current_item_idx, current_item_size, active_bin_idx=None, explanation=""):
        """
        Record a snapshot of the algorithm's state.
        Types of steps:
        - 'evaluate_item': Started looking at a new item
        - 'check_bin': Looking at a specific bin to see if the item fits
        - 'place_item': Placed the item into a bin
        - 'new_bin': Created a new bin for the item
        - 'complete': Algorithm finished
        """
        # Calculate current levels of all bins for easy rendering
        bin_levels = [round(sum(b), 4) for b in self.bins]
        
        self.steps.append({
            'type': step_type,
            'current_item_idx': current_item_idx,
            'current_item_size': current_item_size,
            'active_bin_idx': active_bin_idx,
            'bins_state': copy.deepcopy(self.bins),
            'bin_levels': bin_levels,
            'explanation': explanation
        })

    def get_steps(self):
        """Return the recorded steps history."""
        return self.steps


class FirstFitAlgorithm(BinPackingAlgorithm):
    """
    First Fit Algorithm:
    Places an item into the first bin that has enough remaining capacity.
    If no such bin exists, a new bin is created.
    """
    def run(self):
        self.steps = []
        self.bins = []
        
        if not self.items:
            self._record_step('complete', None, None, None, "No items to pack.")
            return []
            
        for i, item in enumerate(self.items):
            self._record_step(
                'evaluate_item', i, item, None,
                f"Evaluating Item {i+1} (Size: {item})\n\n"
                f"- Looking for the FIRST bin that can fit size {item}."
            )
            
            placed = False
            for j, current_bin in enumerate(self.bins):
                current_level = round(sum(current_bin), 4)
                remaining = round(self.capacity - current_level, 4)
                
                self._record_step(
                    'check_bin', i, item, j,
                    f"Checking Bin {j+1}\n\n"
                    f"- Current Level: {current_level} / {self.capacity}\n"
                    f"- Remaining Capacity: {remaining}\n"
                    f"- Item Size: {item}\n\n"
                    f"{'Can fit!' if item <= remaining else 'Cannot fit.'}"
                )
                
                if item <= remaining:
                    self.bins[j].append(item)
                    placed = True
                    self._record_step(
                        'place_item', i, item, j,
                        f"Placed Item {i+1} into Bin {j+1}\n\n"
                        f"- Bin {j+1} level updated to {round(sum(self.bins[j]), 4)}."
                    )
                    break
            
            if not placed:
                self.bins.append([item])
                new_idx = len(self.bins) - 1
                self._record_step(
                    'new_bin', i, item, new_idx,
                    f"No existing bin could fit Item {i+1}.\n\n"
                    f"- Created new Bin {new_idx+1}.\n"
                    f"- Placed Item {i+1} into Bin {new_idx+1}."
                )
                
        self._record_step(
            'complete', None, None, None,
            f"Algorithm Complete\n\n"
            f"- Total Items Packed: {len(self.items)}\n"
            f"- Total Bins Used: {len(self.bins)}"
        )
        
        return self.bins


class BestFitAlgorithm(BinPackingAlgorithm):
    """
    Best Fit Algorithm:
    Places an item into the bin where it fits perfectly or leaves the least remaining space.
    If no such bin exists, a new bin is created.
    """
    def run(self):
        self.steps = []
        self.bins = []
        
        if not self.items:
            self._record_step('complete', None, None, None, "No items to pack.")
            return []
            
        for i, item in enumerate(self.items):
            self._record_step(
                'evaluate_item', i, item, None,
                f"Evaluating Item {i+1} (Size: {item})\n\n"
                f"- Scanning ALL bins to find the perfectly tightest fit."
            )
            
            best_bin_idx = -1
            min_space_left = float('inf')
            
            for j, current_bin in enumerate(self.bins):
                current_level = round(sum(current_bin), 4)
                remaining = round(self.capacity - current_level, 4)
                
                # Check if it fits
                if item <= remaining:
                    space_left_after = round(remaining - item, 4)
                    
                    is_best_so_far = space_left_after < min_space_left
                    
                    self._record_step(
                        'check_bin', i, item, j,
                        f"Checking Bin {j+1}\n\n"
                        f"- Current Level: {current_level} / {self.capacity}\n"
                        f"- Remaining Capacity: {remaining}\n"
                        f"- Will leave {space_left_after} free space if placed here.\n\n"
                        f"{'New Best Fit!' if is_best_so_far else 'Fits, but not tighter than previous best.'}"
                    )
                    
                    if is_best_so_far:
                        best_bin_idx = j
                        min_space_left = space_left_after
                else:
                    self._record_step(
                        'check_bin', i, item, j,
                        f"Checking Bin {j+1}\n\n"
                        f"- Current Level: {current_level} / {self.capacity}\n"
                        f"- Remaining Capacity: {remaining}\n"
                        f"- Item Size: {item}\n\n"
                        f"Cannot fit."
                    )
            
            if best_bin_idx != -1:
                self.bins[best_bin_idx].append(item)
                self._record_step(
                    'place_item', i, item, best_bin_idx,
                    f"Placed Item {i+1} into Bin {best_bin_idx+1}\n\n"
                    f"- This was the tightest fit.\n"
                    f"- Bin {best_bin_idx+1} level updated to {round(sum(self.bins[best_bin_idx]), 4)}."
                )
            else:
                self.bins.append([item])
                new_idx = len(self.bins) - 1
                self._record_step(
                    'new_bin', i, item, new_idx,
                    f"No existing bin could fit Item {i+1}.\n\n"
                    f"- Created new Bin {new_idx+1}.\n"
                    f"- Placed Item {i+1} into Bin {new_idx+1}."
                )
                
        self._record_step(
            'complete', None, None, None,
            f"Algorithm Complete\n\n"
            f"- Total Items Packed: {len(self.items)}\n"
            f"- Total Bins Used: {len(self.bins)}"
        )
        
        return self.bins
