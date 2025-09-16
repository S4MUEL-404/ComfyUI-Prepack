"""Prepack_SetPipe: pack model, clip, vae, lora_text, positive, negative, latent_image, seed, steps, cfg, denoise into a pipe object."""


class PrepackSetPipe:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                "model": ("MODEL", {"tooltip": "The model to pack."}),
                "clip": ("CLIP", {"tooltip": "The CLIP to pack."}),
                "vae": ("VAE", {"tooltip": "The VAE to pack."}),
                "lora_text": ("STRING", {"tooltip": "The LoRA description to pack.", "multiline": False, "forceInput": True}),
                "positive": ("CONDITIONING", {"tooltip": "The positive conditioning to pack."}),
                "negative": ("CONDITIONING", {"tooltip": "The negative conditioning to pack."}),
                "latent_image": ("LATENT", {"tooltip": "The latent image to pack."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "The seed value to pack."}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "tooltip": "The sampling steps to pack."}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1, "tooltip": "The CFG scale to pack."}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "The denoise strength to pack."}),
            }
        }

    RETURN_TYPES = ("PIPE",)
    RETURN_NAMES = ("pipe",)
    OUTPUT_TOOLTIPS = ("The packed pipeline object containing model, clip, vae, lora_text, positive, negative, latent_image, seed, steps, cfg, denoise.",)
    FUNCTION = "set_pipe"
    CATEGORY = "💀Prepack"
    DESCRIPTION = "Pack model, clip, vae, lora_text, positive, negative, latent_image, seed, steps, cfg, denoise into a single pipe object. All inputs are optional with default values."

    def set_pipe(self, model=None, clip=None, vae=None, lora_text=None, 
                 positive=None, negative=None, latent_image=None, 
                 seed=None, steps=None, cfg=None, denoise=None):
        pipe = {
            "model": model,
            "clip": clip,
            "vae": vae,
            "lora_text": lora_text,
            "positive": positive,
            "negative": negative,
            "latent_image": latent_image,
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "denoise": denoise
        }
        return (pipe,)


