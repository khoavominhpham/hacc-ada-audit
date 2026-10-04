import textstat

def analyze_readability(text):
    print("Running NLP Readability Analysis...")
    
    # Calculate established structural linguistic metrics
    flesch_kincaid = textstat.flesch_kincaid_grade(text)
    smog = textstat.smog_index(text)
    reading_ease = textstat.flesch_reading_ease(text)
    
    print("\n📊 Readability Scorecard:")
    print(f"Flesch-Kincaid Grade Level: {flesch_kincaid}")
    print(f"SMOG Index:                 {smog}")
    print(f"Flesch Reading Ease:        {reading_ease}")
    
    # Cognitive Accessibility Logic: WCAG recommends ~lower secondary education level (Grade 8-9)
    if flesch_kincaid > 9.0 or smog > 9.0:
        print("\n⚠️ WARNING: Text exceeds recommended 9th-grade reading level.")
        print("This may violate cognitive accessibility guidelines. Consider simplifying complex vocabulary and sentence structures.")
    else:
        print("\n✅ PASS: Text is within acceptable cognitive readability bounds.")

if __name__ == "__main__":
    # A deliberately complex, "academic-sounding" test sentence 
    test_text = (
        "Students must unequivocally submit all official matriculation documentation, "
        "including certified transcripts and notarized immunization records, prior to "
        "the culmination of the registration epoch to circumvent administrative disenrollment."
    )
    
    print(f"Analyzing Test Phrase:\n'{test_text}'\n")
    analyze_readability(test_text)