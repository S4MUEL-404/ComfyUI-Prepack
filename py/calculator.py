"""Prepack Calculator: evaluate math expressions with up to 4 variables (a, b, c, d)."""

import re


class PrepackCalculator:
    """
    Calculator node that evaluates mathematical expressions with variables a, b, c, d.
    Supports int and float inputs/outputs.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "formula": ("STRING", {
                    "default": "a + b",
                    "multiline": False,
                    "tooltip": "Math formula using variables a, b, c, d. Example: (a*c)+d/2"
                }),
            },
            "optional": {
                "a": ("INT,FLOAT", {
                    "default": 0.0,
                    "tooltip": "Variable a (int or float)"
                }),
                "b": ("INT,FLOAT", {
                    "default": 0.0,
                    "tooltip": "Variable b (int or float)"
                }),
                "c": ("INT,FLOAT", {
                    "default": 0.0,
                    "tooltip": "Variable c (int or float)"
                }),
                "d": ("INT,FLOAT", {
                    "default": 0.0,
                    "tooltip": "Variable d (int or float)"
                }),
            }
        }
    
    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("result_int", "result_float")
    OUTPUT_TOOLTIPS = (
        "Result as integer (rounded)",
        "Result as float (original precision)"
    )
    FUNCTION = "calculate"
    CATEGORY = "💀Prepack"
    DESCRIPTION = "Calculator node that evaluates math expressions with variables a, b, c, d. Outputs both int and float results."
    
    def calculate(self, formula: str, a=0.0, b=0.0, c=0.0, d=0.0):
        """
        Evaluate the formula with given variables.
        
        Args:
            formula: Math expression string
            a, b, c, d: Variable values (int or float)
            
        Returns:
            Tuple of (int_result, float_result)
        """
        try:
            # Convert inputs to float for calculation
            variables = {
                'a': float(a) if a is not None else 0.0,
                'b': float(b) if b is not None else 0.0,
                'c': float(c) if c is not None else 0.0,
                'd': float(d) if d is not None else 0.0,
            }
            
            # Sanitize formula - only allow safe math operations
            # Remove any dangerous characters/functions
            safe_formula = formula.strip()
            
            # Check for unsafe patterns
            unsafe_patterns = ['__', 'import', 'eval', 'exec', 'open', 'file', 'input']
            for pattern in unsafe_patterns:
                if pattern in safe_formula.lower():
                    raise ValueError(f"Unsafe pattern detected: {pattern}")
            
            # Only allow alphanumeric, math operators, parentheses, and dots
            if not re.match(r'^[a-d0-9+\-*/().%\s]+$', safe_formula, re.IGNORECASE):
                raise ValueError("Formula contains invalid characters")
            
            # Evaluate the formula
            result_float = eval(safe_formula, {"__builtins__": {}}, variables)
            result_int = int(round(result_float))
            
            print(f"[Prepack] 🧮 Calculator: '{formula}' = {result_float} (int: {result_int})")
            
            return (result_int, result_float)
            
        except ZeroDivisionError:
            print(f"[Prepack] ❌ Calculator: Division by zero in formula '{formula}'")
            return (0, 0.0)
        except Exception as e:
            print(f"[Prepack] ❌ Calculator: Error evaluating formula '{formula}': {str(e)}")
            return (0, 0.0)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "PrepackCalculator": PrepackCalculator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PrepackCalculator": "💀Prepack Calculator"
}
