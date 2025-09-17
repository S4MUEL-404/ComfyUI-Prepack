"""Prepack_Int_Split: split a string into two integers using selectable separator."""


class PrepackIntSplit:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", {
                    "default": "0,0",
                    "multiline": False,
                    "tooltip": "String containing up to four integers separated by the chosen separator."
                }),
                "separator": (["Comma", "Semicolon", "Space", "Newline", "Forward Slash"], {
                    "default": "Comma",
                    "tooltip": "Separator used between the integers in the input string."
                }),
            }
        }

    RETURN_TYPES = ("INT", "INT", "INT", "INT")
    RETURN_NAMES = ("int1", "int2", "int3", "int4")
    OUTPUT_TOOLTIPS = (
        "First integer extracted from the input string.",
        "Second integer extracted from the input string.",
        "Third integer extracted from the input string (0 if not present).",
        "Fourth integer extracted from the input string (0 if not present)."
    )
    FUNCTION = "split_ints"

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Split a string into up to four integers using selectable separator (comma, semicolon, space, newline, or forward slash)."

    def split_ints(self, input_string: str, separator: str):
        # Define separator mapping
        separator_map = {
            "Comma": ",",
            "Semicolon": ";",
            "Space": " ",
            "Newline": "\n",
            "Forward Slash": "/"
        }
        
        # Get the actual separator character
        sep_char = separator_map.get(separator, ",")
        
        try:
            # Split the input string by the separator
            parts = input_string.split(sep_char)
            
            # Ensure we have at least 4 parts, pad with "0" as needed
            while len(parts) < 4:
                parts.append("0")
            
            # Convert the first four parts to integers
            int1 = int(parts[0].strip())
            int2 = int(parts[1].strip())
            int3 = int(parts[2].strip())
            int4 = int(parts[3].strip())
            
            return (int1, int2, int3, int4)
            
        except (ValueError, IndexError) as e:
            # If conversion fails, return default values
            print(f"Error parsing integers from '{input_string}': {str(e)}. Using defaults (0, 0, 0, 0).")
            return (0, 0, 0, 0)
