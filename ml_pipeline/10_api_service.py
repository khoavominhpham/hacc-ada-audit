import os
from urllib.parse import urljoin
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import textstat
import chromadb
from openai import OpenAI

app = FastAPI(title="HACC ADA Accessibility & Auto-Remediation API")
client = OpenAI()

# Connect to Persistent ChromaDB Vector Store
db_path = os.path.join("ml_pipeline", "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_collection(name="wcag_guidelines")

# Cache RAG lookups so repeated violation types don't re-trigger embedding calls
RAG_CACHE = {}

class PageContent(BaseModel):
    html_body: str
    auto_remediate: bool = True

def extract_punctuated_text(soup: BeautifulSoup) -> str:
    """Ensures list items, table cells, and headings end with sentence punctuation for accurate NLP scoring."""
    text_blocks = []
    for block in soup.find_all(['p', 'li', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        t = block.get_text(separator=' ', strip=True)
        if t:
            if t[-1] not in '.!?':
                t += '.'
            text_blocks.append(t)
    return " ".join(text_blocks) if text_blocks else soup.get_text(separator='. ', strip=True)

def get_wcag_citation(query_topic: str) -> str:
    """Retrieves the top WCAG/ADA guideline chunk from ChromaDB."""
    if query_topic in RAG_CACHE:
        return RAG_CACHE[query_topic]
    try:
        emb = client.embeddings.create(
            input=query_topic,
            model="text-embedding-3-small"
        ).data[0].embedding
        results = collection.query(query_embeddings=[emb], n_results=1)
        doc = results["documents"][0][0] if results["documents"] and results["documents"][0] else ""
        snippet = (doc[:220].replace("\n", " ").strip() + "...") if len(doc) > 220 else doc
        RAG_CACHE[query_topic] = snippet
        return snippet
    except Exception as e:
        return f"WCAG 2.2 Level AA Standard ({str(e)})"

def generate_alt_text(image_url: str) -> str:
    """Uses VLM settings from 07_vlm_alt_text.py to describe image pixels."""
    system_prompt = (
        "You are an expert ADA web accessibility auditor. "
        "Analyze the provided image and generate concise, highly descriptive alt-text "
        "suitable for a screen reader. Do not include phrases like 'Image of' or 'Picture of'. "
        "Keep the output under 125 characters if possible."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": image_url, "detail": "low"}}
                ]}
            ],
            max_tokens=80,
            temperature=0.0
        )
        return response.choices[0].message.content.strip().strip('"')
    except Exception as e:
        return f"Accessible campus visual ({str(e)[:40]})"

