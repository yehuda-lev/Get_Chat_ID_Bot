FROM python:3.12-alpine
# Set the working directory
WORKDIR /get-chat-id-bot

# Copy the current directory contents into the container at /get-chat-id-bot
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt
