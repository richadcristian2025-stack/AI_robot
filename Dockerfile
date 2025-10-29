# Use Python 3.10 with Node.js for frontend
FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libasound2-dev \
    alsa-utils \
    libportaudio2 \
    libportaudiocpp0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm

# Create app directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Change to frontend directory
WORKDIR /app/robot-ai-dashboard

# Install frontend dependencies
RUN npm install

# Build the frontend
RUN npm run build

# Go back to app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p static templates

# Copy built frontend to static files
RUN cp -r robot-ai-dashboard/dist/* static/

# Expose the port the app runs on
EXPOSE 4141

# Set the working directory to the app root
WORKDIR /app

# Command to run the application
CMD ["python", "web_interface.py"]
