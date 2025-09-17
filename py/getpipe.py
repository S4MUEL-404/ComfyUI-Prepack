"""Prepack_GetPipe: unpack a pipe object into model, clip, vae, lora_text, positive, negative, latent_image, seed, steps, cfg, denoise components."""


class PrepackGetPipe:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "pipe": ("PIPE", {"tooltip": "The packed pipeline object."}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "STRING", "CONDITIONING", "CONDITIONING", "LATENT", "INT", "INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("model", "clip", "vae", "lora_text", "lora_path", "positive", "negative", "latent_image", "seed", "steps", "cfg", "denoise")
    OUTPUT_TOOLTIPS = (
        "The diffusion model from the pipe object (can be None).",
        "The CLIP model from the pipe object (can be None).",
        "The VAE from the pipe object (can be None).",
        "The formatted LoRA prompt string from the pipe object (can be None).",
        "The LoRA model path from the pipe object (can be None).",
        "The positive conditioning from the pipe object (can be None).",
        "The negative conditioning from the pipe object (can be None).",
        "The latent image from the pipe object (can be None).",
        "The seed value from the pipe object (can be None).",
        "The sampling steps from the pipe object (can be None).",
        "The CFG scale from the pipe object (can be None).",
        "The denoise strength from the pipe object (can be None)."
    )
    FUNCTION = "get_pipe"
    CATEGORY = "💀Prepack"
    DESCRIPTION = "Unpack a pipe object produced by Prepack_SetPipe into model, clip, vae, lora_text, lora_path, positive, negative, latent_image, seed, steps, cfg, denoise components. All outputs can be None."

    def get_pipe(self, pipe):
        return (
            pipe.get("model", None),
            pipe.get("clip", None),
            pipe.get("vae", None),
            pipe.get("lora_text", None),
            pipe.get("lora_path", None),
            pipe.get("positive", None),
            pipe.get("negative", None),
            pipe.get("latent_image", None),
            pipe.get("seed", None),
            pipe.get("steps", None),
            pipe.get("cfg", None),
            pipe.get("denoise", None)
        )


