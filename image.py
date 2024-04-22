import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

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
        image_url = "https://www.visa.com.tw/dam/VCOM/regional/ap/taiwan/global-elements/images/tw-visa-gold-card-498x280.png"
    # Get a caption for the image. This will be a synchronously (blocking) call.
    result = client.analyze_from_url(
        image_url=image_url,
        visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
        gender_neutral_caption=True,  # Optional (default is False)
    )

    # print("Image analysis results:")
    # # Print caption results to the console
    # print(" Caption:")
    # if result.caption is not None:
    #     print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

    # # Print text (OCR) analysis results to the console
    # print(" Read:")
    # if result.read is not None:
    #     for line in result.read.blocks[0].lines:
    #         print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
    #         for word in line.words:
    #             print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")

    return result