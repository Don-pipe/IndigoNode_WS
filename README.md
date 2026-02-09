# IndigoNode_WS

Local Streamlit app to scrape company pages for referral/outsourcing info, store results in SQLite, and explore them in Database and Dashboard pages.

## Project structure

- **Home.py** – URL input and scraping; save to DB after confirmation
- **pages/**
  - **Database.py** – View and query SQLite data
  - **Dashboard.py** – Data visualization
- **functions/**
  - **scraper.py** – Web scraping logic (BeautifulSoup)
- **db/**
  - **database.py** – SQLite connection and helpers
  - **indigonode.db** – SQLite database (created on first run)

## Setup

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## Usage

1. **Home** – Paste a URL, click “Scrape URL”, review the data, then “Save to Database” if correct.
2. **Database** – Browse and filter stored companies (no raw SQL).
3. **Dashboard** – See counts and simple charts from the scraped data.
