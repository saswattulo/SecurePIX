import streamlit as st
import numpy as np
from PIL import Image, PngImagePlugin
import random
import io
import os
from functions.encryption import color_transform, scramble_image, encrypt_image
from functions.decryption import reverse_color_transform, unscramble_image, decrypt_image

# Load the image
def load_image(path):
    return Image.open(path)


# # Streamlit app layout
# st.title("SecurePIX")

# Add a logo at the top of the app
logo_path = "logo.svg"  # Replace this with the correct path to your logo
st.image(logo_path, width=200)

# st.markdown(
#     "This application provides a secure way to encrypt and decrypt images using a grid-based scrambling method and color transformations. "
#     "Upload an image to encrypt, then download the encrypted image with embedded metadata for decryption."
# )

# Layout for encryption and decryption side by side with spacing
col1, _, col2 = st.columns([1, 0.5, 1])  # Two columns with equal width

# Encryption Section
with col1:
    st.header("🔒 Encrypt an Image")
    uploaded_image = st.file_uploader("Upload an image to encrypt", type=["png", "jpg", "jpeg"], key="encrypt")

    if uploaded_image:
        image = load_image(uploaded_image)
        st.image(image, caption="Original Image", use_container_width=True)  # Use use_container_width instead of use_column_width
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
        st.image(encrypted_image, caption="Encrypted Image", use_container_width=True)  # Use use_container_width instead of use_column_width
        original_name = os.path.splitext(encrypted_image_file.name.replace("encrypted_", ""))[0]

        if st.button("Decrypt Image"):
            decrypted_image, decrypted_image_bytes = decrypt_image(encrypted_image)
            if decrypted_image:
                st.image(decrypted_image, caption="Decrypted Image", use_container_width=True)  # Use use_container_width instead of use_column_width

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
