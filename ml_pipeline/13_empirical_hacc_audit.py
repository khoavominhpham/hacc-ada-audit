import json
import csv
import statistics
from bs4 import BeautifulSoup
import textstat

INPUT_JSON = "ml_pipeline/data/hacc_scraped.json"
OUTPUT_CSV = "ml_pipeline/data/hacc_empirical_audit.csv"

def extract_punctuated_text(soup: BeautifulSoup) -> str:
    """Ensures list items, table cells, and headings end with sentence punctuation so textstat doesn't fuse them into a giant run-on sentence."""
    text_blocks = []
    for block in soup.find_all(['p', 'li', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        t = block.get_text(separator=' ', strip=True)
        if t:
            if t[-1] not in '.!?':
                t += '.'
            text_blocks.append(t)
    return " ".join(text_blocks) if text_blocks else soup.get_text(separator='. ', strip=True)

def audit_and_remediate_page(page):
    soup = BeautifulSoup(page["body"], "html.parser")
    
    # 1. Heading Hierarchy Audit (Assuming page title is <h1>, body starts at <h2>)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    prev_level = 1
    level_map = {1: 1}
    heading_skips = 0

    for h in headings:
        orig_level = int(h.name[1])
        if orig_level in level_map and orig_level > 1:
            target_level = level_map[orig_level]
        elif orig_level > prev_level + 1:
            target_level = prev_level + 1
        else:
            target_level = orig_level

        for k in list(level_map.keys()):
            if k > orig_level:
                del level_map[k]
        level_map[orig_level] = target_level

        if target_level != orig_level:
            heading_skips += 1
            h.name = f"h{target_level}"
        prev_level = target_level

    # 2. Image Alt-Text Audit
    images = soup.find_all('img')
    total_images = len(images)
    missing_or_weak_alt = 0
    for img in images:
        alt = img.get('alt', '').strip()
        if not img.has_attr('alt') or alt == "" or alt.lower() in ["image", "picture", "photo", "img", "hacc"]:
            missing_or_weak_alt += 1

    # 3. Link Quality Audit (Malformed href or generic 'here'/'click here' text)
    links = soup.find_all('a')
    ambiguous_or_broken_links = 0
    for a in links:
        href = a.get('href', '').strip()
        link_text = a.get_text(strip=True).lower()
        if href.startswith("href=") or link_text in ["here", "click here", "read more", "learn more", "find out how here."]:
            ambiguous_or_broken_links += 1

    # 4. Cognitive Readability (Flesch-Kincaid & SMOG)
    raw_text = extract_punctuated_text(soup)
    word_count = len(raw_text.split())
    fk_grade = round(textstat.flesch_kincaid_grade(raw_text), 2) if word_count > 15 else 0.0
    smog_score = round(textstat.smog_index(raw_text), 2) if word_count > 30 else 0.0
    exceeds_grade_9 = 1 if (fk_grade > 9.0 or smog_score > 9.0) else 0

    total_violations = heading_skips + missing_or_weak_alt + ambiguous_or_broken_links + exceeds_grade_9

    return {
        "title": page["title"],
        "url": page.get("url", ""),
        "word_count": word_count,
        "total_headings": len(headings),
        "heading_skips": heading_skips,
        "total_images": total_images,
        "missing_or_weak_alt": missing_or_weak_alt,
        "ambiguous_or_broken_links": ambiguous_or_broken_links,
        "flesch_kincaid_grade": fk_grade,
        "smog_index": smog_score,
        "exceeds_grade_9": exceeds_grade_9,
        "total_violations": total_violations
    }

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        pages = json.load(f)

    # Filter out system utility directory (Site Map) if present
    editorial_pages = [p for p in pages if p["title"].strip().lower() != "site map"]
    results = [audit_and_remediate_page(p) for p in editorial_pages]
    results.sort(key=lambda x: x["total_violations"], reverse=True)

    # Write detailed CSV for Jonathan & GT Appendix
    fieldnames = list(results[0].keys())
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Calculate Aggregate Empirical Metrics
    n = len(results)
    pages_with_violations = sum(1 for r in results if r["total_violations"] > 0)
    total_heading_skips = sum(r["heading_skips"] for r in results)
    pages_with_heading_skips = sum(1 for r in results if r["heading_skips"] > 0)
    total_imgs = sum(r["total_images"] for r in results)
    total_bad_alt = sum(r["missing_or_weak_alt"] for r in results)
    total_bad_links = sum(r["ambiguous_or_broken_links"] for r in results)
    
    fk_scores = [r["flesch_kincaid_grade"] for r in results if r["flesch_kincaid_grade"] > 0]
    smog_scores = [r["smog_index"] for r in results if r["smog_index"] > 0]
    pages_over_grade_9 = sum(r["exceeds_grade_9"] for r in results)

    print("=" * 70)
    print(f"📊 EMPIRICAL HACC EDITORIAL CONTENT AUDIT (N = {n} Pages, Excl. Site Map)")
    print("=" * 70)
    print(f"Pages Failing >= 1 WCAG Criterion:   {pages_with_violations}/{n} ({pages_with_violations/n*100:.1f}%)")
    print(f"Pages with Skipped Heading Levels:   {pages_with_heading_skips}/{n} ({pages_with_heading_skips/n*100:.1f}%) | Total Skips: {total_heading_skips}")
    print(f"Total Content Images Audited:        {total_imgs} | Missing/Weak Alt: {total_bad_alt}")
    print(f"Ambiguous/Malformed Anchor Links:    {total_bad_links}")
    print(f"Mean Flesch-Kincaid Grade Level:     {statistics.mean(fk_scores):.2f} (SD: {statistics.stdev(fk_scores):.2f} | Median: {statistics.median(fk_scores):.2f})")
    print(f"Mean SMOG Readability Index:         {statistics.mean(smog_scores):.2f} (SD: {statistics.stdev(smog_scores):.2f} | Median: {statistics.median(smog_scores):.2f})")
    print(f"Pages Exceeding WCAG Grade 9 Target: {pages_over_grade_9}/{n} ({pages_over_grade_9/n*100:.1f}%)")
    print("-" * 70)
    print("Top 5 Highest-Violation HACC Editorial Pages:")
    for r in results[:5]:
        print(f" - {r['title'][:42]:<42} | {r['total_violations']} violations (FK: {r['flesch_kincaid_grade']}, Skips: {r['heading_skips']})")
    print("-" * 70)
    print(f"✅ Full page-by-page CSV exported to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()