import requests
from bs4 import BeautifulSoup
import json
import os

# Define our source material URLs
SOURCES = {
    "wcag_2_2": "https://www.w3.org/TR/WCAG22/",
    "ada_title_ii": "https://www.ada.gov/resources/web-guidance/"
}

def fetch_and_clean_html(url, source_name):
    print(f"Fetching data from: {url}...")
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error fetching {url}: Status {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove script, style, and navigation tags
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    # Extract all meaningful text blocks (Headers, Paragraphs, Lists)
    text_blocks = []
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
        clean_text = tag.get_text(strip=True)
        # Filter out tiny boilerplate strings
        if len(clean_text) > 20: 
            text_blocks.append({
                "source": source_name,
                "type": tag.name,
                "content": clean_text
            })
            
    return text_blocks

def main():
    all_data = []
    
    for name, url in SOURCES.items():
        cleaned_blocks = fetch_and_clean_html(url, name)
        all_data.extend(cleaned_blocks)
        print(f"Successfully extracted {len(cleaned_blocks)} text blocks from {name}.")
        
    # Save the cleaned corpus to a JSON file
    output_path = os.path.join("ml_pipeline", "data", "cleaned_corpus.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)
        
    print(f"\nTask 1 Complete! Saved {len(all_data)} total blocks to {output_path}")

if __name__ == "__main__":
    main()