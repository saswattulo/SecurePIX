import streamlit as st
import numpy as np
from PIL import Image, PngImagePlugin
import random
import io
import os

# Load the image
def load_image(path):
    return Image.open(path)

# Scramble the image
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

# Color transformation
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

# Decrypt the image (reverse color transform + unscramble)
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

# Streamlit app layout
st.title("Secure Image Encryption & Decryption System")

st.markdown(
    "This application provides a secure way to encrypt and decrypt images using a grid-based scrambling method and color transformations. "
    "Upload an image to encrypt, then download the encrypted image with embedded metadata for decryption."
)

# Layout for encryption and decryption side by side with spacing
col1,_,col2 = st.columns([1,0.5,1])  # Two columns with equal width

# Encryption Section
with col1:
    st.header("🔒 Encrypt an Image")
    uploaded_image = st.file_uploader("Upload an image to encrypt", type=["png", "jpg", "jpeg"], key="encrypt")

    if uploaded_image:
        image = load_image(uploaded_image)
        st.image(image, caption="Original Image", use_column_width=True)
        original_name = os.path.splitext(uploaded_image.name)[0]

        if st.button("Encrypt Image"):
            encrypted_image_bytes = encrypt_image(image)
            st.success("Image encrypted successfully.")

            download_button = st.download_button(
                "Download Encrypted Image",
                data=encrypted_image_bytes,
                file_name=f"encrypted_{original_name}.png",
                mime="image/png"
            )

            # Clear encrypted image bytes from memory after download
            if download_button:
                encrypted_image_bytes = None
                st.info("Encrypted image closed from memory after download.")

# Decryption Section
with col2:
    st.header("🔓 Decrypt an Image")
    encrypted_image_file = st.file_uploader("Upload an encrypted image to decrypt", type=["png"], key="decrypt")

    if encrypted_image_file:
        encrypted_image = load_image(encrypted_image_file)
        st.image(encrypted_image, caption="Encrypted Image", use_column_width=True)
        original_name = os.path.splitext(encrypted_image_file.name.replace("encrypted_", ""))[0]

        if st.button("Decrypt Image"):
            decrypted_image, decrypted_image_bytes = decrypt_image(encrypted_image)
            if decrypted_image:
                st.image(decrypted_image, caption="Decrypted Image", use_column_width=True)

                # Download button for decrypted image
                decrypt_download_button = st.download_button(
                    "Download Decrypted Image",
                    data=decrypted_image_bytes,
                    file_name=f"decrypted_{original_name}.png",
                    mime="image/png"
                )

                # Clear decrypted image bytes from memory after download
                if decrypt_download_button:
                    decrypted_image_bytes = None
                    st.info("Decrypted image closed from memory after download.")

