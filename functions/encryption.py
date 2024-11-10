import streamlit as st
import numpy as np
from PIL import Image, PngImagePlugin
import random
import io
import os


def scramble_image(image, grid_size=8):
    width, height = image.size
    pixels = np.array(image)
    scrambled_pixels = np.zeros_like(pixels)

    section_width = width // grid_size
    section_height = height // grid_size

    indices = [(i, j) for i in range(grid_size) for j in range(grid_size)]
    random.shuffle(indices)
    pattern_key = indices[:]

    for index, (i, j) in enumerate(indices):
        src_x, src_y = i * section_width, j * section_height
        dest_x, dest_y = (index % grid_size) * section_width, (index // grid_size) * section_height
        scrambled_pixels[dest_y:dest_y+section_height, dest_x:dest_x+section_width] = pixels[src_y:src_y+section_height, src_x:src_x+section_width]

    return Image.fromarray(scrambled_pixels), pattern_key


def color_transform(image, offset=(100, 50, 150)):
    pixels = np.array(image)
    transformed_pixels = (pixels + offset) % 256
    return Image.fromarray(transformed_pixels.astype(np.uint8)), offset

# Encrypt the image (scramble + color transform)
def encrypt_image(image, grid_size=8):
    scrambled_image, pattern_key = scramble_image(image, grid_size)
    encrypted_image, color_offset = color_transform(scrambled_image)

    pattern_key_str = "_".join([f"{x},{y}" for x, y in pattern_key])
    color_offset_str = ",".join(map(str, color_offset))

    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("pattern_key", pattern_key_str)
    metadata.add_text("color_offset", color_offset_str)

    encrypted_image_bytes = io.BytesIO()
    encrypted_image.save(encrypted_image_bytes, format="PNG", pnginfo=metadata)
    encrypted_image_bytes.seek(0)
    return encrypted_image_bytes