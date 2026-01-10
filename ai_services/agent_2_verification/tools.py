import os
from PIL import Image, ExifTags
import cv2
import numpy as np

class ForensicTools:
    
    @staticmethod
    def analyze_metadata(file_path: str) -> dict:
        risk_flags = []
        software_found = None
        source_type = "camera_or_scanner" # default
        
        try:
            img = Image.open(file_path)
            exif_data = img.getexif()
            
            # --- 1. Social Media / WhatsApp Detection ---
            # WhatsApp images usually have NO metadata at all.
            # Real camera photos have 'Make' and 'Model'.
            has_camera_info = False
            if exif_data:
                # Check for Camera Make (Tag 271) or Model (Tag 272)
                if 271 in exif_data or 272 in exif_data:
                    has_camera_info = True
            
            # If no camera info is found, it's likely a Social Media download or Screenshot
            if not has_camera_info:
                source_type = "social_media_or_screenshot"
                # We do NOT add a risk flag yet. We just note the source.
            
            # --- 2. Explicit "Software" Check ---
            if exif_data:
                # Map tags to names
                exif = {ExifTags.TAGS[k]: v for k, v in exif_data.items() if k in ExifTags.TAGS}
                software_found = exif.get("Software", None)
                
                suspicious_tools = ["Photoshop", "GIMP", "Canva", "Paint", "Edit"]
                if software_found and any(tool.lower() in str(software_found).lower() for tool in suspicious_tools):
                    risk_flags.append(f"Editing Software Detected: {software_found}")

            return {
                "source_type": source_type,
                "software": software_found,
                "risk_flags": risk_flags
            }

        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def perform_ela(file_path: str, source_type: str) -> dict:
        """
        ELA with dynamic sensitivity based on source.
        """
        try:
            original = cv2.imread(file_path)
            if original is None:
                return {"error": "Could not read image"}

            # 1. ELA Process
            temp_file = "temp_ela.jpg"
            # Save at 90% quality to compare
            cv2.imwrite(temp_file, original, [cv2.IMWRITE_JPEG_QUALITY, 90])
            compressed = cv2.imread(temp_file)
            
            # Absolute difference
            diff = cv2.absdiff(original, compressed)
            
            # Enhance brightness to make it visible
            ela_image = cv2.convertScaleAbs(diff, alpha=15, beta=0)
            
            # 2. Smart Scoring
            max_diff = np.max(ela_image)
            
            # --- CRITICAL FIX FOR WHATSAPP ---
            # WhatsApp images are ALREADY compressed. Re-saving them causes very little change.
            # So, a WhatsApp image usually has a LOW max_diff (it's already at the floor).
            # A "Fake" paste usually has a HIGH max_diff (the pasted part is fresher).
            
            tamper_score = 0
            
            if source_type == "social_media_or_screenshot":
                # Relaxed Thresholds for WhatsApp
                if max_diff > 180: # Very bright white spots
                    tamper_score = 70
                elif max_diff > 220:
                    tamper_score = 90
            else:
                # Strict Thresholds for Camera Originals
                if max_diff > 120:
                    tamper_score = 50
                elif max_diff > 150:
                    tamper_score = 80

            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            return {
                "ela_max_diff": float(max_diff),
                "visual_tamper_score": tamper_score
            }

        except Exception as e:
            return {"error": str(e)}
        
        
    @staticmethod
    def check_digital_flatness(file_path: str) -> dict:
        """
        Detects if an image looks 'too digital'.
        Real photos of documents have noise/gradients.
        Digital/Edited documents often have pure white (255,255,255) backgrounds.
        """
        try:
            img = cv2.imread(file_path)
            if img is None:
                return {"error": "Could not read image"}

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Count pixels that are PERFECTLY white (255) or extremely close (254-255)
            # Real camera photos almost NEVER have pure 255 clusters due to sensor noise.
            white_pixels = np.sum(gray >= 254)
            total_pixels = gray.size
            white_ratio = (white_pixels / total_pixels) * 100

            # Logic:
            # - A scanned PDF might have ~10-50% pure white.
            # - A photo of a paper (even via WhatsApp) usually has < 1% pure white.
            # - A "Screenshot" of a fake bank statement often has > 50% pure white.
            
            is_suspicious = False
            if white_ratio > 20: 
                is_suspicious = True
                
            return {
                "flatness_score": float(white_ratio),
                "is_suspicious_digital": is_suspicious
            }

        except Exception as e:
            return {"error": str(e)}