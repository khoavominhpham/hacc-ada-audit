import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter


def main():
    input_path = os.path.join("ml_pipeline", "data", "cleaned_corpus.json")
    output_path = os.path.join("ml_pipeline", "data", "chunked_corpus.json")

    print("Loading cleaned corpus...")
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Please run Task 1 first.")
        return

    # Initialize the LangChain text splitter
    # 800 characters with a 100 character overlap preserves context around WCAG technical rules
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunked_data = []
    print("Chunking text...")

    for block in data:
        # Split the text content of each block
        chunks = text_splitter.split_text(block["content"])
        
        # Keep the metadata attached to each new smaller chunk
        for chunk in chunks:
            chunked_data.append({
                "id": f"{block['source']}_{len(chunked_data)}",
                "source": block["source"],
                "type": block["type"],
                "text": chunk
            })

    # Save the properly chunked data for the Vector Database
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunked_data, f, indent=4)

    print(f"\n✅ Task 2 Complete! Split original dataset into {len(chunked_data)} mathematically optimized chunks.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()