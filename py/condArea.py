import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

import node_helpers

"""💀Prepack Cond Area: Multi-conditioning area setter with index-based control"""

class PrepackCondArea:
    """
    Set area for multiple conditioning inputs using index-based selection.
    Similar to MultiAreaConditioning, uses an index parameter to select which conditioning to modify.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_1": ("CONDITIONING", {
                    "tooltip": "Primary conditioning input"
                }),
                "index": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 5,
                    "step": 1,
                    "tooltip": "Select which conditioning to modify (1-5)"
                }),
                "width": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Width of the conditioning area (0.0 to 1.0)"
                }),
                "height": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Height of the conditioning area (0.0 to 1.0)"
                }),
                "x": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "X position of the conditioning area (0.0 to 1.0)"
                }),
                "y": ("FLOAT", {
                    "default": 0.0, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Y position of the conditioning area (0.0 to 1.0)"
                }),
                "strength": ("FLOAT", {
                    "default": 1.0, 
                    "min": 0.0, 
                    "max": 10.0, 
                    "step": 0.01,
                    "tooltip": "Strength of the conditioning effect"
                }),
            },
            "optional": {
                "conditioning_2": ("CONDITIONING", {
                    "default": None,
                    "tooltip": "Optional second conditioning"
                }),
                "conditioning_3": ("CONDITIONING", {
                    "default": None,
                    "tooltip": "Optional third conditioning"
                }),
                "conditioning_4": ("CONDITIONING", {
                    "default": None,
                    "tooltip": "Optional fourth conditioning"
                }),
                "conditioning_5": ("CONDITIONING", {
                    "default": None,
                    "tooltip": "Optional fifth conditioning"
                }),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    OUTPUT_TOOLTIPS = ("Combined conditioning with area settings applied to selected index",)
    
    FUNCTION = "apply_conditioning_area"
    CATEGORY = "💀Prepack"
    DESCRIPTION = "Set area for multiple conditioning inputs using index-based selection. Connect up to 5 conditioning inputs and use the index parameter to select which one to modify. Remaining conditioning inputs are passed through and combined."
    
    def apply_conditioning_area(self, conditioning_1, index, width, height, x, y, strength,
                               conditioning_2=None, conditioning_3=None, conditioning_4=None, conditioning_5=None):
        """
        Apply conditioning area settings to selected conditioning by index.
        Parameters are stored per-index via frontend.
        
        Args:
            conditioning_1: First (required) conditioning
            index: Which conditioning to modify (1-5)
            width, height, x, y: Area parameters (0.0-1.0) for selected index
            strength: Conditioning strength (0.0-10.0) for selected index
            conditioning_2-5: Optional additional conditioning inputs
        
        Returns:
            Combined conditioning with area settings applied to the selected index
        """
        
        # Clamp values to valid ranges
        index = max(1, min(5, int(index)))
        width = max(0.0, min(1.0, float(width)))
        height = max(0.0, min(1.0, float(height)))
        x = max(0.0, min(1.0, float(x)))
        y = max(0.0, min(1.0, float(y)))
        strength = max(0.0, float(strength))
        
        # Collect all conditioning inputs
        cond_list = [conditioning_1, conditioning_2, conditioning_3, conditioning_4, conditioning_5]
        
        # Apply area settings to the selected conditioning by index
        result = None
        for i, cond in enumerate(cond_list):
            if cond is not None:
                current_index = i + 1
                
                if current_index == index:
                    # Apply area settings to selected conditioning
                    modified_cond = node_helpers.conditioning_set_values(cond, {
                        "area": ("percentage", height, width, y, x),
                        "strength": strength,
                        "set_area_to_bounds": False
                    })
                else:
                    # Pass through other conditioning unchanged
                    modified_cond = cond
                
                # Combine with result
                if result is None:
                    result = modified_cond
                else:
                    result = result + modified_cond
        
        return (result,)


NODE_CLASS_MAPPINGS = {
    "PrepackCondArea": PrepackCondArea
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PrepackCondArea": "💀Prepack Cond Area"
}