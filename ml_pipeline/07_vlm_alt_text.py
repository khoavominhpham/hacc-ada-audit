import os
from openai import OpenAI

client = OpenAI()

def generate_alt_text(image_url):
    print(f"Analyzing image pixels from: {image_url}...")
    
    system_prompt = (
        "You are an expert ADA web accessibility auditor. "
        "Analyze the provided image and generate concise, highly descriptive alt-text "
        "suitable for a screen reader. Do not include phrases like 'Image of' or 'Picture of'. "
        "If the image contains text, ensure that text is included in your description. "
        "Keep the output under 125 characters if possible."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "low" # Low detail is faster/cheaper and sufficient for basic alt-text
                            }
                        }
                    ]
                }
            ],
            max_tokens=100,
            temperature=0.0 # Zero creativity; factual descriptions only
        )
        
        alt_text = response.choices[0].message.content
        print(f"\n✅ GENERATED ALT-TEXT:\n{alt_text}\n")
        return alt_text
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    # Test 1: The complex virtual meeting photograph
    team_meeting_url = "https://www.hacc.edu/images/team1_2.jpg"
    
    # Test 2: The newly provided WebP image of a campus event
    campus_event_url = "https://www.hacc.edu/Admissions/Connect/images/Harrisburg-Campus-Smart-Start-event.webp"
    
    print("--- Test 1: Virtual Meeting Photograph ---")
    generate_alt_text(team_meeting_url)
    
    print("--- Test 2: Campus Event Photograph (.webp format) ---")
    generate_alt_text(campus_event_url)