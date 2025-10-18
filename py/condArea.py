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
        self.stored_values = None  # Will be set by ComfyUI from node properties
        self.properties = None     # ComfyUI properties
    
    def set_properties(self, properties):
        """Called by ComfyUI to set node properties"""
        self.properties = properties
        if properties and 'values' in properties:
            self.stored_values = properties['values']
    
    def set_stored_values(self, values):
        """Called by ComfyUI to set the stored values from node properties"""
        if values and isinstance(values, list):
            self.stored_values = values
    
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
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",  # ComfyUI passes node ID
                "extra_pnginfo": "EXTRA_PNGINFO",  # ComfyUI passes workflow info
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    RETURN_NAMES = ("conditioning",)
    OUTPUT_TOOLTIPS = ("Combined conditioning with area settings applied to selected index",)
    
    FUNCTION = "apply_conditioning_area"
    CATEGORY = "💀Prepack"
    DESCRIPTION = "Set area for multiple conditioning inputs using index-based selection. Connect up to 5 conditioning inputs and use the index parameter to select which one to modify. Remaining conditioning inputs are passed through and combined."
    
    def apply_conditioning_area(self, conditioning_1, index, width, height, x, y, strength,
                               conditioning_2=None, conditioning_3=None, conditioning_4=None, conditioning_5=None,
                               unique_id=None, extra_pnginfo=None, **kwargs):
        """
        Apply conditioning area settings to all connected conditioning inputs.
        This behaves exactly like multiple ConditioningSetAreaPercentage nodes combined with ConditioningCombine.
        
        Args:
            conditioning_1: First (required) conditioning
            index: Currently selected index for UI display (1-5) 
            width, height, x, y, strength: Current UI values for selected index
            conditioning_2-5: Optional additional conditioning inputs
        
        Returns:
            Combined conditioning with area settings applied to all connected inputs
        """
        
        print(f"PrepackCondArea - Called with index={index}, x={x}, y={y}, w={width}, h={height}, s={strength}")
        print(f"PrepackCondArea - unique_id: {unique_id}")
        print(f"PrepackCondArea - kwargs keys: {list(kwargs.keys())}")
        
        # CRITICAL: Get stored values - try multiple methods in order of reliability
        area_params = None
        
        # Method 1: Extract from workflow info using unique_id
        if unique_id and extra_pnginfo and 'workflow' in extra_pnginfo:
            try:
                workflow = extra_pnginfo['workflow']
                if 'nodes' in workflow:
                    for node in workflow['nodes']:
                        if str(node.get('id')) == str(unique_id):
                            node_properties = node.get('properties', {})
                            if 'values' in node_properties:
                                area_params = node_properties['values']
                                print(f"PrepackCondArea - Got values from workflow: {area_params}")
                                break
            except Exception as e:
                print(f"PrepackCondArea - Error extracting from workflow: {e}")
        
        # Method 2: From node properties
        if not area_params and hasattr(self, 'properties') and self.properties and 'values' in self.properties:
            area_params = self.properties['values']
            print(f"PrepackCondArea - Got values from self.properties: {area_params}")
        
        # Method 3: From kwargs (backup)
        elif not area_params and 'values' in kwargs:
            area_params = kwargs['values']
            print(f"PrepackCondArea - Got values from kwargs: {area_params}")
        
        # Method 4: From stored values on instance
        elif not area_params and hasattr(self, 'stored_values') and self.stored_values:
            area_params = self.stored_values
            print(f"PrepackCondArea - Got values from stored_values: {area_params}")
        
        # Method 5: Use current JSON values as template (for testing)
        if not area_params:
            area_params = [
                [0.05, 0.35, 0.55, 0.6, 1.3],   # conditioning_1: From current JSON
                [0.69, 0.06, 0.25, 0.25, 0.4],  # conditioning_2: From current JSON
                [0, 0, 1, 1, 0.5],               # conditioning_3: From current JSON
                [0, 0, 1, 1, 1.0],               # conditioning_4: Default
                [0, 0, 1, 1, 1.0],               # conditioning_5: Default
            ]
            print(f"PrepackCondArea - Using JSON template values for testing")
        
        # Ensure we have a valid array
        if not area_params or not isinstance(area_params, list):
            print(f"PrepackCondArea - ERROR: Invalid area_params: {area_params}")
            return (conditioning_1,)
        
        # Make a copy to avoid modifying the original
        area_params = [list(row) for row in area_params]
        
        # Update the selected index with current UI values (CRITICAL for real-time editing)
        if 1 <= index <= 5 and len(area_params) >= index:
            area_params[index-1] = [x, y, width, height, strength]
            print(f"PrepackCondArea - Updated index {index} with UI values: x={x}, y={y}, w={width}, h={height}, s={strength}")
        
        print(f"PrepackCondArea - Final area_params: {area_params}")
        
        # Collect all conditioning inputs
        cond_list = [conditioning_1, conditioning_2, conditioning_3, conditioning_4, conditioning_5]
        
        # Process each conditioning individually (exactly like ConditioningSetAreaPercentage)
        processed_conditionings = []
        
        for i, cond in enumerate(cond_list):
            if cond is not None:
                # Get parameters for this conditioning slot
                if i < len(area_params):
                    params = area_params[i]
                    cond_x = float(params[0])
                    cond_y = float(params[1]) 
                    cond_width = float(params[2])
                    cond_height = float(params[3])
                    cond_strength = float(params[4])
                    
                    # Debug: Print parameters for verification
                    print(f"PrepackCondArea - Conditioning {i+1}: x={cond_x}, y={cond_y}, w={cond_width}, h={cond_height}, s={cond_strength}")
                    
                    # Skip conditioning if strength is 0 or very close to 0 (like official behavior)
                    if abs(cond_strength) < 1e-6:
                        print(f"PrepackCondArea - Conditioning {i+1}: skipped (strength={cond_strength})")
                        continue
                        
                else:
                    # Fallback to full area with strength 1.0
                    cond_x, cond_y, cond_width, cond_height, cond_strength = 0.0, 0.0, 1.0, 1.0, 1.0
                    print(f"PrepackCondArea - Conditioning {i+1}: using fallback parameters")
                
                # Apply area settings exactly like official ConditioningSetAreaPercentage
                cond_processed = node_helpers.conditioning_set_values(cond, {
                    "area": ("percentage", cond_height, cond_width, cond_y, cond_x),
                    "strength": cond_strength,
                    "set_area_to_bounds": False
                })
                
                processed_conditionings.append(cond_processed)
        
        # Combine all processed conditionings exactly like official ConditioningCombine
        if not processed_conditionings:
            print(f"PrepackCondArea - No conditionings to process, returning original")
            return (conditioning_1,)  # Return original if nothing to process
            
        print(f"PrepackCondArea - Combining {len(processed_conditionings)} processed conditionings")
        
        # Start with first conditioning and combine with others
        result = processed_conditionings[0]
        for i, cond in enumerate(processed_conditionings[1:], 1):
            result = result + cond  # This is exactly how official ConditioningCombine works
            print(f"PrepackCondArea - Combined conditioning {i+1}")
        
        print(f"PrepackCondArea - Final result ready")
        return (result,)


NODE_CLASS_MAPPINGS = {
    "PrepackCondArea": PrepackCondArea
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PrepackCondArea": "💀Prepack Cond Area"
}