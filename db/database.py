"""
SQLite connection and helpers for the companies table.
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
    """Create the companies table if it does not exist. Add description column if missing."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            description TEXT,
            referral_program TEXT,
            referral_payout TEXT,
            outsourcing_type TEXT,
            source_url TEXT,
            scraped_at TIMESTAMP
        )
    """)
    # Migration: add description column for existing DBs
    try:
        conn.execute("ALTER TABLE companies ADD COLUMN description TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()


def insert_company(company_name: str, description: str, referral_program: str, referral_payout: str,
                   outsourcing_type: str, source_url: str) -> None:
    """Insert one company record."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO companies (company_name, description, referral_program, referral_payout, outsourcing_type, source_url, scraped_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (company_name, description or "", referral_program, referral_payout, outsourcing_type, source_url, datetime.utcnow().isoformat()),
    )
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
