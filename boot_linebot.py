import os

# Check if venv is already exist
if not os.path.isdir('venv'):
    print('Creating virtual environment...')
    # Create virtual environment
    os.system('python3 -m venv venv')

    # Time out for 30 seconds
    print('Waiting for 30 seconds...')
    os.system('sleep 30')

# Activate virtual environment
print('Activating virtual environment...')
os.system('source venv/bin/activate')

# Run pip install -r requirements.txt
print('Installing requirements...')
os.system('pip3 install -r requirements.txt')

# Time out for 45 seconds
print('Waiting for 45 seconds...')
os.system('sleep 45')

# Export keys to environment variables
LINE_CHANNEL_SECRET = ''
LINE_CHANNEL_ACCESS_TOKEN = ''
os.environ['LINE_CHANNEL_SECRET'] = LINE_CHANNEL_SECRET
os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = LINE_CHANNEL_ACCESS_TOKEN

# Start flask app in the background using cmd "nohup python app.py &"
os.system('nohup python app.py &')


