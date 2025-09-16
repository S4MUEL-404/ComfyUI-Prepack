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

class PrepackLogicString:
    """
    String logic calculation node with string matching priority.
    When any_name contains any_target_name string, outputs any input;
    otherwise performs string comparison logic.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        """
        Define input types for the string logic calculation node.
        """
        return {
            "required": {
                "target_string": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "true": (AlwaysEqualProxy("*"), {}),
                "false": (AlwaysEqualProxy("*"), {}),
                "any": (AlwaysEqualProxy("*"), {}),
                "string": ("STRING", {"default": "", "multiline": False}),
                "any_target_name": ("STRING", {"default": "", "multiline": False}),
                "any_name": ("STRING", {"default": "", "multiline": False}),
            }
        }
    
    RETURN_TYPES = (AlwaysEqualProxy("*"),)
    RETURN_NAMES = ("output",)
    FUNCTION = "calculate"
    CATEGORY = "💀Prepack"
    
    def calculate(self, target_string, 
                 true=None, false=None, any=None, string=None, 
                 any_target_name=None, any_name=None):
        """
        Execute the string logic calculation with string matching priority.
        
        Args:
            target_string: Target string for comparison
            true: Optional input to return if conditions are met
            false: Optional input to return if conditions are not met
            any: Optional input to return when string match is found
            string: Optional string input for matching against target_string
            any_target_name: Optional target string for any_name matching
            any_name: Optional string input for matching
            
        Returns:
            any, true, or false input based on logic results
        """
        
        # Helper: robust string match (case-insensitive, trimmed)
        def _norm(s):
            return str(s).strip().casefold() if s is not None else ""
        
        # Check for string match only if both any_target_name and any_name are provided
        any_match = (
            any is not None
            and any_target_name is not None and any_name is not None
            and isinstance(any_name, str) and isinstance(any_target_name, str)
            and _norm(any_target_name) != ""
            and (_norm(any_target_name) in _norm(any_name))
        )

        # Case 1: any is connected, and string missing -> use string logic only
        if any is not None and string is None:
            result = any if any_match else (false if false is not None else None)
            PrepackLogger.info(
                "LogicString",
                f"Case 1 • Any-only path • any_match={any_match} • result={'any' if any_match else ('false' if false is not None else 'None')}"
            )
            return (result,)

        # Case 2: any is connected and string present
        # If any string matches -> output any immediately; otherwise fall through to string logic
        if any is not None and any_match:
            PrepackLogger.success(
                "LogicString",
                f"Case 2 • Any-match priority • any_match={any_match} • returning=any"
            )
            return (any,)

        # Case 3: any is not connected -> require string for string logic
        if any is None and string is None:
            result = false if false is not None else None
            PrepackLogger.warning(
                "LogicString",
                f"Case 3 • Missing string • string={string} • result={'false' if false is not None else 'None'}"
            )
            return (result,)

        # String comparison logic (used for Case 2 fallback or Case 3)
        # Check if string contains target_string
        string_match = (
            string is not None and target_string is not None
            and isinstance(string, str) and isinstance(target_string, str)
            and _norm(target_string) != ""
            and (_norm(target_string) in _norm(string))
        )

        output = true if string_match and true is not None else (false if false is not None else None)
        output_name = 'true' if string_match and true is not None else ('false' if false is not None else 'None')
        
        PrepackLogger.info(
            "LogicString",
            (
                "String compare • "
                f"'{_norm(string)}' contains '{_norm(target_string)}' = {string_match} • "
                f"result={output_name}"
            )
        )
        
        return (output,)

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "💀Prepack Logic String": PrepackLogicString
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "💀Prepack Logic String": "💀Prepack Logic String"
}
