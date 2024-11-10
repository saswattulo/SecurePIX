import streamlit as st
import numpy as np
from PIL import Image, PngImagePlugin
import random
import io
import os



# Reverse color transformation
def reverse_color_transform(image, offset):
    pixels = np.array(image)
    transformed_pixels = (pixels - offset) % 256
    return Image.fromarray(transformed_pixels.astype(np.uint8))

# Unscramble the image based on the provided pattern_key
def unscramble_image(image, pattern_key, grid_size):
    width, height = image.size
    pixels = np.array(image)
    unscrambled_pixels = np.zeros_like(pixels)
    
    section_width = width // grid_size
    section_height = height // grid_size

    for index, (i, j) in enumerate(pattern_key):
        src_x, src_y = (index % grid_size) * section_width, (index // grid_size) * section_height
        dest_x, dest_y = i * section_width, j * section_height
        unscrambled_pixels[dest_y:dest_y+section_height, dest_x:dest_x+section_width] = pixels[src_y:src_y+section_height, src_x:src_x+section_width]
    
    return Image.fromarray(unscrambled_pixels)


def decrypt_image(encrypted_image):
    pattern_key_str = encrypted_image.info.get("pattern_key")
    color_offset_str = encrypted_image.info.get("color_offset")

    if not pattern_key_str or not color_offset_str:
        st.error("Image metadata for decryption not found.")
        return None

    pattern_key = [(int(x.split(",")[0]), int(x.split(",")[1])) for x in pattern_key_str.split("_")]
    color_offset = tuple(map(int, color_offset_str.split(",")))

    decrypted_color_image = reverse_color_transform(encrypted_image, color_offset)
    decrypted_image = unscramble_image(decrypted_color_image, pattern_key, grid_size=8)
    
    decrypted_image_bytes = io.BytesIO()
    decrypted_image.save(decrypted_image_bytes, format="PNG")
    decrypted_image_bytes.seek(0)
    
    return decrypted_image, decrypted_image_bytes