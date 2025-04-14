FROM python:3.11-alpine

WORKDIR /PERCEPTRONX

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (using Alpine packages)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    pkgconf

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for file uploads if they don't exist
RUN mkdir -p /app/Frontend_Web/static/assets/images/user

# Make sure the directory is writable
RUN chmod -R 777 /app/Frontend_Web/static/assets/images/user

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]