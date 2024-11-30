# utiles.py 
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

def upload_compressed_image(image_file):
    """
    Compress the image, upload it to Cloudinary, and return the URLs for
    both the compressed and uncompressed versions.
    """
    try:
        # Upload image with compression
        upload_response = cloudinary.uploader.upload(
            image_file,
            folder="compressed_images/",
            quality="auto:low",  # Automatically optimize quality
            format="jpg"         # Convert to JPEG for better compression
        )

        # Get the public ID of the uploaded image
        public_id = upload_response['public_id']

        # Generate URL for the uncompressed image
        uncompressed_url, _ = cloudinary_url(public_id, secure=True)

        # Generate URL for the compressed image (transformation)
        compressed_url, _ = cloudinary_url(public_id, quality="auto:low", secure=True)

        return {
            "compressed_url": compressed_url,
            "uncompressed_url": uncompressed_url,
        }

    except Exception as e:
        raise ValueError(f"Image upload failed: {str(e)}")
