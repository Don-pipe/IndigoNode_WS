"""
Database page: View & query SQLite data.
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import get_connection, get_all_companies, init_db

st.set_page_config(page_title="Database", page_icon="🗄️")
st.title("Database")

init_db()

# Display all records
df = get_all_companies()
if df is not None and not df.empty:
    st.dataframe(df, use_container_width=True)

    # Simple filters (no raw SQL)
    st.subheader("Filter")
    col1, col2 = st.columns(2)
    with col1:
        company_filter = st.text_input("Company name contains", placeholder="e.g. Acme")
    with col2:
        payout_filter = st.text_input("Payout contains", placeholder="e.g. $500")

    if company_filter or payout_filter:
        conn = get_connection()
        query = "SELECT * FROM companies WHERE 1=1"
        params = []
        if company_filter:
            query += " AND company_name LIKE ?"
            params.append(f"%{company_filter}%")
        if payout_filter:
            query += " AND referral_payout LIKE ?"
            params.append(f"%{payout_filter}%")
        query += " ORDER BY scraped_at DESC"
        filtered = conn.execute(query, params).fetchall()
        conn.close()
        if filtered:
            import pandas as pd
            cols = ["id", "company_name", "referral_program", "referral_payout", "outsourcing_type", "source_url", "scraped_at"]
            st.dataframe(pd.DataFrame(filtered, columns=cols), use_container_width=True)
        else:
            st.info("No matches.")
else:
    st.info("No data yet. Scrape URLs from the Home page to populate the database.")
