# Library requirements (requirements.txt)

Install all dependencies:

```bash
pip install -r requirements.txt
```

## Packages

| Package     | Version   | Purpose |
|------------|-----------|---------|
| **streamlit** | ≥1.28.0 | Web UI for the app (Home, Database, Dashboard pages). |
| **beautifulsoup4** | ≥4.12.0 | HTML parsing for web scraping. |
| **requests**  | ≥2.31.0 | HTTP requests to fetch web pages before scraping. |
| **pandas**    | ≥2.0.0  | DataFrames for displaying and querying table data (Database/Dashboard). |

## Optional (included with Streamlit)

- **sqlite3** – Built into Python; used in `db/database.py` for the SQLite database.
