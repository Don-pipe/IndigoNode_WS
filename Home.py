"""
Home page: URL input and web scraping. Save to SQLite after confirmation.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from functions.scraper import scrape_url
from db.database import init_db, insert_company

st.set_page_config(page_title="IndigoNode", page_icon="🏠")
st.title("IndigoNode – Web Scraping")

init_db()

url = st.text_input("URL to scrape", placeholder="https://example.com/referral-program")

if st.button("Scrape URL"):
    if not url or not url.strip():
        st.error("Please enter a valid URL.")
    else:
        try:
            data = scrape_url(url.strip())
            st.session_state["last_scraped"] = data
            st.success("Scraping finished. Review the data below.")
        except ValueError as e:
            st.error(str(e))

if "last_scraped" in st.session_state:
    data = st.session_state["last_scraped"]
    st.subheader("Scraped data")
    st.json(data)

    if st.button("Save to Database"):
        insert_company(
            company_name=data["company_name"],
            referral_program=data["referral_program"],
            referral_payout=data["referral_payout"],
            outsourcing_type=data["outsourcing_type"],
            source_url=data["source_url"],
        )
        st.success("Saved to database.")
        del st.session_state["last_scraped"]
