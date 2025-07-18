# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system packages for audio and webrtcvad
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    python3-dev \
    libsndfile1 \
    libasound2-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port (same as FastAPI default)
EXPOSE 8000

# Start the FastAPI app
CMD ["python", "main.py"]
