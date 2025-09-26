import os
import torch
import comfy.utils
import comfy.sample
import comfy.samplers
import latent_preview

"""Prepack_Ksampler: sample latent and decode to image in one node."""


class PrepackKsampler:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The model used for denoising the input latent."}),
                "positive": ("CONDITIONING", {"tooltip": "Positive conditioning (CFG target)."}),
                "negative": ("CONDITIONING", {"tooltip": "Negative conditioning (CFG target to avoid)."}),
                "vae": ("VAE", {"tooltip": "The VAE model used for decoding the latent to image."}),
                "latent_image": ("LATENT", {"tooltip": "The input latent to denoise (from VAE Encode or Empty Latent Image)."}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "tooltip": "The random seed used for creating the noise."}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000, "tooltip": "The number of steps used in the denoising process."}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step": 0.1, "round": 0.01, "tooltip": "The Classifier-Free Guidance scale."}),
                "sampler_name": (comfy.samplers.KSampler.SAMPLERS, {"tooltip": "The algorithm used when sampling."}),
                "scheduler": (comfy.samplers.KSampler.SCHEDULERS, {"tooltip": "The noise schedule applied during sampling."}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "Relative denoising strength: 1.0 = full denoise; <1.0 = partial denoise (img2img)."}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    OUTPUT_TOOLTIPS = (
        "Decoded image tensor (NCHW, float32, range 0..1).",
        "Sampling process information including model, prompts, parameters, and status."
    )
    FUNCTION = "sample_and_decode"

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Run KSampler and then decode with VAE in a single node."

    def sample_and_decode(self, model, positive, negative, vae, latent_image, seed, steps, cfg, sampler_name, scheduler, denoise=1.0):
        try:
            debug = os.environ.get("PREPACK_DEBUG") == "1"
            
            
            # Calculate output dimensions from latent
            latent_samples = latent_image.get('samples')
            if latent_samples is not None:
                # For most models, latent is downscaled by 8x
                batch, channels, latent_h, latent_w = latent_samples.shape
                output_w = latent_w * 8
                output_h = latent_h * 8
                latent_info = f"{output_w}x{output_h}"
            else:
                latent_info = "Unknown"
            
            # Initialize sampling info
            info = {
                "latent": latent_info,
                "seed": str(seed),
                "steps": str(steps),
                "cfg": str(cfg),
                "sampler_name": str(sampler_name),
                "scheduler": str(scheduler),
                "denoise": str(denoise)
            }

            latent = latent_image.copy()
            latent_samples = latent.get("samples")
            if latent_samples is None or latent_samples.numel() == 0:
                raise ValueError("Latent samples are empty or invalid")

            nonzero = torch.count_nonzero(latent_samples).item()
            if debug:
                if nonzero == 0:
                    print(f"Processing empty latent image with shape: {latent_samples.shape}")
                else:
                    print(f"Processing latent with {nonzero} non-zero values")

            latent_samples = comfy.sample.fix_empty_latent_channels(model, latent_samples)
            if debug:
                print(f"Latent samples shape: {latent_samples.shape}")

            noise = comfy.sample.prepare_noise(latent_samples, seed, latent.get("batch_index", None))
            noise_mask = latent.get("noise_mask", None)

            callback = latent_preview.prepare_callback(model, steps)
            disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED

            samples = comfy.sample.sample(
                model, noise, steps, cfg, sampler_name, scheduler, positive, negative, latent_samples,
                denoise=denoise, disable_noise=False, start_step=None, last_step=None,
                force_full_denoise=False, noise_mask=noise_mask, callback=callback,
                disable_pbar=disable_pbar
            )
            if debug:
                print(f"Samples shape: {samples.shape}")

            with torch.no_grad():
                images = vae.decode(samples)
            if len(images.shape) == 5:
                images = images.reshape(-1, images.shape[-3], images.shape[-2], images.shape[-1])
            if debug:
                print(f"Images shape: {images.shape}")

            # Format successful sampling info
            info_str = f"latent : {info['latent']}\n" + \
                       f"seed : {info['seed']}\n" + \
                       f"steps : {info['steps']}\n" + \
                       f"cfg : {info['cfg']}\n" + \
                       f"sampler_name : {info['sampler_name']}\n" + \
                       f"scheduler : {info['scheduler']}\n" + \
                       f"denoise : {info['denoise']}"
                       
            return (images, info_str)
        except Exception as e:
            error_msg = f"Error in PrepackKsampler: {str(e)}"
            print(error_msg)
            # Return error information when sampling fails
            return (None, error_msg)
