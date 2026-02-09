"""
Database page: View & query SQLite data.
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import get_connection, get_all_companies, init_db, delete_company

st.set_page_config(page_title="Database", page_icon="🗄️")
st.title("Database")

init_db()

df = get_all_companies()
if df is not None and not df.empty:
    # Filter at the top
    st.subheader("Filter")
    col1, col2 = st.columns(2)
    with col1:
        company_filter = st.text_input("Company name contains", placeholder="e.g. Acme")
    with col2:
        email_filter = st.text_input("Email contains", placeholder="e.g. @company.com")

    if company_filter or email_filter:
        conn = get_connection()
        query = "SELECT * FROM companies WHERE 1=1"
        params = []
        if company_filter:
            query += " AND company_name LIKE ?"
            params.append(f"%{company_filter}%")
        if email_filter:
            query += " AND contact_email LIKE ?"
            params.append(f"%{email_filter}%")
        query += " ORDER BY scraped_at DESC"
        filtered = conn.execute(query, params).fetchall()
        conn.close()
        if filtered:
            import pandas as pd
            display_df = pd.DataFrame([dict(r) for r in filtered])
            st.dataframe(display_df, use_container_width=True)
            rows_for_delete = list(filtered)
        else:
            st.info("No matches.")
            rows_for_delete = []
    else:
        st.dataframe(df, use_container_width=True)
        rows_for_delete = df.to_dict("records") if "id" in df.columns else []

    # Delete rows section
    if rows_for_delete:
        st.subheader("Delete rows")
        options = {f"ID {r.get('id')} — {r.get('company_name', '?')}": r["id"] for r in rows_for_delete if r.get("id") is not None}
        if options:
            to_delete = st.multiselect("Select rows to delete", options=list(options.keys()), key="delete_multiselect")
            if st.button("Delete selected"):
                ids = [options[k] for k in to_delete]
                for i in ids:
                    delete_company(i)
                st.success(f"Deleted {len(ids)} row(s).")
                st.rerun()
else:
    st.info("No data yet. Scrape URLs from the Home page to populate contact data.")
