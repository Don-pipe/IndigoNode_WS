"""
Web scraping logic using BeautifulSoup.
Extracts company name (from URL), description (page title), referral program, payout, outsourcing type, and source URL.
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def scrape_url(url: str) -> dict:
    """
    Scrape a URL and return structured data for the companies table.
    Returns dict with: company_name (from URL domain), description (page title), referral_program,
    referral_payout, outsourcing_type, source_url.
    """
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (compatible; IndigoNode/1.0)"})
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}") from e

    soup = BeautifulSoup(resp.text, "html.parser")

    # Company name = URL domain name (e.g. thevirtualgurus.com -> thevirtualgurus)
    netloc = urlparse(url).netloc.replace("www.", "")
    company_name = netloc.split(".")[0] if netloc else ""

    # Description = page title (e.g. "Introducing Virtual Gurus' All-New Referral Program – Virtual Gurus")
    description = ""
    if soup.title and soup.title.string:
        description = soup.title.string.strip()[:500]

    # Look for referral / payout / outsourcing keywords in text
    text = soup.get_text(separator=" ", strip=True).lower()
    referral_program = "No"
    if any(k in text for k in ("referral", "refer", "refer a friend", "referral program")):
        referral_program = "Yes"

    referral_payout = ""
    # Simple payout patterns ($500, $1000, etc.)
    for m in re.finditer(r"\$[\d,]+(?:\s*(?:USD|dollars?))?", text, re.I):
        referral_payout = m.group(0).strip()
        break
    if not referral_payout and re.search(r"(\d+)\s*(?:USD|dollars?)", text):
        referral_payout = re.search(r"(\d+)\s*(?:USD|dollars?)", text).group(0)

    outsourcing_type = ""
    for kw in ("outsourcing", "outsource", "offshore", "remote", "bpo", "staffing"):
        if kw in text:
            outsourcing_type = kw
            break

    return {
        "company_name": company_name or "unknown",
        "description": description,
        "referral_program": referral_program,
        "referral_payout": referral_payout or "N/A",
        "outsourcing_type": outsourcing_type or "N/A",
        "source_url": url,
    }
