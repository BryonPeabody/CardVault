# Use Ubuntu as base image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python and required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/CardVault

# Clone the CardVault project
RUN git clone https://github.com/BryonPeabody/CardVault.git .

# Install Python dependencies
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

# Expose default Django port
EXPOSE 8000

# Default command: collect static files, migrate DB, run server
CMD ["sh", "-c", "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]