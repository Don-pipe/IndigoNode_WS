"""
Web scraping logic for company contact information.
Extracts: company name (from URL), description (page title), email, phone, address, source URL.
"""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\+?[\d\s\-().]{10,}")
ADDRESS_REGEX = re.compile(
    r"\d+[\s\w.-]+(?:street|st|avenue|ave|blvd|boulevard|road|rd|drive|dr|way|lane|ln|court|ct)\.?\s*[,\s]*[\w\s.-]+",
    re.I,
)


def _extract_contact(soup: BeautifulSoup, text: str) -> tuple[str, str, str]:
    """Extract email, phone, and address from page. Returns (email, phone, address)."""
    email, phone, address = "", "", ""

    for a in soup.find_all("a", href=re.compile(r"^mailto:", re.I)):
        href = a.get("href", "")
        if "?" in href:
            href = href.split("?")[0]
        addr = href.replace("mailto:", "").strip()
        if addr and EMAIL_REGEX.match(addr):
            email = addr[:200]
            break
    if not email:
        match = EMAIL_REGEX.search(text)
        if match:
            email = match.group(0)[:200]

    for a in soup.find_all("a", href=re.compile(r"^tel:", re.I)):
        raw = a.get("href", "").replace("tel:", "").strip()
        digits = re.sub(r"\D", "", raw)
        if len(digits) >= 10:
            phone = raw[:50]
            break
    if not phone:
        for m in PHONE_REGEX.finditer(text):
            digits = re.sub(r"\D", "", m.group(0))
            if len(digits) >= 10:
                phone = m.group(0).strip()[:50]
                break

    addr_tag = soup.find("address")
    if addr_tag:
        address = addr_tag.get_text(separator=" ", strip=True)[:300]
    if not address:
        for el in soup.find_all(class_=re.compile(r"address|location|office", re.I)):
            t = el.get_text(separator=" ", strip=True)
            if 10 < len(t) < 400:
                address = t[:300]
                break
    if not address:
        match = ADDRESS_REGEX.search(text)
        if match:
            address = match.group(0).strip()[:300]

    return (email or "", phone or "", address or "")


def _has_contact_form(soup: BeautifulSoup, url: str) -> str:
    """
    Detect if the page has a form or embedded form (e.g. iframe), and if it looks like a contact form.
    Returns "Yes" if the page has a form (or form iframe) and context suggests contact, else "No".
    """
    url_lower = url.lower()
    path_has_contact = "contact" in url_lower

    # 1) In-page <form> elements
    forms = soup.find_all("form")
    if forms:
        for form in forms:
            action = (form.get("action") or "").lower()
            form_id = (form.get("id") or "").lower()
            form_class = " ".join(form.get("class", [])).lower() if form.get("class") else ""
            parent_text = ""
            for parent in form.parents:
                if parent.name and parent.get_text(strip=True):
                    parent_text = parent.get_text(separator=" ", strip=True)[:500].lower()
                    break
            if path_has_contact or "contact" in action or "contact" in form_id or "contact" in form_class or "contact" in parent_text:
                return "Yes"
            inputs = form.find_all(["input", "textarea"], type=re.compile(r"text|email|tel", re.I))
            inputs += form.find_all("textarea")
            names = " ".join((inp.get("name") or inp.get("id") or "").lower() for inp in inputs)
            if "email" in names or "message" in names or "name" in names:
                return "Yes"
        return "Yes" if path_has_contact else "No"

    # 2) Embedded form via iframe (Wufoo, Typeform, Jotform, Google Forms, etc.)
    form_embed_pattern = re.compile(
        r"wufoo|typeform|jotform|google\.com/forms|forms\.office\.com|formstack|hubspot.*form|form",
        re.I,
    )
    for iframe in soup.find_all("iframe"):
        src = (iframe.get("src") or "").lower()
        iframe_id = (iframe.get("id") or "").lower()
        iframe_class = " ".join(iframe.get("class", [])).lower() if iframe.get("class") else ""
        if form_embed_pattern.search(src) or form_embed_pattern.search(iframe_id) or form_embed_pattern.search(iframe_class):
            return "Yes"
        # iframe with "form" in id/class and we're on a contact-like URL
        if path_has_contact and ("form" in iframe_id or "form" in iframe_class or "form" in src):
            return "Yes"

    return "No"


def scrape_url(url: str) -> dict:
    """
    Scrape a URL for company contact information.
    Returns: company_name, description, contact_email, contact_phone, contact_address, has_contact_form, source_url.
    """
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (compatible; IndigoNode/1.0)"})
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}") from e

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    netloc = urlparse(url).netloc.replace("www.", "")
    company_name = (netloc.split(".")[0] if netloc else "") or "unknown"

    description = ""
    if soup.title and soup.title.string:
        description = soup.title.string.strip()[:500]

    contact_email, contact_phone, contact_address = _extract_contact(soup, text)
    has_contact_form = _has_contact_form(soup, url)

    return {
        "company_name": company_name,
        "description": description,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
        "contact_address": contact_address,
        "has_contact_form": has_contact_form,
        "source_url": url,
    }


def _normalize_url(url: str, base: str) -> str:
    """Resolve url relative to base and strip fragment."""
    full = urljoin(base, url.strip())
    parsed = urlparse(full)
    if not parsed.netloc or parsed.scheme not in ("http", "https"):
        return ""
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def _same_domain_links(soup: BeautifulSoup, base_url: str) -> set[str]:
    """Extract absolute same-domain links from page."""
    base_netloc = urlparse(base_url).netloc.replace("www.", "")
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        full = _normalize_url(href, base_url)
        if not full:
            continue
        netloc = urlparse(full).netloc.replace("www.", "")
        if netloc != base_netloc:
            continue
        seen.add(full)
    return seen


def discover_site_urls(start_url: str, max_pages: int = 50) -> list[str]:
    """BFS crawl from start_url, collecting same-domain URLs up to max_pages."""
    start_url = _normalize_url(start_url, start_url)
    if not start_url:
        return []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IndigoNode/1.0)"}
    to_visit = [start_url]
    visited = {start_url}
    urls = [start_url]

    while to_visit and len(urls) < max_pages:
        url = to_visit.pop(0)
        try:
            resp = requests.get(url, timeout=10, headers=headers)
            resp.raise_for_status()
        except requests.RequestException:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        for link in _same_domain_links(soup, url):
            if link not in visited:
                visited.add(link)
                to_visit.append(link)
                urls.append(link)
                if len(urls) >= max_pages:
                    break
    return urls


def scrape_urls(url_list: list[str]) -> list[dict]:
    """Scrape each URL for contact info. Returns list of results; skips failures."""
    results = []
    for u in url_list:
        try:
            results.append(scrape_url(u))
        except ValueError:
            continue
    return results
