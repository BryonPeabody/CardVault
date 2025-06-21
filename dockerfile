# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory inside the container
WORKDIR /CardVault

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pip + Python deps
COPY requirements.txt /CardVault/
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy project files
COPY . /CardVault

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000 for the dev server
EXPOSE 8000

# Default command
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
