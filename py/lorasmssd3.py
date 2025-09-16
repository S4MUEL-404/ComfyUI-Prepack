import folder_paths
import comfy.sd
import comfy.utils
import comfy.model_management

"""Prepack_Loras_and_MSSD3: load and apply up to 3 LoRA adapters to model, and apply SD3 model sampling."""


class PrepackLorasAndMSSD3:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        lora_list = ["None"] + folder_paths.get_filename_list("loras")
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The diffusion model to apply LoRA adapters and SD3 sampling to."}),
                "lora_name_1": (lora_list, {
                    "tooltip": "Select the first LoRA file to apply (choose 'None' to skip)."
                }),
                "strength_model_1": ("FLOAT", {
                    "default": 1.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the diffusion model. Typical range [-2.0, 2.0]; 0 disables."
                }),
            },
            "optional": {
                "lora_name_2": (lora_list, {
                    "default": "None",
                    "tooltip": "Select the second LoRA file to apply (optional, choose 'None' to skip)."
                }),
                "strength_model_2": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the diffusion model. Typical range [-2.0, 2.0]; 0 disables."
                }),
                "lora_name_3": (lora_list, {
                    "default": "None",
                    "tooltip": "Select the third LoRA file to apply (optional, choose 'None' to skip)."
                }),
                "strength_model_3": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the diffusion model. Typical range [-2.0, 2.0]; 0 disables."
                }),
                "shift": ("FLOAT", {
                    "default": 3.0,
                    "min": 0.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Shift parameter for SD3 model sampling."
                }),
            }
        }

    RETURN_TYPES = ("MODEL",)
    RETURN_NAMES = ("model",)
    OUTPUT_TOOLTIPS = (
        "The diffusion model with up to 3 LoRAs applied and SD3 model sampling configured.",
    )
    FUNCTION = "load_loras_and_apply_mssd3"

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Load and apply up to 3 LoRA adapters to the diffusion model and apply SD3 model sampling; integrated LoRA + ModelSamplingSD3 functionality."

    def load_loras_and_apply_mssd3(self, model, lora_name_1, strength_model_1,
                                   lora_name_2="None", strength_model_2=0.0,
                                   lora_name_3="None", strength_model_3=0.0,
                                   shift=3.0):
        
        # First apply LoRAs (no CLIP processing)
        loras_to_load = [(lora_name_1, float(strength_model_1))]
        if lora_name_2 != "None":
            loras_to_load.append((lora_name_2, float(strength_model_2)))
        if lora_name_3 != "None":
            loras_to_load.append((lora_name_3, float(strength_model_3)))

        current_model = model
        for lora_name, strength_model in loras_to_load:
            # Skip when user selects "None" for a LoRA slot
            if lora_name == "None":
                continue
            if strength_model == 0:
                continue
            
            try:
                lora_path = folder_paths.get_full_path_or_raise("loras", lora_name)
                lora = None
                if self.loaded_lora is not None:
                    if self.loaded_lora[0] == lora_path:
                        lora = self.loaded_lora[1]
                    else:
                        self.loaded_lora = None

                if lora is None:
                    lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
                    self.loaded_lora = (lora_path, lora)
            except Exception as e:
                print(f"Warning: Failed to load LoRA file '{lora_name}': {str(e)}. Skipping this LoRA.")
                continue

            try:
                # Apply LoRA only to model, not CLIP
                model_lora, _ = comfy.sd.load_lora_for_models(
                    current_model, None, lora, strength_model, 0
                )
                current_model = model_lora
            except Exception as e:
                print(f"Warning: Failed to apply LoRA '{lora_name}': {str(e)}. Skipping this LoRA.")
                continue

        # Apply SD3 model sampling
        current_model = self.apply_sd3_sampling(current_model, shift)

        return (current_model,)

    def apply_sd3_sampling(self, model, shift):
        """Apply SD3 model sampling configuration - safe detection of API availability."""
        try:
            # First check if SD3 sampling classes are available
            sd3_sampling_class = None
            
            # Try to find SD3 sampling class in various possible locations
            try:
                # Option 1: Direct import from ComfyUI's sampling module
                import comfy.model_sampling
                if hasattr(comfy.model_sampling, 'ModelSamplingSD3'):
                    sd3_sampling_class = comfy.model_sampling.ModelSamplingSD3
            except (ImportError, AttributeError):
                pass
            
            # Option 2: Try alternative locations
            if sd3_sampling_class is None:
                try:
                    # Check if available in model_management or other modules
                    if hasattr(comfy.model_management, 'ModelSamplingSD3'):
                        sd3_sampling_class = comfy.model_management.ModelSamplingSD3
                except AttributeError:
                    pass
            
            # Option 3: Check in the model itself for existing sampling config
            if sd3_sampling_class is None and hasattr(model.model, 'model_sampling'):
                current_sampling = model.model.model_sampling
                # If already has shift attribute, just modify it
                if hasattr(current_sampling, 'shift'):
                    try:
                        m = model.clone()
                        m.model.model_sampling.shift = float(shift)
                        return m
                    except Exception:
                        pass
            
            # If we found a proper SD3 sampling class, use it
            if sd3_sampling_class is not None:
                try:
                    m = model.clone()
                    # Create new SD3 sampling instance with shift parameter
                    sd3_sampling = sd3_sampling_class(shift=float(shift))
                    m.model.model_sampling = sd3_sampling
                    return m
                except Exception as create_error:
                    print(f"Info: Could not create SD3 sampling instance: {create_error}")
            
            # Fallback: No proper SD3 API found, but apply basic shift if possible
            if hasattr(model.model, 'model_sampling'):
                try:
                    m = model.clone()
                    # Try to set shift in any way possible
                    if not hasattr(m.model.model_sampling, 'shift'):
                        setattr(m.model.model_sampling, 'shift', float(shift))
                    else:
                        m.model.model_sampling.shift = float(shift)
                    return m
                except Exception:
                    pass
            
            # Ultimate fallback: return original model with info message
            print(f"Info: SD3 sampling API not detected. Shift parameter ({shift}) ignored. Model returned unchanged.")
            return model
            
        except Exception as e:
            # Fallback: return original model if any unexpected error occurs
            print(f"Warning: Unexpected error in SD3 sampling configuration: {e}. Model returned unchanged.")
            return model


