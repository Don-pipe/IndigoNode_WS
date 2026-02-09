"""
Dashboard page: Data visualization and insights.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import get_all_companies, init_db

st.set_page_config(page_title="Dashboard", page_icon="📊")
st.title("Dashboard")

init_db()
df = get_all_companies()

if df is not None and not df.empty:
    # Total companies
    st.metric("Total companies", len(df))

    # Payout distribution (if we have payout data)
    if "referral_payout" in df.columns and df["referral_payout"].notna().any():
        payouts = df["referral_payout"].dropna()
        if len(payouts) > 0:
            st.subheader("Referral payouts (sample)")
            st.bar_chart(payouts.value_counts().head(15))

    # Referral program yes/no
    if "referral_program" in df.columns:
        st.subheader("Referral program")
        st.bar_chart(df["referral_program"].value_counts())
else:
    st.info("No data yet. Scrape URLs from the Home page to see the dashboard.")
