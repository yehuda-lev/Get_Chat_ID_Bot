FROM python:3.12-alpine
# Set the working directory
WORKDIR /get-chat-id-bot

# Copy the current directory contents into the container at /get-chat-id-bot
COPY requirements.txt .

# Create a virtual environment
RUN python3 -m venv venv
RUN source venv/bin/activate

# Install the dependencies
RUN pip install -r requirements.txt
