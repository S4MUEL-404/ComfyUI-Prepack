"""Prepack Number Type Converter: convert between string, int, and float types."""


class AlwaysEqualProxy(str):
    """Proxy class to accept any input type"""
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False


class PrepackNumberTypeConverter:
    """
    Number type converter node that accepts string, int, or float input
    and outputs all three types.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": (AlwaysEqualProxy("*"), {
                    "tooltip": "Input value (string, int, or float)"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "FLOAT")
    RETURN_NAMES = ("string", "int", "float")
    OUTPUT_TOOLTIPS = (
        "Value as string",
        "Value as integer (rounded if needed)",
        "Value as float"
    )
    FUNCTION = "convert"
    CATEGORY = "💀Prepack"
    DESCRIPTION = "Convert between string, int, and float types. Accepts any of these types and outputs all three."
    
    def convert(self, value):
        """
        Convert input value to string, int, and float.
        
        Args:
            value: Input value (string, int, or float)
            
        Returns:
            Tuple of (string, int, float)
        """
        try:
            # Convert to string
            str_value = str(value).strip()
            
            # Convert to float
            float_value = float(value)
            
            # Convert to int (rounded)
            int_value = int(round(float_value))
            
            print(f"[Prepack] 🔄 Number Type Converter: input={value} → string='{str_value}', int={int_value}, float={float_value}")
            
            return (str_value, int_value, float_value)
            
        except (ValueError, TypeError) as e:
            print(f"[Prepack] ❌ Number Type Converter: Error converting value '{value}': {str(e)}")
            # Return safe defaults on error
            return (str(value) if value is not None else "0", 0, 0.0)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "PrepackNumberTypeConverter": PrepackNumberTypeConverter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PrepackNumberTypeConverter": "💀Prepack Number Type Converter"
}
