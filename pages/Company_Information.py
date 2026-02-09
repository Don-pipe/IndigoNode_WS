"""
Company Information page: Search for a company and edit its information.
"""
import streamlit as st
import sys
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from db.database import update_company, delete_company
from app_cache import get_cached_companies, clear_companies_cache


def _str(val):
    """Coerce value to str for display/DB; NaN/None -> ''."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


st.set_page_config(page_title="Company Information", page_icon="🏢", layout="wide")
st.markdown("""
<style>
    .main .block-container {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)
st.title("Company Information")

st.caption("Search for a company and edit its information below.")

# Show success message after save (persists across rerun)
if st.session_state.get("company_info_save_success"):
    st.success("The database change has been completed successfully.")
    del st.session_state["company_info_save_success"]
# Show message after delete and reset selectbox (before ci_select widget is created)
if st.session_state.get("company_info_delete_success"):
    st.error("Row Deleted Successfully.")
    st.session_state["ci_select"] = "— Select a company —"
    del st.session_state["company_info_delete_success"]

df = get_cached_companies()

if df is None or df.empty:
    st.info("No companies in the database yet. Add data from the Home page.")
else:
    # Compute filtered list and selection (needed for both columns)
    search_query = st.session_state.get("ci_search", "")
    if search_query and str(search_query).strip():
        q = str(search_query).strip().lower()
        mask = (
            df["company_name"].fillna("").astype(str).str.lower().str.contains(q, regex=False)
            | df["contact_email"].fillna("").astype(str).str.lower().str.contains(q, regex=False)
            | df["contact_phone"].fillna("").astype(str).str.contains(q, regex=False)
        )
        filtered_df = df.loc[mask]
    else:
        filtered_df = df

    _placeholder = "— Select a company —"
    options = {_placeholder: None}
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            rid = row.get("id")
            if pd.notna(rid) and rid is not None:
                name = _str(row.get("company_name", "?"))
                options[f"ID {int(rid)} — {name}"] = int(rid)
    option_keys = list(options.keys())

    col_search, col_card = st.columns([1, 2])

    with col_search:
        st.subheader("Search & filter")
        search_query = st.text_input(
            "Search",
            placeholder="Search by company name, email, or phone…",
            key="ci_search",
        )
        if filtered_df.empty:
            st.warning("No companies match your search.")
        chosen_label = st.selectbox(
            "Select company to view or edit",
            options=option_keys,
            key="ci_select",
        )
        chosen_id = options.get(chosen_label)

    with col_card:
        st.subheader("Company information")
        if chosen_id is not None:
            row = filtered_df[filtered_df["id"] == chosen_id].iloc[0]

            with st.form("company_info_edit"):
                st.caption(f"**{_str(row.get('company_name'))}** (ID {chosen_id})")
                company_name = st.text_input("Company name", value=_str(row.get("company_name")), key="ci_company")
                description = st.text_input("Description", value=_str(row.get("description")), key="ci_desc")
                contact_email = st.text_input("Contact email", value=_str(row.get("contact_email")), key="ci_email")
                contact_phone = st.text_input("Contact phone", value=_str(row.get("contact_phone")), key="ci_phone")
                contact_address = st.text_area("Contact address", value=_str(row.get("contact_address")), key="ci_address")
                has_contact_form = st.selectbox(
                    "Has contact form",
                    ["No", "Yes"],
                    index=1 if _str(row.get("has_contact_form")).lower() == "yes" else 0,
                    key="ci_has_form",
                )
                source_url = st.text_input("Source URL", value=_str(row.get("source_url")), key="ci_url")
                btn_col1, btn_col2, _ = st.columns([1, 1, 6])
                with btn_col1:
                    save_clicked = st.form_submit_button("Save")
                with btn_col2:
                    delete_clicked = st.form_submit_button("Delete")

            if save_clicked:
                if not company_name or not company_name.strip():
                    st.error("Company name is required.")
                else:
                    update_company(
                        company_id=chosen_id,
                        company_name=company_name.strip(),
                        description=(description or "").strip(),
                        contact_email=(contact_email or "").strip(),
                        contact_phone=(contact_phone or "").strip(),
                        contact_address=(contact_address or "").strip(),
                        has_contact_form=has_contact_form or "No",
                        source_url=(source_url or "").strip(),
                    )
                    clear_companies_cache()
                    st.session_state["company_info_save_success"] = True
                    st.rerun()

            if delete_clicked:
                delete_company(chosen_id)
                clear_companies_cache()
                st.session_state["company_info_delete_success"] = True
                st.rerun()
        else:
            st.info("Select a company from the list to view and edit its information.")
