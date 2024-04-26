import requests
import shutil
import cloudinary

def upload_image(channel_access_token, messageId):
    url = "https://api-data.line.me/v2/bot/message/{}/content".format(messageId)
    headers = {"Authorization": "Bearer {}".format(channel_access_token)}
    r = requests.get(url, headers=headers, stream=True)
    
    filename = "test.jpg"
    if r.status_code == 200:
        with open(f'{filename}', "wb") as file:
            shutil.copyfileobj(r.raw, file)
            print("Image downloaded successfully.")

    cloudinary_response = cloudinary.uploader.upload('test.jpg')
    print("Uploading image... ")

    return cloudinary_response['url']
