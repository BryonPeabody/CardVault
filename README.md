# CardVault

CardVault is a Django web application for tracking and valuing trading card collections.  
It pulls **card images and market prices from external APIs** and lets users manage their collection in one place.

## Features
- Add, edit, and remove cards from your collection
- Automatically fetch images and prices from APIs
- User authentication (login & registration)
- Data stored in a PostgreSQL database
- (Planned) Automated daily price updates
- (Planned) Historical price tracking and graphs
- (Planned) Smarter search (typo-tolerant lookup)

## Tech Stack
- Python / Django
- PostgreSQL
- Docker (development)
- Gunicorn (production server)
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
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Fill in .env with your own data

# You will need postgresql installed locally, if you have done this
createdb cardvault_db
# and update the .env with DATABASE_URL=postgres://<your-username>@localhost:5432/cardvault_db

python manage.py migrate
python manage.py runserver

# Run tests
pytest
```

## Running Docker (simple with local postgres)
```bash
docker build -t cardvault .
docker run -d -p 8000:8000 cardvault
```
Or full stack 
```bash
docker compose up --build
```
