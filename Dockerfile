FROM python:3.11-slim

WORKDIR /PERCEPTRONX

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (including libraries needed for image processing)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libffi-dev \
    libssl-dev \
    libc-dev \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY Backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY Backend /PERCEPTRONX/Backend
COPY Frontend_Web /PERCEPTRONX/Frontend_Web
COPY Frontend /PERCEPTRONX/Frontend
COPY docker-compose.yml .
COPY init.sql .

# Make sure that static images are copied to the correct directory
COPY Frontend_Web/static/assets/images/user/ /PERCEPTRONX/Frontend_Web/static/assets/images/user/

# Set permissions (if necessary, ensure images are writable)
RUN chmod -R 777 /PERCEPTRONX/Frontend_Web/static/assets/images/user

# Expose the static directory as a volume for persistence (optional)
VOLUME ["/PERCEPTRONX/Frontend_Web/static"]

# Set the working directory for FastAPI
WORKDIR /PERCEPTRONX/Backend

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
