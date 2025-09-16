import folder_paths
import torch
import comfy.sd
import nodes

"""Prepack_Model_DualCLIP: load a diffusion UNet and a dual-CLIP pair in one step."""


class PrepackModelDualCLIP:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "unet_name": (folder_paths.get_filename_list("diffusion_models"), {
                    "tooltip": "The name of the diffusion model (UNET) to load."
                }),
                "weight_dtype": (["default", "fp8_e4m3fn", "fp8_e4m3fn_fast", "fp8_e5m2"], {
                    "tooltip": "The weight dtype for the diffusion model."
                }),
                "vae_name": (folder_paths.get_filename_list("vae"), {
                    "tooltip": "The VAE to load."
                }),
                "clip_name1": (folder_paths.get_filename_list("text_encoders"), {
                    "tooltip": "The name of the first CLIP model to load."
                }),
                "clip_name2": (folder_paths.get_filename_list("text_encoders"), {
                    "tooltip": "The name of the second CLIP model to load."
                }),
                "type": (["sdxl", "sd3", "flux", "hunyuan_video"], {
                    "tooltip": "The type of CLIP configuration to use."
                }),
            },
            "optional": {
                "device": (["default", "cpu"], {"advanced": True, "tooltip": "Device override for CLIP loading/offloading. Use 'cpu' to force CPU; 'default' lets Comfy manage devices."}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    RETURN_NAMES = ("model", "clip", "vae")
    OUTPUT_TOOLTIPS = (
        "The loaded diffusion model (UNET) used for denoising latents.",
        "The loaded dual CLIP model used for encoding text prompts.",
        "The loaded VAE for encoding/decoding latents (can be None if loading fails)."
    )
    FUNCTION = "load_prepack"

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Load a diffusion UNet and a dual-CLIP pair in one step (SDXL, SD3, FLUX, optional Hunyuan Video)."

    def load_prepack(self, unet_name, weight_dtype, vae_name, clip_name1, clip_name2, type, device="default"):
        model_options = {}
        try:
            if weight_dtype == "fp8_e4m3fn":
                model_options["dtype"] = torch.float8_e4m3fn
            elif weight_dtype == "fp8_e4m3fn_fast":
                model_options["dtype"] = torch.float8_e4m3fn
                model_options["fp8_optimizations"] = True
            elif weight_dtype == "fp8_e5m2":
                model_options["dtype"] = torch.float8_e5m2
        except AttributeError:
            # Fallback silently if torch version doesn't support float8 types
            pass

        try:
            unet_path = folder_paths.get_full_path_or_raise("diffusion_models", unet_name)
            model = comfy.sd.load_diffusion_model(unet_path, model_options=model_options)
        except Exception as e:
            raise RuntimeError(f"Failed to load diffusion model '{unet_name}': {str(e)}")

        try:
            clip_path1 = folder_paths.get_full_path_or_raise("text_encoders", clip_name1)
            clip_path2 = folder_paths.get_full_path_or_raise("text_encoders", clip_name2)

            if type == "sdxl":
                clip_type = comfy.sd.CLIPType.STABLE_DIFFUSION
            elif type == "sd3":
                clip_type = comfy.sd.CLIPType.SD3
            elif type == "flux":
                clip_type = comfy.sd.CLIPType.FLUX
            elif type == "hunyuan_video":
                clip_type = getattr(comfy.sd.CLIPType, "HUNYUAN_VIDEO", comfy.sd.CLIPType.STABLE_DIFFUSION)
            else:
                clip_type = comfy.sd.CLIPType.STABLE_DIFFUSION

            clip_model_options = {}
            if device == "cpu":
                clip_model_options["load_device"] = clip_model_options["offload_device"] = torch.device("cpu")

            clip = comfy.sd.load_clip(
                ckpt_paths=[clip_path1, clip_path2],
                embedding_directory=folder_paths.get_folder_paths("embeddings"),
                clip_type=clip_type,
                model_options=clip_model_options
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load CLIP models '{clip_name1}' and '{clip_name2}': {str(e)}")

        try:
            vae = nodes.VAELoader().load_vae(vae_name)[0]
        except Exception as e:
            print(f"Warning: Failed to load VAE '{vae_name}': {str(e)}. Returning None.")
            vae = None

        return (model, clip, vae)


