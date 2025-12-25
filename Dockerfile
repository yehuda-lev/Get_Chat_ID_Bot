FROM python:3.13-alpine
# Set the working directory
WORKDIR /get-chat-id-bot

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    python3-dev \
    libffi-dev

# Copy the current directory contents into the container at /get-chat-id-bot
COPY requirements.txt .

# Create a virtual environment
RUN python3 -m venv venv
RUN source venv/bin/activate

# Install the dependencies
RUN pip install -r requirements.txt
