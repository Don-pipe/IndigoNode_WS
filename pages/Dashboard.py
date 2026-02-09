"""
Dashboard page: Contact data overview.
"""
import streamlit as st
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import get_all_companies, init_db

st.set_page_config(page_title="Dashboard", page_icon="📊")
st.title("Dashboard")

init_db()
df = get_all_companies()

if df is not None and not df.empty:
    st.metric("Total companies", len(df))

    col1, col2, col3 = st.columns(3)
    with col1:
        with_email = (df["contact_email"].fillna("").astype(str).str.strip() != "").sum() if "contact_email" in df.columns else 0
        st.metric("With email", int(with_email))
    with col2:
        with_phone = (df["contact_phone"].fillna("").astype(str).str.strip() != "").sum() if "contact_phone" in df.columns else 0
        st.metric("With phone", int(with_phone))
    with col3:
        with_address = (df["contact_address"].fillna("").astype(str).str.strip() != "").sum() if "contact_address" in df.columns else 0
        st.metric("With address", int(with_address))
else:
    st.info("No data yet. Scrape URLs from the Home page to see the dashboard.")
