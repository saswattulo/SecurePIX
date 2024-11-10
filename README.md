# SecurePIX

## Overview

SecurePIX is an image encryption and decryption tool that allows users to protect their images by applying a combination of color transformation and grid scrambling. The app uses simple algorithms to scramble image sections and apply a color offset to securely encrypt the image. It also allows the user to decrypt the image back to its original form using the pattern key and color offset embedded in the image's metadata.

## Features

- **Image Encryption**: Scrambles an image into a grid and applies a color transformation to secure it.
- **Image Decryption**: Reverts the encrypted image back to its original form using the metadata for color offset and scrambling pattern.
- **Metadata Storage**: Stores encryption details like the scrambling pattern and color offset within the image's metadata.
- **Download Options**: Easily download the encrypted or decrypted image after processing.

## How it Works

1. **Scrambling**: The image is divided into a grid of sections. Each section is scrambled using a random pattern key, which is saved for later decryption.
2. **Color Transformation**: The pixel values of the image are modified by adding a fixed color offset, and this offset is stored for decryption.
3. **Decryption**: The encrypted image is reversed by extracting the metadata (pattern key and color offset), undoing both the scrambling and color transformation to restore the original image.

## How to Use

1. Upload your image on the app.
2. Choose to encrypt or decrypt the image.
3. For encryption, you will receive a scrambled and color-transformed version of your image. 
4. For decryption, upload the encrypted image, and it will restore to the original image after applying the reverse operations.
5. Download the processed image directly.

## Installation

To run this project locally, follow these steps:

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/SecurePIX.git
    ```
2. Navigate into the project directory:
    ```bash
    cd SecurePIX
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the app:
    ```bash
    streamlit run app.py
    ```

## Technologies Used

- **Python**: For backend image processing and encryption/decryption algorithms.
- **Streamlit**: To create the interactive web interface.
- **Pillow**: For image handling (loading, saving, and processing).
- **Numpy**: For handling pixel-level operations and transformations.

## Contributing

Feel free to fork this repository and submit pull requests for bug fixes, features, or improvements. If you encounter any issues, please open an issue in the Issues section.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Thank you for checking out SecurePIX! If you enjoy the tool, feel free to buy me a coffee ☕ to support my work. Cheers!

