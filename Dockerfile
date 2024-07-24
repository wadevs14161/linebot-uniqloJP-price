# Dockerize a django app with python 3.12.1
# Start from the official Python image
FROM python:3.12.1-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LINE_CHANNEL_SECRET 37d24f448086640d7824cb363f5fd1c1
ENV LINE_CHANNEL_ACCESS_TOKEN oGbZ9+xp5AK2S9A1jG7nzUpiH13skFHh1pBlJ2A0oLpu5wIQhQdMmj4tbqC/+2F/kkw5T+12bUSQONaPzcWeC3VCzPQYSpQC9SoNv2lkqGzSr1IHySlWnMogK7rBs9ClkX07RoAkvH6nZ0FbodlSLgdB04t89/1O/w1cDnyilFU=

# Set work directory
WORKDIR /app

# Copy project
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Run server 
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]