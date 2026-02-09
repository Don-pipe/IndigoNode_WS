"""
Home page: URL input and web scraping. Save to SQLite after confirmation.
"""
import streamlit as st
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db.database import insert_company
from app_cache import init_db_once, clear_companies_cache


def _str(val):
    """Coerce value to str for DB; NaN/None -> ''."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()

st.set_page_config(page_title="IndigoNode", page_icon="🏠")
st.title("IndigoNode – Web Scraping")

init_db_once()

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
                from functions.scraper import discover_site_urls
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
                from functions.scraper import scrape_urls
                with st.spinner(f"Scraping {len(selected)} page(s)…"):
                    results = scrape_urls(selected)
                st.session_state["last_scraped_list"] = results
                st.success(f"Scraped {len(results)} page(s). Review and save below.")

    if "last_scraped_list" in st.session_state:
        results = st.session_state["last_scraped_list"]
        st.subheader("Edit scraped data")
        st.caption("Fields are shown as rows; each column is one record. Edit any cell, then click **Save all to Database**.")
        cols = ["company_name", "description", "contact_email", "contact_phone", "contact_address", "has_contact_form", "source_url"]
        row_labels = ["Company name", "Description", "Contact email", "Contact phone", "Contact address", "Has contact form", "Source URL"]
        # Build table: rows = fields, columns = Record 1, Record 2, ...
        data_by_field = [[_str(r.get(c)) for r in results] for c in cols]
        df_vertical = pd.DataFrame(
            {f"Record {i+1}": [data_by_field[j][i] for j in range(len(cols))] for i in range(len(results))},
            index=row_labels,
        )
        edited_df = st.data_editor(df_vertical, use_container_width=True, num_rows="fixed", key="edit_scraped_list")
        if st.button("Save all to Database"):
            for j, col in enumerate(edited_df.columns):
                row_vals = [edited_df.iloc[i, j] for i in range(len(cols))]
                insert_company(
                    company_name=_str(row_vals[0]),
                    description=_str(row_vals[1]),
                    contact_email=_str(row_vals[2]),
                    contact_phone=_str(row_vals[3]),
                    contact_address=_str(row_vals[4]),
                    has_contact_form=_str(row_vals[5]) or "No",
                    source_url=_str(row_vals[6]),
                )
            clear_companies_cache()
            st.success(f"Saved {len(edited_df.columns)} record(s) to database.")
            del st.session_state["last_scraped_list"]
            if "discovered_urls" in st.session_state:
                del st.session_state["discovered_urls"]
            st.rerun()
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
            clear_companies_cache()
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
                from functions.scraper import scrape_url
                data = scrape_url(url.strip())
                st.session_state["last_scraped"] = data
                st.success("Scraping finished. Review the data below.")
            except ValueError as e:
                st.error(str(e))

    if "last_scraped" in st.session_state:
        data = st.session_state["last_scraped"]
        st.subheader("Edit scraped data")
        st.caption("Edit any field below, then click **Save to Database**.")
        with st.form("edit_single_form"):
            company_name = st.text_input("Company name", value=data.get("company_name", ""))
            description = st.text_input("Description", value=data.get("description", ""))
            contact_email = st.text_input("Contact email", value=data.get("contact_email", ""))
            contact_phone = st.text_input("Contact phone", value=data.get("contact_phone", ""))
            contact_address = st.text_area("Contact address", value=data.get("contact_address", ""))
            has_contact_form = st.selectbox("Has contact form", ["No", "Yes"], index=1 if (data.get("has_contact_form") or "").strip().lower() == "yes" else 0)
            source_url = st.text_input("Source URL", value=data.get("source_url", ""))
            submitted = st.form_submit_button("Save to Database")
        if submitted:
            insert_company(
                company_name=(company_name or "").strip(),
                description=(description or "").strip(),
                contact_email=(contact_email or "").strip(),
                contact_phone=(contact_phone or "").strip(),
                contact_address=(contact_address or "").strip(),
                has_contact_form=has_contact_form or "No",
                source_url=(source_url or "").strip(),
            )
            clear_companies_cache()
            st.success("Saved to database.")
            del st.session_state["last_scraped"]
            st.rerun()