def simplify_paragraph_html(p_html: str) -> str:
    """Rewrites a complex HTML paragraph to a 9th-grade reading level while preserving inner <a>/<strong> tags."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an ADA cognitive accessibility editor. Rewrite the provided HTML paragraph "
                        "so its Flesch-Kincaid reading level is Grade 8-9 or lower. "
                        "CRITICAL: Preserve all existing HTML tags, <a> links, and href attributes intact. "
                        "Return ONLY the valid rewritten HTML <p>...</p> element without markdown fences."
                    )
                },
                {"role": "user", "content": p_html}
            ],
            max_tokens=300,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return p_html

@app.post("/api/v1/analyze-structure")
async def analyze_structure(content: PageContent):
    try:
        soup = BeautifulSoup(content.html_body, 'html.parser')
        violations = []

        # 1. Heading Structure Check & In-Place DOM Remediation
        # Note: Page Title is <h1> in Drupal, so body content should start at <h2> (previous_remediated_level = 1)
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        previous_remediated_level = 1
        level_map = {1: 1}  # Maps original heading level -> remediated level so sibling headings stay aligned

        for heading in headings:
            orig_level = int(heading.name[1])
            text = heading.get_text(strip=True)

            if orig_level in level_map and orig_level > 1:
                target_level = level_map[orig_level]
            elif orig_level > previous_remediated_level + 1:
                target_level = previous_remediated_level + 1
            else:
                target_level = orig_level

            # Clear deeper mappings when moving back up the hierarchy
            for k in list(level_map.keys()):
                if k > orig_level:
                    del level_map[k]
            level_map[orig_level] = target_level

            if target_level != orig_level:
                violations.append({
                    "category": "Structure",
                    "severity": "Error",
                    "message": f"Skipped heading level to <h{orig_level}> ('{text[:60]}').",
                    "suggestion": f"Auto-remediated tag from <h{orig_level}> to <h{target_level}>.",
                    "wcag_citation": get_wcag_citation("heading hierarchy levels logical structure")
                })
                heading.name = f"h{target_level}"

            previous_remediated_level = target_level

        # 2. Image Alt Text Check & VLM Injection
        images = soup.find_all('img')
        for img in images:
            alt_text = img.get('alt', '').strip()
            src = img.get('src', 'unknown source')
            filename = src.split('/')[-1] if '/' in src else src

            needs_ai = False
            base_msg = ""

            if not img.has_attr('alt'):
                base_msg = f"Image '{filename}' is missing the 'alt' attribute."
                needs_ai = True
            elif alt_text == "":
                base_msg = f"Image '{filename}' has an empty 'alt' attribute."
                needs_ai = True
            elif alt_text.lower() in ["image", "picture", "photo", "img", "banner", "graphic", "hacc"]:
                base_msg = f"Image '{filename}' uses non-descriptive alt text ('{alt_text}')."
                needs_ai = True

            if needs_ai:
                full_url = urljoin("https://www.hacc.edu", src) if src.startswith('/') else src
                if full_url.startswith('http'):
                    ai_alt = generate_alt_text(full_url)
                    img['alt'] = ai_alt  # Inject directly into DOM
                    suggestion_msg = f"Injected VLM alt-text: \"{ai_alt}\""
                else:
                    suggestion_msg = "Provide a descriptive alt attribute (public URL required for VLM)."

                violations.append({
                    "category": "Media",
                    "severity": "Error",
                    "message": base_msg,
                    "suggestion": suggestion_msg,
                    "wcag_citation": get_wcag_citation("What is the requirement for image alt text?")
                })

        # 3. Cognitive Readability Check (Flesch-Kincaid & SMOG Index) + Paragraph Auto-Simplification
        raw_text = extract_punctuated_text(soup)
        fk_grade = 0.0
        smog_grade = 0.0
        remediated_fk_grade = 0.0

        if len(raw_text.split()) > 15:
            fk_grade = round(textstat.flesch_kincaid_grade(raw_text), 1)
            smog_grade = round(textstat.smog_index(raw_text), 1)

            if fk_grade > 9.0 or smog_grade > 9.0:
                if content.auto_remediate:
                    rewritten_count = 0
                    for p in soup.find_all('p'):
                        p_text = p.get_text(strip=True)
                        # Target dense paragraphs (>18 words and >Grade 9.5)
                        if len(p_text.split()) >= 18 and textstat.flesch_kincaid_grade(p_text) > 9.5 and rewritten_count < 4:
                            new_p_html = simplify_paragraph_html(str(p))
                            new_p_soup = BeautifulSoup(new_p_html, 'html.parser')
                            if new_p_soup.p:
                                p.replace_with(new_p_soup.p)
                                rewritten_count += 1

                new_raw_text = extract_punctuated_text(soup)
                remediated_fk_grade = round(textstat.flesch_kincaid_grade(new_raw_text), 1)

                violations.append({
                    "category": "Cognitive",
                    "severity": "Warning",
                    "message": f"Readability exceeds target (Flesch-Kincaid: Grade {fk_grade}, SMOG Index: {smog_grade}).",
                    "suggestion": f"AI simplified complex paragraphs (New Flesch-Kincaid: Grade {remediated_fk_grade}). Target is Grade 9.0 or lower.",
                    "wcag_citation": get_wcag_citation("cognitive readability reading level clear simple language")
                })

        remediated_html = str(soup)

        return {
            "status": "success",
            "violations_found": len(violations),
            "metrics": {
                "original_fk_grade": fk_grade,
                "original_smog": smog_grade,
                "remediated_fk_grade": remediated_fk_grade if remediated_fk_grade else fk_grade
            },
            "violations": violations,
            "remediated_html": remediated_html
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)