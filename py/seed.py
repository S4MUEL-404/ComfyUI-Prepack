"""Prepack_Random_Int: provide a random integer with button control."""


class PrepackSeed:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff,
                    "tooltip": "Seed value with Random button control."
                }),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("seed",)
    OUTPUT_TOOLTIPS = ("The resolved random integer value (unsigned 64-bit range).",)
    FUNCTION = "make_seed"

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Provide a random integer with button control for generating new random values."

    def make_seed(self, seed: int):
        resolved = int(seed) & 0xffffffffffffffff
        return (resolved,)


