# IndigoNode_WS – Requirements Document

## 1. Objective

Build a **local** Python application using Streamlit as the UI. The app will:

- Scrape company websites to identify **referral programs for outsourcing**
- Validate the scraped data before saving
- Store results in a **SQLite** database
- Let users explore and analyze the collected information

---

## 2. Tech Stack

| Component      | Technology        |
|----------------|-------------------|
| Language       | Python 3.x        |
| UI             | Streamlit         |
| Web scraping   | BeautifulSoup     |
| HTTP requests  | requests          |
| Database       | SQLite (local)    |

---

## 3. Project Structure

```
Home.py                    → URL input + scraping
pages/
  Database.py              → View & query SQLite data
  Dashboard.py             → Data visualization
functions/
  scraper.py               → Web scraping logic
db/
  database.py              → SQLite connection & helpers
  indigonode.db            → SQLite database file (created on first run)
requirements.txt
README.md
REQUIREMENTS.md            → This document
```

---

## 4. Page Requirements

### 4.1 Home Page

- **URL input** – Single input field for the URL to scrape.
- **Scrape action** – Button to start web scraping.
- **Scraping** – Use BeautifulSoup to scrape the page.
- **Extracted data** (structured):
  - Company name
  - Referral program existence (Yes/No)
  - Referral payout (if available)
  - Outsourcing type or keywords
  - Source URL
- **Preview** – Display scraped data in a readable format below the form.
- **Save to Database** – Button to persist data.
- **Confirmation** – Save to SQLite **only after** user confirms (e.g. after reviewing the preview).

### 4.2 Database Page

- **Connection** – Connect to the project SQLite database.
- **Table view** – Display all stored records in a table.
- **Filtering** – Allow simple filtering/querying (e.g. by company name or payout), **without** raw SQL input from users.

### 4.3 Dashboard Page

- **Data source** – Read from the same SQLite database.
- **Insights** – Use Streamlit charts and metrics, including:
  - Total number of companies scraped
  - Distribution of referral payouts
  - Referral programs by category or keyword
- **Design** – Prefer clarity over complexity.

---

## 5. Database Schema

**Table: `companies`**

| Column            | Type      | Description                    |
|-------------------|-----------|--------------------------------|
| id                | INTEGER   | Primary key, auto-increment    |
| company_name      | TEXT      | Company name                   |
| referral_program  | TEXT      | e.g. "Yes" / "No"             |
| referral_payout   | TEXT      | Payout if available            |
| outsourcing_type  | TEXT      | Type or keywords               |
| source_url        | TEXT      | Scraped URL                    |
| scraped_at        | TIMESTAMP | When the record was scraped    |

---

## 6. Implementation Guidelines

- **Modularity** – Keep code modular and readable; separate UI, scraping, and database logic.
- **Error handling** – Handle at least:
  - Invalid URL
  - Failed HTTP requests
  - Missing or incomplete data
- **Scope** – Application is fully local; no over-engineering of authentication or deployment.

---

## 7. Goal

- Deliver a **functional MVP**.
- Keep the system **easy to extend** later with better scraping logic, automation, or AI-based classification.
