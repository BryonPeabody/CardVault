# CardVault

CardVault is a Django web application for tracking and valuing trading card collections.  
It pulls **card images and market prices from external APIs** and lets users manage their collection in one place.

## Features
- Add, edit, and remove cards from your collection
- Automatically fetch images and prices from APIs
- User authentication (login & registration)
- Data stored in a PostgreSQL database

## Tech Stack
- Python / Django
- PostgreSQL
- Docker (development)
- External APIs for images and price data

## Current Status
This project is actively being developed.  
Planned improvements:
- Automated daily price updates
- Historical price tracking and graphs
- Better search (e.g., typo‑tolerant lookup)
- Additional testing

## Running Locally
Clone the repo, install requirements, run migrations, then start the dev server:

```bash
git clone https://github.com/yourusername/cardvault.git
cd cardvault
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver



Running Docker
docker build -t cardvault .
docker run -d -p 8000:8000 cardvault
