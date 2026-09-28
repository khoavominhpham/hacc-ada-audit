import json
import os
import time
from openai import OpenAI

def main():
    input_path = os.path.join("ml_pipeline", "data", "chunked_corpus.json")
    output_path = os.path.join("ml_pipeline", "data", "embedded_corpus.json")

    print("Loading chunked corpus...")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Please run Task 2 first.")
        return

    # Initialize OpenAI client (it automatically detects the OPENAI_API_KEY env variable)
    client = OpenAI()
    
    embedded_data = []
    batch_size = 100
    
    print(f"Generating embeddings for {len(chunks)} chunks using text-embedding-3-small...")
    
    # Process in batches to respect rate limits
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        # Extract just the text strings for the API call
        texts = [item["text"] for item in batch]
        
        total_batches = (len(chunks) // batch_size) + 1
        print(f"Processing batch {(i // batch_size) + 1}/{total_batches}...")
        
        try:
            # Call the OpenAI Embeddings API
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            
            # Merge the mathematical vectors back with our original text and metadata
            for j, item in enumerate(batch):
                embedded_item = {
                    "id": item["id"],
                    "embedding": response.data[j].embedding,
                    "text": item["text"],
                    "metadata": {
                        "source": item["source"],
                        "type": item["type"]
                    }
                }
                embedded_data.append(embedded_item)
                
            # Brief 1-second pause to respect API rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing batch {(i // batch_size) + 1}: {e}")
            return
            
    # Save the properly structured data for the Vector Database
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, indent=4)
        
    print(f"\n✅ Task 3 Complete! Generated {len(embedded_data)} embeddings.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
