"""
Database page: View & query SQLite data.
"""
import streamlit as st
import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import delete_company, update_company
from app_cache import get_cached_companies, clear_companies_cache

def _str(val):
    """Coerce value to str for DB; NaN/None -> ''."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


st.set_page_config(page_title="Database", page_icon="🗄️", layout="wide")
# Use full width for the data grid
st.markdown("""
<style>
    .main .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)
st.title("Database")

df = get_cached_companies()
if df is not None and not df.empty:
    # Filter at the top
    st.subheader("Filter")
    col1, col2 = st.columns(2)
    with col1:
        company_filter = st.text_input("Company name contains", placeholder="e.g. Acme")
    with col2:
        email_filter = st.text_input("Email contains", placeholder="e.g. @company.com")

    if company_filter or email_filter:
        mask = pd.Series(True, index=df.index)
        if company_filter:
            mask &= df["company_name"].fillna("").astype(str).str.contains(company_filter, case=False, regex=False)
        if email_filter:
            mask &= df["contact_email"].fillna("").astype(str).str.contains(email_filter, case=False, regex=False)
        filtered_df = df.loc[mask]
        if filtered_df.empty:
            st.info("No matches.")
            display_df = pd.DataFrame()
            rows_for_delete = []
        else:
            display_df = filtered_df.copy()
            rows_for_delete = filtered_df.to_dict("records")
    else:
        display_df = df.copy()
        rows_for_delete = df.to_dict("records") if "id" in df.columns else []

    # Editable grid (id and scraped_at read-only)
    if not display_df.empty:
        st.subheader("Edit data")
        st.caption("Edit cells in the grid, then click **Save changes to database**.")
        column_config = {}
        if "id" in display_df.columns:
            column_config["id"] = st.column_config.NumberColumn("ID", disabled=True)
        if "scraped_at" in display_df.columns:
            column_config["scraped_at"] = st.column_config.TextColumn("Scraped at", disabled=True)
        edited_df = st.data_editor(
            display_df,
            use_container_width=True,
            num_rows="fixed",
            column_config=column_config or None,
            key="database_editor",
        )
        if st.button("Save changes to database"):
            for _, row in edited_df.iterrows():
                rid = row.get("id")
                if rid is not None and pd.notna(rid):
                    update_company(
                        company_id=int(rid),
                        company_name=_str(row.get("company_name")),
                        description=_str(row.get("description")),
                        contact_email=_str(row.get("contact_email")),
                        contact_phone=_str(row.get("contact_phone")),
                        contact_address=_str(row.get("contact_address")),
                        has_contact_form=_str(row.get("has_contact_form")) or "No",
                        source_url=_str(row.get("source_url")),
                    )
            clear_companies_cache()
            st.success("Changes saved.")
            st.rerun()

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
                clear_companies_cache()
                st.success(f"Deleted {len(ids)} row(s).")
                st.rerun()
else:
    st.info("No data yet. Scrape URLs from the Home page to populate contact data.")
