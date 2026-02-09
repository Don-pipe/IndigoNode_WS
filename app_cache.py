"""
Shared Streamlit cache for DB init and company list. Use get_cached_companies()
everywhere; call clear_companies_cache() after insert/delete so other pages see fresh data.
"""
import streamlit as st
from db import database


@st.cache_resource
def init_db_once():
    """Run DB init once per session instead of on every script rerun."""
    database.init_db()


@st.cache_data(ttl=300)
def get_cached_companies():
    """Cached companies DataFrame. Cleared on insert/delete so data stays fresh."""
    init_db_once()
    return database.get_all_companies()


def clear_companies_cache():
    """Call after inserting or deleting companies so Dashboard/Database show fresh data."""
    get_cached_companies.clear()
