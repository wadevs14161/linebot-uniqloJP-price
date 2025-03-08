import os

# Export keys to environment variables
LINE_CHANNEL_SECRET = ''
LINE_CHANNEL_ACCESS_TOKEN = ''
os.environ['LINE_CHANNEL_SECRET'] = LINE_CHANNEL_SECRET
os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = LINE_CHANNEL_ACCESS_TOKEN

# Start flask app in the background using cmd "nohup python app.py &"
os.system('nohup python app.py &')


