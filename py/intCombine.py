"""Prepack_Int_Combine: combine two integers with selectable separator."""


class PrepackIntCombine:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "int1": ("INT", {
                    "default": 0,
                    "min": -0x7fffffff,
                    "max": 0x7fffffff,
                    "tooltip": "First integer value to combine."
                }),
                "int2": ("INT", {
                    "default": 0,
                    "min": -0x7fffffff,
                    "max": 0x7fffffff,
                    "tooltip": "Second integer value to combine."
                }),
            },
            "optional": {
                "int3": ("INT", {
                    "default": 0,
                    "min": -0x7fffffff,
                    "max": 0x7fffffff,
                    "tooltip": "Third integer value to combine (optional)."
                }),
                "int4": ("INT", {
                    "default": 0,
                    "min": -0x7fffffff,
                    "max": 0x7fffffff,
                    "tooltip": "Fourth integer value to combine (optional)."
                }),
                "separator": (["Comma", "Semicolon", "Space", "Newline", "Forward Slash"], {
                    "default": "Comma",
                    "tooltip": "Separator to use between the integers."
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("combined",)
    OUTPUT_TOOLTIPS = ("Combined string with up to four integers separated by the chosen separator.",)
    FUNCTION = "combine_ints"

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Combine up to four integers into a string with selectable separator (comma, semicolon, space, newline, or forward slash)."

    def combine_ints(self, int1: int, int2: int, int3=None, int4=None, separator="Comma"):
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
        
        # Build list of integers to combine
        integers = [int1, int2]
        
        # Add optional integers if they are provided (not None)
        if int3 is not None:
            integers.append(int3)
        if int4 is not None:
            integers.append(int4)
        
        # Combine the integers with the separator
        combined = sep_char.join(str(i) for i in integers)
        
        return (combined,)
