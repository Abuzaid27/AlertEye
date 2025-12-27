# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# cmake & build-essential -> for dlib
# libgl1 & libglib2.0-0 -> for opencv-python-headless
# libasound2-dev -> for simpleaudio support
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
