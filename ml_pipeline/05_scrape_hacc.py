import requests
from bs4 import BeautifulSoup
import json
import os

URLS = {
    "Admissions: Get Started": "https://www.hacc.edu/Admissions/index.cfm",
    "Programs & Courses": "https://www.hacc.edu/ProgramsandCourses/index.cfm",
    "Student Support": "https://www.hacc.edu/Students/index.cfm",
    "About HACC": "https://www.hacc.edu/AboutHACC/index.cfm"
}

def scrape_clean_page(url, title):
    print(f"Scraping {title}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Keep it simple: just remove scripts, styles, and basic HTML5 layout tags
    for element in soup(["nav", "header", "footer", "script", "style"]):
        element.decompose()

    # Extract the HTML of the body (preserving tags like <p>, <h2>, <ul>)
    if soup.body:
        body_html = soup.body.decode_contents().strip()
    else:
        body_html = str(soup)
    
    return {
        "title": title,
        "body": body_html
    }

def main():
    scraped_data = []
    for title, url in URLS.items():
        data = scrape_clean_page(url, title)
        scraped_data.append(data)
        
    direct_path = "ml_pipeline/data/hacc_scraped.json"
    
    with open(direct_path, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4)
            
    print(f"Successfully scraped and preserved HTML for {len(scraped_data)} pages!")

if __name__ == "__main__":
    main()