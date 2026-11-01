import os
import chromadb
from openai import OpenAI

# 1. Setup Clients and correct Paths
client = OpenAI()
db_path = os.path.join("ml_pipeline", "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_collection(name="wcag_guidelines")

# Define test queries and the expected keyword that must appear in a successful chunk match
test_queries = [
    {"query": "What are the requirements for video captions?", "expected_match": "caption"},
    {"query": "How should alternative text be written for images?", "expected_match": "alt text"},
    {"query": "What is the minimum contrast ratio for text?", "expected_match": "contrast"},
]

def calculate_metrics(queries, k=3):
    mrr_score = 0.0
    precision_at_k = 0.0
    total_queries = len(queries)

    for test in queries:
        query_text = test["query"]
        expected = test["expected_match"].lower()

        # 2. Manually embed the query using the exact model used for ingestion
        response = client.embeddings.create(
            input=query_text,
            model="text-embedding-3-small"
        )
        query_vector = response.data[0].embedding

        # 3. Execute semantic search using the vector
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )

        retrieved_documents = results["documents"][0]
        
        # 4. Evaluate Precision@K and MRR
        match_found = False
        for rank, doc in enumerate(retrieved_documents):
            if expected in doc.lower():
                if not match_found:
                    mrr_score += 1.0 / (rank + 1)
                    precision_at_k += 1.0
                    match_found = True
                    
    mrr = mrr_score / total_queries
    p_at_k = precision_at_k / total_queries
    
    return mrr, p_at_k

if __name__ == "__main__":
    k_value = 3
    print("Calculating evaluation metrics. Please wait...")
    mrr, precision = calculate_metrics(test_queries, k=k_value)
    
    print("\n--- Quantitative Analytics: RAG Evaluation ---")
    print(f"Total Test Queries: {len(test_queries)}")
    print(f"Mean Reciprocal Rank (MRR): {mrr:.4f}")
    print(f"Precision@{k_value}: {precision:.4f}")