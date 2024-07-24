# Dockerize a django app with python 3.12.1
# Start from the official Python image
FROM python:3.12.1-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV LINE_CHANNEL_SECRET 2d89a411a7883fc61c412547c56e3d69
ENV LINE_CHANNEL_ACCESS_TOKEN IaJib8xyDo+YRBjWLNBEJItkTQ9gNkRIkSwuRaOPhtgMYoAPKeUQYOzRzAWYdEndowSIZM5vk2MKaA2F1sDfJcGr2gGnzUepWr4SKcxlGBxpqqo4XnAlRREK1qi+WfEdF6xJ3kgMfBTEx05miZeIBgdB04t89/1O/w1cDnyilFU=

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