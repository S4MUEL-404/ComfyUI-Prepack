import folder_paths
import comfy.sd
import comfy.utils
import os
import glob
from server import PromptServer
from aiohttp import web

"""Prepack_Loras: load and apply up to 3 LoRA adapters to model and CLIP."""


# HTTP API routes for LoRA text document functionality
@PromptServer.instance.routes.get("/prepack/lora-texts/{lora_name}")
async def get_lora_texts(request):
    """Get available text documents for a LoRA file"""
    lora_name = request.match_info["lora_name"]
    
    try:
        # Get full path of the LoRA file
        lora_path = folder_paths.get_full_path("loras", lora_name)
        if not lora_path:
            return web.json_response([])
        
        # Get the directory and base name without extension
        lora_dir = os.path.dirname(lora_path)
        lora_base = os.path.splitext(os.path.basename(lora_path))[0]
        
        # Look for folder with same name as LoRA file
        text_folder = os.path.join(lora_dir, lora_base)
        text_files = []
        
        if os.path.isdir(text_folder):
            # Find all .txt files in the folder
            txt_pattern = os.path.join(text_folder, "*.txt")
            for txt_file in sorted(glob.glob(txt_pattern)):
                txt_name = os.path.basename(txt_file)
                text_files.append(txt_name)
        
        return web.json_response(text_files)
    
    except Exception as e:
        print(f"Error getting LoRA texts for {lora_name}: {str(e)}")
        return web.json_response([])


