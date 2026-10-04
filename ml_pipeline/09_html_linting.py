from bs4 import BeautifulSoup

def lint_heading_hierarchy(html_content):
    print("Running HTML Structural Linting...\n")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract all headings in the order they appear on the page
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not headings:
        print("No headings found.")
        return

    previous_level = 0
    violations = []

    for heading in headings:
        current_level = int(heading.name[1]) # Extracts the integer (e.g., '2' from 'h2')
        text = heading.get_text(strip=True)
        
        print(f"Found <h{current_level}>: {text}")
        
        # WCAG Rule: You cannot skip a heading level downward (e.g., h2 straight to h4)
        if previous_level > 0 and current_level > previous_level + 1:
            violations.append(
                f"WCAG Violation: Skipped heading level from <h{previous_level}> to <h{current_level}> "
                f"(Triggered by: '{text}')"
            )
        
        previous_level = current_level

    if violations:
        print("\n❌ LINTING ERRORS DETECTED:")
        for v in violations:
            print(f" - {v}")
    else:
        print("\n✅ PASS: Heading hierarchy is logically structured.")

if __name__ == "__main__":
    # A test HTML block containing a classic authoring mistake: skipping from H2 to H4
    test_html = """
    <h1>Admissions Process</h1>
    <p>Welcome to HACC.</p>
    
    <h2>Step 1: Apply</h2>
    <p>Submit your application.</p>
    
    <h4>Financial Aid</h4> <!-- ⚠️ Intentional WCAG violation: skipped h3 -->
    <p>Apply for FAFSA.</p>
    
    <h2>Step 2: Transcripts</h2>
    """
    
    lint_heading_hierarchy(test_html)