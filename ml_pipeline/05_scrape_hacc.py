import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

BASE_DOMAIN = "https://www.hacc.edu"
SEED_URLS = [
    "https://www.hacc.edu/Site-Map.cfm",
    "https://www.hacc.edu/Admissions/index.cfm",
    "https://www.hacc.edu/ProgramsandCourses/index.cfm",
    "https://www.hacc.edu/Students/index.cfm",
    "https://www.hacc.edu/Paying/index.cfm",
    "https://www.hacc.edu/Campuses/index.cfm",
    "https://www.hacc.edu/AboutHACC/index.cfm"
]

MAX_PAGES = 100  # 100 clean editorial content pages

def clean_and_extract(html, page_url):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract page title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True).replace(" - HACC", "") if title_tag else page_url

    # Discover internal HACC .cfm links before decomposing navigation
    discovered_links = set()
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        full_url = urljoin(BASE_DOMAIN, href).split('#')[0].split('?')[0]
        parsed = urlparse(full_url)
        if parsed.netloc == "www.hacc.edu" and full_url.endswith(".cfm"):
            discovered_links.add(full_url)

    # Isolate the actual CMS authoring area (#CS_Element_MainBody)
    main_content = soup.find(id="CS_Element_MainBody")
    if not main_content:
        for tag in soup(["nav", "header", "footer", "script", "style", "noscript"]):
            tag.decompose()
        main_content = soup.body if soup.body else soup
    else:
        for tag in main_content(["script", "style", "noscript"]):
            tag.decompose()

    # Convert relative image src="/..." to absolute URLs so OpenAI VLM can fetch them
    for img in main_content.find_all('img'):
        if img.get('src') and img['src'].startswith('/'):
            img['src'] = urljoin(BASE_DOMAIN, img['src'])

    body_html = main_content.decode_contents().strip()
    return title, body_html, discovered_links

def crawl_hacc(max_pages=MAX_PAGES):
    visited = set()
    queue = list(SEED_URLS)
    scraped_data = []

    headers = {"User-Agent": "HACC-ADA-Research-Crawler/1.0"}

    while queue and len(scraped_data) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200 or 'text/html' not in resp.headers.get('Content-Type', ''):
                continue

            title, body_html, links = clean_and_extract(resp.text, url)

            for link in links:
                if link not in visited and link not in queue:
                    queue.append(link)

            # Use Site-Map.cfm to harvest links, but do NOT include it in the editorial dataset
            if "site-map.cfm" in url.lower() or title.strip().lower() == "site map":
                print(f"[Seed Index] Harvested links from Site Map (excluded from editorial dataset)")
                continue

            # Skip empty shell pages
            if len(body_html) < 200:
                continue

            scraped_data.append({
                "url": url,
                "title": title,
                "body": body_html
            })
            print(f"[{len(scraped_data)}/{max_pages}] Scraped: {title} ({url})")

            time.sleep(0.2)
        except Exception as e:
            print(f"  -> Skipped {url}: {e}")

    output_path = "ml_pipeline/data/hacc_scraped.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4)

    print(f"\n✅ Successfully scraped {len(scraped_data)} editorial HACC pages to {output_path}!")

if __name__ == "__main__":
    crawl_hacc()