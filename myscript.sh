# Run the following command to set the environment variables
# $ source myscript.sh
export LINE_CHANNEL_SECRET="37d24f448086640d7824cb363f5fd1c1"
export LINE_CHANNEL_ACCESS_TOKEN="oGbZ9+xp5AK2S9A1jG7nzUpiH13skFHh1pBlJ2A0oLpu5wIQhQdMmj4tbqC/+2F/kkw5T+12bUSQONaPzcWeC3VCzPQYSpQC9SoNv2lkqGzSr1IHySlWnMogK7rBs9ClkX07RoAkvH6nZ0FbodlSLgdB04t89/1O/w1cDnyilFU="
echo $LINE_CHANNEL_SECRET
echo $LINE_CHANNEL_ACCESS_TOKEN

# Load Virtual environment
source .venv/bin/activate

# Start flask app in the background using cmd "nohup python app.py &"
nohup python app.py &