import torch
import comfy.samplers
import comfy.sample
import comfy.utils
import latent_preview

"""
PrepackKsamplerAdvanced: 完全照抄 ComfyUI 原生 KSamplerAdvanced 實現
"""

def common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0, disable_noise=False, start_step=None, last_step=None, force_full_denoise=False):
    latent_image = latent["samples"]
    latent_image = comfy.sample.fix_empty_latent_channels(model, latent_image)

    if disable_noise:
        noise = torch.zeros(latent_image.size(), dtype=latent_image.dtype, layout=latent_image.layout, device="cpu")
    else:
        batch_inds = latent["batch_index"] if "batch_index" in latent else None
        noise = comfy.sample.prepare_noise(latent_image, seed, batch_inds)

    noise_mask = None
    if "noise_mask" in latent:
        noise_mask = latent["noise_mask"]

    callback = latent_preview.prepare_callback(model, steps)
    disable_pbar = not comfy.utils.PROGRESS_BAR_ENABLED
    samples = comfy.sample.sample(model, noise, steps, cfg, sampler_name, scheduler, positive, negative, latent_image,
                                  denoise=denoise, disable_noise=disable_noise, start_step=start_step, last_step=last_step,
                                  force_full_denoise=force_full_denoise, noise_mask=noise_mask, callback=callback, disable_pbar=disable_pbar, seed=seed)
    out = latent.copy()
    out["samples"] = samples
    return (out, )


class PrepackKsamplerAdvanced:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"model": ("MODEL",),
                    "add_noise": (["enable", "disable"], ),
                    "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "control_after_generate": True}),
                    "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                    "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01}),
                    "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                    "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                    "positive": ("CONDITIONING", ),
                    "negative": ("CONDITIONING", ),
                    "latent_image": ("LATENT", ),
                    "start_at_step": ("INT", {"default": 0, "min": 0, "max": 10000}),
                    "end_at_step": ("INT", {"default": 10000, "min": 0, "max": 10000}),
                    "return_with_leftover_noise": (["disable", "enable"], ),
                     }
                }

    RETURN_TYPES = ("LATENT", "STRING")
    RETURN_NAMES = ("latent", "info")
    OUTPUT_TOOLTIPS = (
        "The processed latent samples with advanced sampling options applied.",
        "Advanced sampling process information including parameters and status."
    )
    FUNCTION = "sample"
    CATEGORY = "💀Prepack"
    DESCRIPTION = "Advanced KSampler that returns latent instead of decoded image, matching native behavior exactly."

    def sample(self, model, add_noise, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, start_at_step, end_at_step, return_with_leftover_noise, denoise=1.0):
        try:
            
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
                "seed": str(noise_seed),
                "steps": str(steps),
                "cfg": str(cfg),
                "sampler_name": str(sampler_name),
                "scheduler": str(scheduler),
                "denoise": str(denoise),
                "add_noise": str(add_noise),
                "start_at_step": str(start_at_step),
                "end_at_step": str(end_at_step),
                "return_with_leftover_noise": str(return_with_leftover_noise)
            }
            
            force_full_denoise = True
            if return_with_leftover_noise == "enable":
                force_full_denoise = False
            disable_noise = False
            if add_noise == "disable":
                disable_noise = True
            
            result = common_ksampler(model, noise_seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise, disable_noise=disable_noise, start_step=start_at_step, last_step=end_at_step, force_full_denoise=force_full_denoise)
            
            # Format successful sampling info
            info_str = f"latent : {info['latent']}\n" + \
                       f"seed : {info['seed']}\n" + \
                       f"steps : {info['steps']}\n" + \
                       f"cfg : {info['cfg']}\n" + \
                       f"sampler_name : {info['sampler_name']}\n" + \
                       f"scheduler : {info['scheduler']}\n" + \
                       f"denoise : {info['denoise']}\n" + \
                       f"add_noise : {info['add_noise']}\n" + \
                       f"start_at_step : {info['start_at_step']}\n" + \
                       f"end_at_step : {info['end_at_step']}\n" + \
                       f"return_with_leftover_noise : {info['return_with_leftover_noise']}"
            
            return (result[0], info_str)
            
        except Exception as e:
            error_msg = f"Error in PrepackKsamplerAdvanced: {str(e)}"
            print(error_msg)
            # Return error information when sampling fails
            return (None, error_msg)
