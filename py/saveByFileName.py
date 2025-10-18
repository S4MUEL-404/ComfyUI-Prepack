import os
import datetime
import shutil
import folder_paths

"""Prepack Save By File Name: rename and copy files with custom file names without any modification."""


class PrepackSaveByFileName:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filename": ("STRING", {
                    "default": "output",
                    "multiline": False,
                    "tooltip": "Base filename. Add .webp, .jpg, .png etc. to force specific format. Supports {date}, {time}, {timestamp} placeholders."
                }),
                "overwrite": (["false", "true"], {
                    "default": "false",
                    "tooltip": "Whether to overwrite existing files or add suffix."
                }),
            },
            "optional": {
                "image": ("IMAGE", {
                    "tooltip": "Image files: PNG, JPG, JPEG, GIF, WebP, APNG formats (preserves animation)."
                }),
                "video": ("*", {
                    "tooltip": "Video files: MP4, AVI formats."
                }),
                "text": ("STRING", {
                    "tooltip": "Text content to save as file.",
                    "forceInput": True
                })
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("file_path", "filename")
    OUTPUT_TOOLTIPS = (
        "Full path to the renamed file.",
        "Final filename used for renaming."
    )
    FUNCTION = "save_by_filename"
    OUTPUT_NODE = True

    CATEGORY = "💀Prepack"
    DESCRIPTION = "Rename and copy files with custom file names without any modification. Preserves original format and content."

    def save_by_filename(self, filename, overwrite, image=None, video=None, text=None):
        # SaveByFileName v1.2 - Format preservation enabled by default
        try:
            # Find which input was provided
            file_data = None
            file_type = None
            
            if image is not None:
                file_data = image
                file_type = 'image'
            elif video is not None:
                file_data = video
                file_type = 'video'
            elif text is not None:
                file_data = text
                file_type = 'text'
            else:
                raise ValueError("No input provided. Please connect image, video, or text.")
            
            # Process filename placeholders
            processed_filename = self.process_filename_placeholders(filename)
            
            # Handle different file types
            if file_type == 'text':
                # For text input, save directly as text file
                output_path = self.determine_output_path(processed_filename, None, 'txt', overwrite)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(file_data))
                    
                output_filename = os.path.basename(output_path)
                print(f"Text saved: {output_path}")
                
            else:
                # For image/video types, try to get source file path first
                source_path = self.get_source_file_path(file_data)
                
                if source_path and os.path.isfile(source_path):
                    # Found existing file - copy it directly
                    original_ext = os.path.splitext(source_path)[1].lstrip('.')
                    if not original_ext:
                        original_ext = 'png' if file_type == 'image' else 'mp4'
                    
                    output_path = self.determine_output_path(processed_filename, source_path, original_ext, overwrite)
                    shutil.copy2(source_path, output_path)
                    
                    output_filename = os.path.basename(output_path)
                    print(f"File renamed and copied: {source_path} -> {output_path}")
                    
                else:
                    # No source file found - handle tensor data
                    if file_type == 'image':
                        
                        # For image tensor, try to preserve format if specified by user or detect from tensor
                        user_ext = None
                        if '.' in processed_filename:
                            user_ext = os.path.splitext(processed_filename)[1].lstrip('.')
                        
                        # Try to detect original format from tensor metadata
                        detected_ext = self.detect_image_format(file_data)
                        
                        # If no format detected, try to infer from context
                        if not detected_ext and not user_ext:
                            detected_ext = self.infer_format_from_context()
                        
                        # Priority: user specified > detected format > png default
                        default_ext = user_ext if user_ext else (detected_ext if detected_ext else 'png')
                        output_path = self.determine_output_path(processed_filename, None, default_ext, overwrite)
                        self.save_image_tensor(file_data, output_path)
                        
                    elif file_type == 'video':
                        
                        # Handle user-specified extension
                        user_ext = None
                        if '.' in processed_filename:
                            user_ext = os.path.splitext(processed_filename)[1].lstrip('.')
                        
                        # For video, check if it's a file path or tensor
                        if isinstance(file_data, str) and os.path.isfile(file_data):
                            # It's a file path
                            original_ext = os.path.splitext(file_data)[1].lstrip('.')
                            if not original_ext:
                                original_ext = 'mp4'
                            final_ext = user_ext if user_ext else original_ext
                            output_path = self.determine_output_path(processed_filename, file_data, final_ext, overwrite)
                            shutil.copy2(file_data, output_path)
                        else:
                            # Handle video objects or tensor data
                            default_ext = user_ext if user_ext else 'mp4'
                            output_path = self.determine_output_path(processed_filename, None, default_ext, overwrite)
                            
                            # Try to save video data
                            try:
                                self.save_video_data(file_data, output_path)
                            except Exception as save_error:
                                print(f"Error saving video data: {str(save_error)}")
                                # Fallback: try to extract file path from video object
                                video_source = self.extract_video_source_path(file_data)
                                if video_source and os.path.isfile(video_source):
                                    shutil.copy2(video_source, output_path)
                                else:
                                    raise Exception(f"Cannot process video data of type {type(file_data)}")
                        
                    output_filename = os.path.basename(output_path)
                    print(f"{file_type.capitalize()} saved: {output_path}")
            
            return (output_path, output_filename)
            
        except Exception as e:
            print(f"Error in PrepackSaveByFileName: {str(e)}")
            return ("", "")

    def process_filename_placeholders(self, filename):
        """Process placeholders in filename like {date}, {time}, {timestamp}"""
        now = datetime.datetime.now()
        
        placeholders = {
            "{date}": now.strftime("%Y-%m-%d"),
            "{time}": now.strftime("%H-%M-%S"),
            "{timestamp}": str(int(now.timestamp())),
            "{datetime}": now.strftime("%Y-%m-%d_%H-%M-%S")
        }
        
        processed = str(filename)
        for placeholder, value in placeholders.items():
            processed = processed.replace(placeholder, value)
        
        # Remove invalid filename characters but preserve path separators
        # Allow forward slashes for directory creation
        invalid_chars = '<>:"|?*'
        for char in invalid_chars:
            processed = processed.replace(char, "_")
        
        # Convert backslashes to forward slashes for consistent path handling
        processed = processed.replace("\\", "/")
        
        return processed


    def determine_output_path(self, processed_filename, source_path, default_ext, overwrite):
        """Determine output path with smart extension handling and directory creation"""
        # Check if filename already has an extension
        filename_name, filename_ext = os.path.splitext(processed_filename)
        
        if filename_ext:  # User specified extension in filename
            # Use user-specified extension, remove the dot
            final_ext = filename_ext.lstrip('.')
            final_filename = processed_filename
        else:  # No extension in filename
            # Use source file extension or default
            final_ext = default_ext
            final_filename = f"{processed_filename}.{final_ext}"
        
        # Create full output path
        output_path = os.path.join(self.output_dir, final_filename)
        
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created directory: {output_dir}")
        
        # Handle file conflicts
        return self.get_unique_filename(output_path, overwrite)
    
    def get_unique_filename(self, base_path, overwrite):
        """Get unique filename if file exists and overwrite is false"""
        if overwrite == "true" or not os.path.exists(base_path):
            return base_path
        
        directory = os.path.dirname(base_path)
        filename = os.path.basename(base_path)
        name, ext = os.path.splitext(filename)
        
        counter = 1
        while True:
            new_filename = f"{name}_{counter:03d}{ext}"
            new_path = os.path.join(directory, new_filename)
            if not os.path.exists(new_path):
                return new_path
            counter += 1
    
    def get_source_file_path(self, file):
        """Get source file path from various input types"""
        try:
            # Direct string file path
            if isinstance(file, str):
                if os.path.isfile(file):
                    return file
                # Try to decode if it looks like a path
                if '\\' in file or '/' in file:
                    cleaned_path = file.strip('"\'')
                    if os.path.isfile(cleaned_path):
                        return cleaned_path
            
            # Dictionary with file information
            if isinstance(file, dict):
                # Common ComfyUI file dict keys
                for key in ['filename', 'path', 'file_path', 'filepath', 'source_path', 'src_path', 'source_file', 'original_file']:
                    if key in file and isinstance(file[key], str) and os.path.isfile(file[key]):
                        return file[key]
                
                # Check for nested dictionaries
                for key, value in file.items():
                    if isinstance(value, (dict, str)):
                        nested_path = self.get_source_file_path(value)
                        if nested_path:
                            return nested_path
            
            # List or tuple - check all elements
            if isinstance(file, (list, tuple)):
                for item in file:
                    path = self.get_source_file_path(item)
                    if path:
                        return path
            
            # Try hasattr for objects with file attributes
            if hasattr(file, '__dict__'):
                for attr_name in ['filename', 'path', 'file_path', 'source', 'source_file', 'original_file']:
                    if hasattr(file, attr_name):
                        attr_value = getattr(file, attr_name)
                        if isinstance(attr_value, str) and os.path.isfile(attr_value):
                            return attr_value
            
            return None
            
        except Exception as e:
            print(f"Error getting source file path: {str(e)}")
            return None
    
    def detect_image_format(self, file_data):
        """Try to detect image format from various sources"""
        try:
            # Check if file_data has format information
            if hasattr(file_data, 'format') and file_data.format:
                format_name = str(file_data.format).lower()
                if format_name in ['jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp']:
                    return 'jpg' if format_name == 'jpeg' else format_name
            
            # Check metadata or attributes
            if hasattr(file_data, '__dict__'):
                for attr in ['format', 'format_name', 'file_format', 'extension', 'ext', 'source', 'filename']:
                    if hasattr(file_data, attr):
                        value = str(getattr(file_data, attr)).lower()
                        if value in ['jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp']:
                            return 'jpg' if value == 'jpeg' else value
                        # Check if it's a path
                        if '.' in value:
                            ext = os.path.splitext(value)[1].lower().lstrip('.')
                            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                                return 'jpg' if ext == 'jpeg' else ext
            
            # Check if it's a dictionary with format info
            if isinstance(file_data, dict):
                for key in ['format', 'file_format', 'extension', 'ext', 'type', 'source', 'filename']:
                    if key in file_data:
                        value = str(file_data[key]).lower()
                        if value in ['jpeg', 'jpg', 'png', 'gif', 'webp', 'bmp']:
                            return 'jpg' if value == 'jpeg' else value
                        # Check if it's a path
                        if '.' in value:
                            ext = os.path.splitext(value)[1].lower().lstrip('.')
                            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                                return 'jpg' if ext == 'jpeg' else ext
            
            # Try to get format from potential file path in data
            potential_path = self.get_source_file_path(file_data)
            if potential_path:
                ext = os.path.splitext(potential_path)[1].lower().lstrip('.')
                if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
                    return 'jpg' if ext == 'jpeg' else ext
            
            return None
            
        except Exception as e:
            return None
    
    def infer_format_from_context(self):
        """Try to infer image format from context clues"""
        try:
            import folder_paths
            input_dir = folder_paths.get_input_directory()
            if os.path.isdir(input_dir):
                current_time = datetime.datetime.now().timestamp()
                for file in os.listdir(input_dir):
                    if file.lower().endswith('.webp'):
                        file_path = os.path.join(input_dir, file)
                        if os.path.isfile(file_path):
                            mod_time = os.path.getmtime(file_path)
                            if current_time - mod_time < 300:  # Within 5 minutes
                                return 'webp'
            return None
        except Exception as e:
            return None
    
    def extract_video_source_path(self, video_data):
        """Extract source file path from video object"""
        try:
            # Check for methods that might return source information
            method_attrs = ['get_stream_source', 'get_source_path', 'get_file_path']
            for method_name in method_attrs:
                if hasattr(video_data, method_name):
                    try:
                        method = getattr(video_data, method_name)
                        if callable(method):
                            result = method()
                            if isinstance(result, str) and os.path.isfile(result):
                                return result
                    except Exception:
                        continue
            
            # Common video object attributes that might contain file path
            path_attrs = ['filename', 'file_path', 'filepath', 'path', 'source', 'video_path', 'input_path', 'source_file']
            
            for attr in path_attrs:
                if hasattr(video_data, attr):
                    try:
                        value = getattr(video_data, attr)
                        if isinstance(value, str) and os.path.isfile(value):
                            return value
                    except Exception:
                        continue
            
            # If it's a dictionary-like object
            if hasattr(video_data, '__getitem__'):
                for key in path_attrs:
                    try:
                        value = video_data[key]
                        if isinstance(value, str) and os.path.isfile(value):
                            return value
                    except (KeyError, TypeError):
                        continue
            
            return None
            
        except Exception:
            return None
    
    def save_video_data(self, video_data, output_path):
        """Save video data to file - unified method"""
        try:
            # First try to extract source file path and copy directly
            source_path = self.extract_video_source_path(video_data)
            if source_path:
                shutil.copy2(source_path, output_path)
                return
            
            # Check if it's a ComfyUI VideoFromFile object with save_to method
            if hasattr(video_data, 'save_to'):
                try:
                    # Try to use the save_to method
                    video_data.save_to(output_path)
                    return
                except Exception:
                    # Continue to other methods
                    pass
            
            # If no source path and no save_to, try to process as tensor data
            self.save_video_tensor(video_data, output_path)
            
        except Exception as e:
            print(f"Error in save_video_data: {str(e)}")
            raise
    
    def save_image_tensor(self, image_tensor, output_path):
        """Save image tensor to file with animation support"""
        try:
            from PIL import Image
            import numpy as np
            import torch
            
            # Check if we have multiple frames (animation)
            has_animation = False
            if isinstance(image_tensor, torch.Tensor):
                image_np = image_tensor.cpu().numpy()
            else:
                image_np = image_tensor
            
            # Determine output format
            ext = os.path.splitext(output_path)[1].lower().lstrip('.')
            format_map = {
                'jpg': 'JPEG',
                'jpeg': 'JPEG', 
                'png': 'PNG',
                'gif': 'GIF',
                'webp': 'WebP',
                'bmp': 'BMP',
                'apng': 'PNG'
            }
            save_format = format_map.get(ext, 'PNG')
            
            # Check for animation frames
            if len(image_np.shape) == 4 and image_np.shape[0] > 1:
                # Multiple frames - handle as animation
                frames = []
                for i in range(image_np.shape[0]):
                    frame_np = image_np[i]
                    
                    # Convert to uint8
                    if frame_np.dtype == np.float32 or frame_np.dtype == np.float64:
                        frame_np = (frame_np * 255).astype(np.uint8)
                    
                    # Convert to PIL Image
                    if len(frame_np.shape) == 3 and frame_np.shape[2] == 3:
                        pil_frame = Image.fromarray(frame_np, 'RGB')
                    elif len(frame_np.shape) == 3 and frame_np.shape[2] == 4:
                        pil_frame = Image.fromarray(frame_np, 'RGBA')
                    elif len(frame_np.shape) == 3 and frame_np.shape[2] == 1:
                        pil_frame = Image.fromarray(frame_np.squeeze(2), 'L')
                    else:
                        pil_frame = Image.fromarray(frame_np)
                    
                    frames.append(pil_frame)
                
                # Save animation
                if save_format == 'GIF':
                    frames[0].save(
                        output_path,
                        format='GIF',
                        save_all=True,
                        append_images=frames[1:],
                        duration=100,  # 100ms per frame
                        loop=0
                    )
                elif save_format == 'WebP':
                    frames[0].save(
                        output_path,
                        format='WebP',
                        save_all=True,
                        append_images=frames[1:],
                        duration=100,  # 100ms per frame
                        loop=0
                    )
                elif ext == 'apng' or save_format == 'PNG':
                    # APNG support - fallback to first frame if APNG not supported
                    try:
                        frames[0].save(
                            output_path,
                            format='PNG',
                            save_all=True,
                            append_images=frames[1:],
                            duration=100
                        )
                    except:
                        # Fallback to first frame only
                        frames[0].save(output_path, format='PNG')
                        print(f"Warning: APNG not supported, saved first frame only")
                else:
                    # Format doesn't support animation, save first frame
                    pil_image = frames[0]
                    if save_format == 'JPEG' and pil_image.mode == 'RGBA':
                        background = Image.new('RGB', pil_image.size, (255, 255, 255))
                        background.paste(pil_image, mask=pil_image.split()[-1])
                        pil_image = background
                    pil_image.save(output_path, format=save_format)
                    print(f"Warning: {save_format} doesn't support animation, saved first frame only")
                    
            else:
                # Single frame
                if len(image_np.shape) == 4:
                    image_np = image_np[0]  # Take first frame
                
                # Convert to uint8
                if image_np.dtype == np.float32 or image_np.dtype == np.float64:
                    image_np = (image_np * 255).astype(np.uint8)
                
                # Convert to PIL Image
                if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                    pil_image = Image.fromarray(image_np, 'RGB')
                elif len(image_np.shape) == 3 and image_np.shape[2] == 4:
                    pil_image = Image.fromarray(image_np, 'RGBA')
                elif len(image_np.shape) == 3 and image_np.shape[2] == 1:
                    pil_image = Image.fromarray(image_np.squeeze(2), 'L')
                elif len(image_np.shape) == 2:
                    pil_image = Image.fromarray(image_np, 'L')
                else:
                    pil_image = Image.fromarray(image_np)
                
                # Handle JPEG conversion from RGBA
                if save_format == 'JPEG' and pil_image.mode == 'RGBA':
                    background = Image.new('RGB', pil_image.size, (255, 255, 255))
                    background.paste(pil_image, mask=pil_image.split()[-1])
                    pil_image = background
                
                pil_image.save(output_path, format=save_format)
            
        except ImportError:
            print("Warning: PIL not available, saving as pickle")
            import pickle
            with open(output_path, 'wb') as f:
                pickle.dump(image_tensor, f)
    
    def save_video_tensor(self, video_tensor, output_path):
        """Save video tensor to file"""
        try:
            import cv2
            import numpy as np
            import torch
            
            # Convert tensor to numpy
            if isinstance(video_tensor, torch.Tensor):
                video_np = video_tensor.cpu().numpy()
            else:
                video_np = video_tensor
            
            # Handle different video tensor formats
            if len(video_np.shape) == 4:  # [frames, height, width, channels]
                frames, height, width, channels = video_np.shape
            else:
                print("Warning: Unexpected video tensor shape, saving as pickle")
                import pickle
                with open(output_path, 'wb') as f:
                    pickle.dump(video_tensor, f)
                return
            
            # Convert to uint8
            if video_np.dtype == np.float32 or video_np.dtype == np.float64:
                video_np = (video_np * 255).astype(np.uint8)
            
            # Determine codec from extension
            ext = os.path.splitext(output_path)[1].lower().lstrip('.')
            if ext == 'mp4':
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            elif ext == 'avi':
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            else:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            # Create video writer
            fps = 30  # Default FPS
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                raise RuntimeError(f"Could not open video writer for {output_path}")
            
            # Write frames
            for frame_idx in range(frames):
                frame = video_np[frame_idx]
                
                # Convert RGB to BGR for OpenCV
                if channels == 3:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                else:
                    frame_bgr = frame
                    
                out.write(frame_bgr)
            
            out.release()
            
        except ImportError:
            print("Warning: OpenCV not available, saving as pickle")
            import pickle
            with open(output_path, 'wb') as f:
                pickle.dump(video_tensor, f)


