# Run the following command to set the environment variables
# $ source myscript.sh
export LINE_CHANNEL_SECRET=""
export LINE_CHANNEL_ACCESS_TOKEN=""
echo $LINE_CHANNEL_SECRET
echo $LINE_CHANNEL_ACCESS_TOKEN

# Load Virtual environment
source venv/bin/activate

# Start flask app in the background using cmd "nohup python app.py &"
nohup python app.py &