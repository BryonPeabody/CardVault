# CardVault


CardVault is a Django web application for tracking and valuing trading card collections.  
It pulls **card images and market prices from external APIs** and lets users manage their collection in one place.

## Features
- Add, edit, and delete cards in a personal collection
- Automatically fetch images and prices from APIs on card creation and price refresh
- Store historical price snapshots per card
- Aggregate and graph total collection value over time
- Manual price refresh with idempotent update logic
- User authentication (login & registration)
- PostgrSQL-backed data storage


## Tech Stack
- Python / Django
- PostgreSQL
- Docker (development)
- Gunicorn (production server)
- External APIs for images and price data

## Current Status
Core is functionally complete. The application is stable and fully tested

## Planned improvements
- Automated daily price updates (scheduled job)
- Minor UI/CSS polish
- Password reset / recovery
- Expanded card set support

## Design Notes
- Historical pricing is stored using a separate snapshot model to avoid data drift.
- Current card value is denormalized for fast list and aggregation queries.
- Business logic is handled in a service layer to keep views thin and testable.


## Running Locally
Clone the repository, set up a virtual environment, configure environment variables, and start the development server:

```bash
git clone https://github.com/yourusername/cardvault.git
cd cardvault

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in required values in .env (API keys, DATABASE_URL, etc.)

# Create a local PostgreSQL database and update DATABASE_URL in .env:
createdb cardvault_db
# Example:
# DATABASE_URL=postgres://<username>@localhost:5432/cardvault_db

python manage.py migrate
python manage.py runserver

# Run tests
pytest
```

## Running Docker 
## App container only (expects external Postgres)
```bash
docker build -t cardvault .
docker run -d -p 8000:8000 cardvault
```
## Full stack (recommended)
```bash
docker compose up --build
```

