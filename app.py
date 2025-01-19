import streamlit as st
import numpy as np
from PIL import Image, PngImagePlugin
import random
import io
import os

st.set_page_config(
    page_title="SecurePIX - Image Encryption and Decryption",
    page_icon="static/logo.svg",
    layout="centered",
)

# Add CSS to hide Streamlit's nav bar and footer
# Add CSS to hide Streamlit's nav bar, deploy button, and footer
# hide_streamlit_style = """
#     <style>
#     #MainMenu {visibility: hidden; display: none;} /* Hide the main menu (hamburger) */
#     footer {visibility: hidden; display: none;}    /* Hide the footer */
#     header {visibility: hidden; display: none;}    /* Hide the header with the deploy button */
#     </style>
# """
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden; display: none;}
    footer {visibility: hidden; display: none;}
    header {visibility: hidden; display: none;}
    
    /* Hide Streamlit Cloud badge and profile container */
    ._container_gzau3_1,
    ._viewerBadge_nim44_23,
    ._link_gzau3_10,
    ._profileContainer_gzau3_53,
    ._profilePreview_gzau3_63,
    ._profileImage_gzau3_78,
    [data-testid="appCreatorAvatar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        z-index: -1 !important;
    }
    
    /* Additional selectors to catch parent elements */
    a[href*="streamlit.io/cloud"],
    a[href*="share.streamlit.io/user"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Hide any SVG elements within these containers */
    ._container_gzau3_1 svg,
    ._link_gzau3_10 svg {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Remove any remaining space */
    .element-container:has(._container_gzau3_1),
    .element-container:has(._profileContainer_gzau3_53) {
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



# Add a logo at the top of the app
logo_path = "static/branding.svg"  # Replace this with the correct path to your logo
st.image(logo_path, width=200)


# Load the image
def load_image(path):
    return Image.open(path)


# Scramble the image
def scramble_image(image, grid_size):
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
        dest_x, dest_y = (index % grid_size) * section_width, (
            index // grid_size
        ) * section_height
        scrambled_pixels[
            dest_y : dest_y + section_height, dest_x : dest_x + section_width
        ] = pixels[src_y : src_y + section_height, src_x : src_x + section_width]

    return Image.fromarray(scrambled_pixels), pattern_key


# Color transformation
def color_transform(image, offset=(100, 50, 150)):
    pixels = np.array(image)
    transformed_pixels = (pixels + offset) % 256
    return Image.fromarray(transformed_pixels.astype(np.uint8)), offset


# Encrypt the image (scramble + color transform)
def encrypt_image(image, grid_size=16):
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
        src_x, src_y = (index % grid_size) * section_width, (
            index // grid_size
        ) * section_height
        dest_x, dest_y = i * section_width, j * section_height
        unscrambled_pixels[
            dest_y : dest_y + section_height, dest_x : dest_x + section_width
        ] = pixels[src_y : src_y + section_height, src_x : src_x + section_width]

    return Image.fromarray(unscrambled_pixels)


# Decrypt the image (reverse color transform + unscramble)
def decrypt_image(encrypted_image):
    pattern_key_str = encrypted_image.info.get("pattern_key")
    color_offset_str = encrypted_image.info.get("color_offset")

    if not pattern_key_str or not color_offset_str:
        st.error(
            "Image metadata for decryption not found. Please ensure the image is properly encrypted."
        )
        return None, None  # Return a tuple of None values

    pattern_key = [
        (int(x.split(",")[0]), int(x.split(",")[1])) for x in pattern_key_str.split("_")
    ]
    color_offset = tuple(map(int, color_offset_str.split(",")))

    decrypted_color_image = reverse_color_transform(encrypted_image, color_offset)
    decrypted_image = unscramble_image(decrypted_color_image, pattern_key, grid_size=16)

    decrypted_image_bytes = io.BytesIO()
    decrypted_image.save(decrypted_image_bytes, format="PNG")
    decrypted_image_bytes.seek(0)

    return decrypted_image, decrypted_image_bytes


# Layout for encryption and decryption side by side with spacing
col1, _, col2 = st.columns([1, 0.5, 1])  # Two columns with equal width

# Encryption Section
with col1:
    st.header("🔒 Encrypt an Image")
    uploaded_image = st.file_uploader(
        "Upload an image to encrypt", type=["png", "jpg", "jpeg"], key="encrypt"
    )

    if uploaded_image:
        image = load_image(uploaded_image)
        st.image(image, caption="Original Image", use_container_width=True)
        original_name = os.path.splitext(uploaded_image.name)[0]

        if st.button("Encrypt Image"):
            encrypted_image_bytes = encrypt_image(image)
            st.success("Image encrypted successfully.")

            download_button = st.download_button(
                "Download Encrypted Image",
                data=encrypted_image_bytes,
                file_name=f"encrypted_{original_name}.png",
                mime="image/png",
            )

            # Clear encrypted image bytes from memory after download
            if download_button:
                encrypted_image_bytes = None
                st.info("Encrypted image closed from memory after download.")

# Decryption Section
# Handle Image Decryption
with col2:
    st.header("🔓 Decrypt an Image")
    encrypted_image_file = st.file_uploader(
        "Upload an encrypted image to decrypt",
        type=["png", "jpg", "jpeg"],
        key="decrypt",
    )

    if encrypted_image_file:
        encrypted_image = Image.open(encrypted_image_file)
        st.image(encrypted_image, caption="Encrypted Image", use_container_width=True)
        original_name = os.path.splitext(
            encrypted_image_file.name.replace("encrypted_", "")
        )[0]

        if st.button("Decrypt Image"):
            decrypted_image, decrypted_image_bytes = decrypt_image(encrypted_image)

            # Simulate a popup using expander
            if decrypted_image is None or decrypted_image_bytes is None:
                with st.expander(
                    "❌ Decryption Failed - Metadata Not Found", expanded=True
                ):
                    st.error(
                        "Image metadata for decryption not found. Please ensure the image is properly encrypted."
                    )
            else:
                st.image(
                    decrypted_image, caption="Decrypted Image", use_container_width=True
                )

                # Decrypt download button
                decrypt_download_button = st.download_button(
                    "Download Decrypted Image",
                    data=decrypted_image_bytes,
                    file_name=f"decrypted_{original_name}.png",
                    mime="image/png",
                )

                # Clear decrypted image bytes from memory after download
                if decrypt_download_button:
                    decrypted_image_bytes = None
                    st.info("Decrypted image closed from memory after download.")
