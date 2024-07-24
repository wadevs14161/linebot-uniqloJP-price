import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

# Azure service is not available, 23/07/2024
# Set the values of your computer vision endpoint and computer vision key
# as environment variables:
def analyze(url):
    try:
        endpoint = os.environ["VISION_ENDPOINT"]
        key = os.environ["VISION_KEY"]
    except KeyError:
        print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Image Analysis client
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )
    if url:
        image_url = url
    else:
        image_url = "https://i.imgur.com/HLw9BhO.jpg"
    # Get a caption for the image. This will be a synchronously (blocking) call.
    result = client.analyze_from_url(
        image_url=image_url,
        visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
        gender_neutral_caption=True,  # Optional (default is False)
    )

    return result