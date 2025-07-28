# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .


# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the main Python script
CMD ["python", "main.py"]
