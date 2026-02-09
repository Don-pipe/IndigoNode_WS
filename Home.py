"""
Home page: URL input and web scraping. Save to SQLite after confirmation.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from functions.scraper import scrape_url, discover_site_urls, scrape_urls
from db.database import init_db, insert_company

st.set_page_config(page_title="IndigoNode", page_icon="🏠")
st.title("IndigoNode – Web Scraping")

init_db()

url = st.text_input("URL", placeholder="https://example.com or https://example.com/page")

mode = st.radio("Mode", ["Single page only", "Discover & choose pages", "Manual entry"], horizontal=True)
max_pages = 50
if "Discover" in mode:
    max_pages = st.number_input("Max pages to discover", min_value=5, max_value=150, value=50, step=5)

if "Discover" in mode:
    if st.button("Discover pages"):
        if not url or not url.strip():
            st.error("Please enter a valid URL.")
        else:
            try:
                with st.spinner("Discovering pages on this site…"):
                    discovered = discover_site_urls(url.strip(), max_pages=max_pages)
                st.session_state["discovered_urls"] = discovered
                st.success(f"Found {len(discovered)} page(s). Select the ones you want to scrape below.")
            except Exception as e:
                st.error(str(e))

    if "discovered_urls" in st.session_state:
        discovered_urls = st.session_state["discovered_urls"]
        st.subheader("Select pages to scrape")
        st.caption("Uncheck any page you don’t want to scrape, then click **Scrape selected**.")
        sel_col, desel_col, _ = st.columns([1, 1, 4])
        with sel_col:
            if st.button("Select all"):
                for i in range(len(discovered_urls)):
                    st.session_state[f"page_{i}"] = True
        with desel_col:
            if st.button("Deselect all"):
                for i in range(len(discovered_urls)):
                    st.session_state[f"page_{i}"] = False
        for i, u in enumerate(discovered_urls):
            label = u if len(u) <= 90 else u[:87] + "..."
            st.checkbox(label, value=st.session_state.get(f"page_{i}", True), key=f"page_{i}")

        if st.button("Scrape selected"):
            selected = [
                st.session_state["discovered_urls"][i]
                for i in range(len(st.session_state["discovered_urls"]))
                if st.session_state.get(f"page_{i}", True)
            ]
            if not selected:
                st.warning("Select at least one page.")
            else:
                with st.spinner(f"Scraping {len(selected)} page(s)…"):
                    results = scrape_urls(selected)
                st.session_state["last_scraped_list"] = results
                st.success(f"Scraped {len(results)} page(s). Review and save below.")

    if "last_scraped_list" in st.session_state:
        results = st.session_state["last_scraped_list"]
        st.subheader("Scraped data")
        for i, data in enumerate(results):
            with st.expander(f"{data.get('company_name', '?')} — {data.get('source_url', '')[:70]}{'…' if len(data.get('source_url', '')) > 70 else ''}"):
                st.json(data)
        if st.button("Save all to Database"):
            for data in results:
                insert_company(
                    company_name=data["company_name"],
                    description=data.get("description", ""),
                    contact_email=data.get("contact_email", ""),
                    contact_phone=data.get("contact_phone", ""),
                    contact_address=data.get("contact_address", ""),
                    has_contact_form=data.get("has_contact_form", "No"),
                    source_url=data["source_url"],
                )
            st.success(f"Saved {len(results)} record(s) to database.")
            del st.session_state["last_scraped_list"]
            if "discovered_urls" in st.session_state:
                del st.session_state["discovered_urls"]
elif "Manual" in mode:
    st.caption("Use this when the scraper can't access the page (blocked, login required, or you prefer to type it in).")
    with st.form("manual_entry_form"):
        manual_company = st.text_input("Company name", placeholder="e.g. Acme Corp")
        manual_description = st.text_input("Description (optional)", placeholder="e.g. Contact page title or note")
        manual_email = st.text_input("Contact email", placeholder="e.g. contact@company.com")
        manual_phone = st.text_input("Contact phone", placeholder="e.g. +1 234 567 8900")
        manual_address = st.text_area("Contact address (optional)", placeholder="Street, City, State, ZIP")
        manual_has_form = st.selectbox("Has contact form on page?", ["No", "Yes"], index=0)
        manual_url = st.text_input("Source URL (optional)", placeholder="https://example.com/contact")
        submitted = st.form_submit_button("Save to Database")
    if submitted:
        if not manual_company or not manual_company.strip():
            st.error("Company name is required.")
        else:
            insert_company(
                company_name=manual_company.strip(),
                description=manual_description.strip() if manual_description else "",
                contact_email=manual_email.strip() if manual_email else "",
                contact_phone=manual_phone.strip() if manual_phone else "",
                contact_address=manual_address.strip() if manual_address else "",
                has_contact_form=manual_has_form,
                source_url=manual_url.strip() if manual_url else "",
            )
            st.session_state["manual_save_success"] = True
    if st.session_state.get("manual_save_success"):
        st.success("We were able to save successfully.")
        del st.session_state["manual_save_success"]
else:
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
                description=data.get("description", ""),
                contact_email=data.get("contact_email", ""),
                contact_phone=data.get("contact_phone", ""),
                contact_address=data.get("contact_address", ""),
                has_contact_form=data.get("has_contact_form", "No"),
                source_url=data["source_url"],
            )
            st.success("Saved to database.")
            del st.session_state["last_scraped"]