@PromptServer.instance.routes.get("/prepack/lora-text-content/{lora_name}/{text_name}")
async def get_lora_text_content(request):
    """Get content of a specific text document"""
    lora_name = request.match_info["lora_name"]
    text_name = request.match_info["text_name"]
    
    try:
        # Get full path of the LoRA file
        lora_path = folder_paths.get_full_path("loras", lora_name)
        if not lora_path:
            return web.Response(text="", content_type="text/plain")
        
        # Get the directory and base name without extension
        lora_dir = os.path.dirname(lora_path)
        lora_base = os.path.splitext(os.path.basename(lora_path))[0]
        
        # Construct path to text file
        text_file_path = os.path.join(lora_dir, lora_base, text_name)
        
        # Security check: ensure the file is within the expected directory
        if not os.path.commonpath([os.path.dirname(text_file_path), lora_dir]) == lora_dir:
            return web.Response(text="Access denied", status=403)
        
        # Read and return file content
        if os.path.isfile(text_file_path):
            with open(text_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return web.Response(text=content, content_type="text/plain")
        else:
            return web.Response(text="", content_type="text/plain")
    
    except Exception as e:
        print(f"Error getting LoRA text content for {lora_name}/{text_name}: {str(e)}")
        return web.Response(text="", content_type="text/plain")


class PrepackLoras:
    def __init__(self):
        self.loaded_lora = None

    @classmethod
    def INPUT_TYPES(s):
        lora_list = ["None"] + folder_paths.get_filename_list("loras")
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The diffusion model to apply LoRA adapters to."}),
                "clip": ("CLIP", {"tooltip": "The CLIP encoder to apply LoRA adapters to."}),
                "lora_name_1": (lora_list, {
                    "tooltip": "Select the first LoRA file to apply (choose 'None' to skip)."
                }),
                "lora_text_1": ("STRING", {
                    "default": "None",
                    "tooltip": "Select text document associated with the first LoRA (automatically populated)."
                }),
                "strength_model_1": ("FLOAT", {
                    "default": 1.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the diffusion model. Typical range [-2.0, 2.0]; 0 disables."
                }),
                "strength_clip_1": ("FLOAT", {
                    "default": 1.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the CLIP encoder. Typical range [-2.0, 2.0]; 0 disables."
                }),
            },
            "optional": {
                "lora_name_2": (lora_list, {
                    "default": "None",
                    "tooltip": "Select the second LoRA file to apply (optional, choose 'None' to skip)."
                }),
                "lora_text_2": ("STRING", {
                    "default": "None",
                    "tooltip": "Select text document associated with the second LoRA (automatically populated)."
                }),
                "strength_model_2": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the diffusion model. Typical range [-2.0, 2.0]; 0 disables."
                }),
                "strength_clip_2": ("FLOAT", {
                    "default": 1.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the CLIP encoder. Typical range [-2.0, 2.0]; 0 disables."
                }),
                "lora_name_3": (lora_list, {
                    "default": "None",
                    "tooltip": "Select the third LoRA file to apply (optional, choose 'None' to skip)."
                }),
                "lora_text_3": ("STRING", {
                    "default": "None",
                    "tooltip": "Select text document associated with the third LoRA (automatically populated)."
                }),
                "strength_model_3": ("FLOAT", {
                    "default": 0.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the diffusion model. Typical range [-2.0, 2.0]; 0 disables."
                }),
                "strength_clip_3": ("FLOAT", {
                    "default": 1.0,
                    "min": -100.0,
                    "max": 100.0,
                    "step": 0.01,
                    "tooltip": "Strength for the CLIP encoder. Typical range [-2.0, 2.0]; 0 disables."
                }),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "lora_path", "lora_text")
    OUTPUT_TOOLTIPS = (
        "The diffusion model with up to 3 LoRAs applied.",
        "The CLIP model with up to 3 LoRAs applied.",
        "Text description of applied LoRAs and their strengths (can be empty if no LoRAs applied).",
        "Content of selected text documents from all LoRAs, separated by commas (can be empty if no texts selected)."
    )
    FUNCTION = "load_loras"

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Load and apply up to 3 LoRA adapters to both the diffusion model and the CLIP encoder; also returns a formatted LoRA prompt string."
    
    @classmethod
    def IS_CHANGED(s, **kwargs):
        # Always allow execution to avoid validation issues with dynamic inputs
        return float("nan")
    
    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        # Custom validation that allows any text file name
        return True

    def load_loras(self, model, clip, lora_name_1, lora_text_1, strength_model_1, strength_clip_1, 
                   lora_name_2="None", lora_text_2="None", strength_model_2=0.0, strength_clip_2=1.0,
                   lora_name_3="None", lora_text_3="None", strength_model_3=0.0, strength_clip_3=1.0):
        
        loras_to_load = [(lora_name_1, float(strength_model_1), float(strength_clip_1))]
        if lora_name_2 != "None":
            loras_to_load.append((lora_name_2, float(strength_model_2), float(strength_clip_2)))
        if lora_name_3 != "None":
            loras_to_load.append((lora_name_3, float(strength_model_3), float(strength_clip_3)))

        current_model = model
        current_clip = clip
        for lora_name, strength_model, strength_clip in loras_to_load:
            # Skip when user selects "None" for a LoRA slot
            if lora_name == "None":
                continue
            if strength_model == 0 and strength_clip == 0:
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

                model_lora, clip_lora = comfy.sd.load_lora_for_models(
                    current_model, current_clip, lora, strength_model, strength_clip
                )
                current_model = model_lora
                current_clip = clip_lora
            except Exception as e:
                print(f"Warning: Failed to load LoRA '{lora_name}': {str(e)}. Skipping this LoRA.")
                continue

        # Generate lora_path output (LoRA file paths with strengths)
        lora_path_parts = []
        for lora_name, strength_model, _ in loras_to_load:
            if lora_name != "None":  # Include all selected LoRAs regardless of strength
                formatted_strength = f"{strength_model:.1f}"
                lora_path_parts.append(f"<lora:{lora_name}:{formatted_strength}>")
        lora_path_output = ", ".join(lora_path_parts)
        
        # Generate lora_text output (text content from selected documents)
        lora_text_contents = []
        lora_text_pairs = [
            (lora_name_1, lora_text_1),
            (lora_name_2, lora_text_2),
            (lora_name_3, lora_text_3)
        ]
        
        for lora_name, text_name in lora_text_pairs:
            if lora_name != "None" and text_name != "None":
                try:
                    lora_path = folder_paths.get_full_path("loras", lora_name)
                    if lora_path:
                        lora_dir = os.path.dirname(lora_path)
                        lora_base = os.path.splitext(os.path.basename(lora_path))[0]
                        text_file_path = os.path.join(lora_dir, lora_base, text_name)
                        
                        if os.path.isfile(text_file_path):
                            with open(text_file_path, 'r', encoding='utf-8') as f:
                                content = f.read().strip()
                                if content:  # Only add non-empty content
                                    lora_text_contents.append(content)
                except Exception as e:
                    print(f"Warning: Failed to read text file '{text_name}' for LoRA '{lora_name}': {str(e)}")
                    continue
        
        lora_text_output = ", ".join(lora_text_contents)
        
        return (current_model, current_clip, lora_path_output, lora_text_output)


