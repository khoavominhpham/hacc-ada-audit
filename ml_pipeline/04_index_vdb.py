import os
import json
import chromadb

def main():
    print("Loading embedded corpus...")
    # Adjust this filename if your step 3 saved it differently
    data_path = os.path.join("ml_pipeline", "data", "embedded_corpus.json") 
    
    if not os.path.exists(data_path):
        print(f"Error: Could not find {data_path}. Did Step 3 complete successfully?")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        embedded_data = json.load(f)
        
    db_path = os.path.join("ml_pipeline", "chroma_db")
    print(f"Initializing persistent ChromaDB client at {db_path}...")
    chroma_client = chromadb.PersistentClient(path=db_path)
    
    # Explicitly creating and naming the collection to prevent schema mismatch down the line
    collection = chroma_client.get_or_create_collection(name="wcag_guidelines")
    
    print("Parsing structured data...")
    ids = []
    embeddings = []
    documents = []
    metadatas = []
    
    for i, item in enumerate(embedded_data):
        # Assuming your JSON structure has 'embedding' and 'text'. 
        # Update keys if your Step 3 output uses different names.
        ids.append(f"chunk_{i}")
        embeddings.append(item["embedding"])
        documents.append(item["text"])
        metadatas.append({"source": item.get("source", "wcag"), "chunk_index": i})

    total_vectors = len(embeddings)
    batch_size = 500
    
    print(f"Indexing {total_vectors} vectors into ChromaDB in batches of {batch_size}...")
    
    for i in range(0, total_vectors, batch_size):
        end_idx = min(i + batch_size, total_vectors)
        print(f"Adding batch {i} to {end_idx}...")
        collection.add(
            ids=ids[i:end_idx],
            embeddings=embeddings[i:end_idx],
            documents=documents[i:end_idx],
            metadatas=metadatas[i:end_idx]
        )
        
    print("\n✅ Task 4 Complete!")
    print(f"Successfully indexed {total_vectors} vectors into the local Vector Database.")

if __name__ == "__main__":
    main()