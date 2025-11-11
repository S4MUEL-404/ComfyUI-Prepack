class AlwaysEqualProxy(str):
    """Proxy class to accept any input type"""
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False


# ANSI color utilities for pretty logging
class _PrepackColors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

class PrepackLogger:
    """Unified colorful logger for Prepack nodes"""
    PREFIX = "Prepack"

    @staticmethod
    def _fmt(level: str, node: str, message: str) -> str:
        # Choose icon and color by level
        if level == "ERROR":
            icon, color = "❌", _PrepackColors.RED
        elif level == "WARNING":
            icon, color = "⚠️", _PrepackColors.YELLOW
        elif level == "SUCCESS":
            icon, color = "✅", _PrepackColors.GREEN
        elif level == "INFO":
            icon, color = "ℹ️", _PrepackColors.CYAN
        elif level == "DEBUG":
            icon, color = "🔧", _PrepackColors.DIM
        else:
            icon, color = "📝", _PrepackColors.WHITE
        # Format: [Prepack] ICON Node: message (with color and bold prefix)
        return f"{color}{_PrepackColors.BOLD}[{PrepackLogger.PREFIX}]{_PrepackColors.RESET} {icon} {color}{node}:{_PrepackColors.RESET} {message}"

    @staticmethod
    def info(node: str, message: str):
        print(PrepackLogger._fmt("INFO", node, message))

    @staticmethod
    def debug(node: str, message: str):
        print(PrepackLogger._fmt("DEBUG", node, message))

    @staticmethod
    def warning(node: str, message: str):
        print(PrepackLogger._fmt("WARNING", node, message))

    @staticmethod
    def error(node: str, message: str):
        print(PrepackLogger._fmt("ERROR", node, message))

    @staticmethod
    def success(node: str, message: str):
        print(PrepackLogger._fmt("SUCCESS", node, message))


class PrepackMergeSelector:
    """
    Merge Selector node that outputs one of 5 arbitrary type inputs based on selector number.
    Only outputs the selected input, ignoring all others.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        Define input types for the merge selector node.
        """
        return {
            "required": {
                "selector": ("INT", {"default": 1, "min": 1, "max": 5}),
            },
            "optional": {
                "input_1": (AlwaysEqualProxy("*"), {}),
                "input_2": (AlwaysEqualProxy("*"), {}),
                "input_3": (AlwaysEqualProxy("*"), {}),
                "input_4": (AlwaysEqualProxy("*"), {}),
                "input_5": (AlwaysEqualProxy("*"), {}),
            }
        }
    
    RETURN_TYPES = (AlwaysEqualProxy("*"),)
    RETURN_NAMES = ("output",)
    FUNCTION = "select"
    CATEGORY = "💀Prepack"
    
    def select(self, selector, input_1=None, input_2=None, input_3=None, input_4=None, input_5=None):
        """
        Select and output one of the 5 inputs based on selector number.
        
        Args:
            selector: Integer (1-5) indicating which input to output
            input_1: Optional first input of any type
            input_2: Optional second input of any type
            input_3: Optional third input of any type
            input_4: Optional fourth input of any type
            input_5: Optional fifth input of any type
            
        Returns:
            The selected input based on selector value
        """
        
        # Map selector to corresponding input
        inputs = {
            1: input_1,
            2: input_2,
            3: input_3,
            4: input_4,
            5: input_5
        }
        
        # Get the selected input
        selected_input = inputs.get(selector)
        
        # Check if the selected input is connected
        if selected_input is None:
            PrepackLogger.warning(
                "MergeSelector",
                f"Selector={selector} but input_{selector} is not connected • returning None"
            )
            return (None,)
        
        # Log successful selection
        input_type = type(selected_input).__name__
        PrepackLogger.success(
            "MergeSelector",
            f"Selector={selector} • Selected input_{selector} • Type={input_type}"
        )
        
        return (selected_input,)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "💀Prepack Merge Selector": PrepackMergeSelector
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "💀Prepack Merge Selector": "💀Prepack Merge Selector"
}
