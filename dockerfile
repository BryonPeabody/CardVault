# Use official Python slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
WORKDIR /app/CardVault

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the CardVault project
RUN git clone https://github.com/BryonPeabody/CardVault.git .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose default Django port
EXPOSE 8000

# Default command: migrate DB and run server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# Install Python dependencies
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

# Expose default Django port
EXPOSE 8000

# Default command: collect static files, migrate DB, run server
CMD ["sh", "-c", "python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000"]