"""
SQLite connection and helpers for the companies table (contact information only).
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "indigonode.db"


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the companies table if it does not exist. Schema: contact info only."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            description TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            contact_address TEXT,
            has_contact_form TEXT,
            source_url TEXT,
            scraped_at TIMESTAMP
        )
    """)
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN has_contact_form TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def insert_company(company_name: str, description: str, contact_email: str, contact_phone: str,
                   contact_address: str, has_contact_form: str, source_url: str) -> None:
    """Insert one company record (contact information)."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO companies (company_name, description, contact_email, contact_phone, contact_address, has_contact_form, source_url, scraped_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (company_name, description or "", contact_email or "", contact_phone or "", contact_address or "",
         has_contact_form or "No", source_url, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def delete_company(company_id: int) -> None:
    """Delete one company record by id."""
    conn = get_connection()
    conn.execute("DELETE FROM companies WHERE id = ?", (company_id,))
    conn.commit()
    conn.close()


def get_all_companies() -> pd.DataFrame | None:
    """Return all companies as a DataFrame."""
    init_db()
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM companies ORDER BY scraped_at DESC", conn)
        return df
    except Exception:
        return None
    finally:
        conn.close()
