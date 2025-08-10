import os

# The URL for the image retriever service, loaded from environment variables.
IMAGE_RETRIEVER_URL = os.getenv("IMAGE_RETRIEVER_URL", "http://ms-image-retriever:8000")

def get_image_url(type: str, item_id: str) -> str:
    """
    Constructs a direct URL to the image retriever service.
    """
    return f"{IMAGE_RETRIEVER_URL}/images/{type}/{item_id}"
