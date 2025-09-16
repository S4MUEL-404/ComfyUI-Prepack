class AlwaysEqualProxy(str):
    """Proxy class to accept any input type"""
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False


# ANSI color utilities for pretty logging (inspired by S4Tool-Image)
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

class PrepackLogicInt:
    """
    Logic calculation node with string matching priority and integer comparison fallback.
    When any_name contains any_target_name string, outputs any input;
    otherwise performs integer comparison logic.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        Define input types for the enhanced logic calculation node.
        """
        comparison_options_a = [
            "A = target",
            "A ≠ target", 
            "A < target",
            "A > target",
            "A <= target",
            "A >= target"
        ]
        
        comparison_options_b = [
            "B = target",
            "B ≠ target", 
            "B < target",
            "B > target",
            "B <= target",
            "B >= target"
        ]
        
        return {
            "required": {
                "target_int": ("INT", {"default": 0}),
                "comparison_a": (comparison_options_a, {"default": "A = target"}),
                "comparison_b": (comparison_options_b, {"default": "B = target"}),
            },
            "optional": {
                "true": (AlwaysEqualProxy("*"), {}),
                "false": (AlwaysEqualProxy("*"), {}),
                "any": (AlwaysEqualProxy("*"), {}),
                "int_a": ("INT", {"default": 0}),
                "int_b": ("INT", {"default": 0}),
                "any_target_name": ("STRING", {"default": "", "multiline": False}),
                "any_name": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = (AlwaysEqualProxy("*"),)
    RETURN_NAMES = ("output",)
    FUNCTION = "calculate"
    CATEGORY = "💀Prepack"
    
    def calculate(self, target_int, comparison_a, comparison_b, 
                 true=None, false=None, any=None, int_a=None, int_b=None, 
                 any_target_name=None, any_name=None):
        """
        Execute the enhanced logic calculation with string matching priority.
        
        Args:
            target_int: Target integer for comparison
            comparison_a: Comparison operation for int_a
            comparison_b: Comparison operation for int_b
            true: Optional input to return if conditions are met
            false: Optional input to return if conditions are not met
            any: Optional input to return when string match is found
            int_a: Optional first integer to compare
            int_b: Optional second integer to compare
            any_target_name: Optional target string for any_name matching
            any_name: Optional string input for matching
            
        Returns:
            any, true, or false input based on logic results
        """
        
        # Helper: robust string match (case-insensitive, trimmed)
        def _norm(s):
            return str(s).strip().casefold() if s is not None else ""
        
        # Check for string match only if both any_target_name and any_name are provided
        match = (
            any is not None
            and any_target_name is not None and any_name is not None
            and isinstance(any_name, str) and isinstance(any_target_name, str)
            and _norm(any_target_name) != ""
            and (_norm(any_target_name) in _norm(any_name))
        )

        # Case 1: any is connected, and one or both ints missing -> use string logic only
        if any is not None and (int_a is None or int_b is None):
            result = any if match else (false if false is not None else None)
            PrepackLogger.info(
                "LogicInt",
                f"Case 1 • String-only path • match={match} • result={'any' if match else ('false' if false is not None else 'None')}"
            )
            return (result,)

        # Case 2: any is connected and both ints present
        # If string matches -> output any immediately; otherwise fall through to int logic
        if any is not None and match:
            PrepackLogger.success(
                "LogicInt",
                f"Case 2 • String-match priority • match={match} • returning=any"
            )
            return (any,)

        # Case 3: any is not connected -> require both ints for int logic
        if any is None and (int_a is None or int_b is None):
            result = false if false is not None else None
            PrepackLogger.warning(
                "LogicInt",
                f"Case 3 • Missing integers • int_a={int_a} • int_b={int_b} • result={'false' if false is not None else 'None'}"
            )
            return (result,)

        # Integer comparison logic (used for Case 2 fallback or Case 3)
        # Define comparison functions mapping
        comparison_map = {
            "A = target": lambda a, target: a == target,
            "A ≠ target": lambda a, target: a != target,
            "A < target": lambda a, target: a < target,
            "A > target": lambda a, target: a > target,
            "A <= target": lambda a, target: a <= target,
            "A >= target": lambda a, target: a >= target,
            "B = target": lambda b, target: b == target,
            "B ≠ target": lambda b, target: b != target,
            "B < target": lambda b, target: b < target,
            "B > target": lambda b, target: b > target,
            "B <= target": lambda b, target: b <= target,
            "B >= target": lambda b, target: b >= target,
        }

        comparison_a_func = comparison_map.get(comparison_a)
        comparison_b_func = comparison_map.get(comparison_b)

        result_a = comparison_a_func(int_a, target_int) if comparison_a_func else False
        result_b = comparison_b_func(int_b, target_int) if comparison_b_func else False

        final_result = result_a and result_b
        output = true if final_result and true is not None else (false if false is not None else None)
        output_name = 'true' if final_result and true is not None else ('false' if false is not None else 'None')
        
        PrepackLogger.info(
            "LogicInt",
            (
                "Integer compare • "
                f"{comparison_a}({int_a} vs {target_int})={result_a} • "
                f"{comparison_b}({int_b} vs {target_int})={result_b} • "
                f"final={final_result} • result={output_name}"
            )
        )
        
        return (output,)

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "💀Prepack Logic Int": PrepackLogicInt
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "💀Prepack Logic Int": "💀Prepack Logic Int"
}
