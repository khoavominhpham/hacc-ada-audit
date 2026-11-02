import os
import chromadb
from openai import OpenAI

client = OpenAI()
db_path = os.path.join("ml_pipeline", "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_collection(name="wcag_guidelines")

TEST_QUERIES = [
    {"query": "heading hierarchy levels logical structure", "expected_keyword": "headings"},
    {"query": "What is the requirement for image alt text?", "expected_keyword": "text alternative"},
    {"query": "cognitive readability reading level clear simple language", "expected_keyword": "reading level"},
    {"query": "contrast ratio for text and background", "expected_keyword": "contrast"},
    {"query": "keyboard navigation focus order", "expected_keyword": "keyboard"}
]

def calculate_rag_metrics():
    print("==========================================================")
    print("🧠 RAG VECTOR DATABASE EVALUATION (MRR & Precision@3)")
    print("==========================================================\n")
    
    mrr_sum = 0
    precision_at_3_sum = 0
    k = 3

    for idx, test in enumerate(TEST_QUERIES, 1):
        emb = client.embeddings.create(input=test["query"], model="text-embedding-3-small").data[0].embedding
        results = collection.query(query_embeddings=[emb], n_results=k)
        
        docs = results["documents"][0]
        rank = 0
        hit = False
        
        for r, doc in enumerate(docs, 1):
            if test["expected_keyword"].lower() in doc.lower():
                rank = r
                hit = True
                break
                
        if hit:
            mrr_sum += (1 / rank)
            precision_at_3_sum += 1  
            
        print(f"Q{idx}: '{test['query']}'")
        print(f" -> Expected: '{test['expected_keyword']}' | Hit at Rank: {rank if rank > 0 else 'None'}\n")

    mrr = mrr_sum / len(TEST_QUERIES)
    precision = precision_at_3_sum / len(TEST_QUERIES)

    print("-" * 58)
    print(f"Mean Reciprocal Rank (MRR): {mrr:.4f} (1.0000 is perfect)")
    print(f"Precision@{k}:               {precision:.4f} (1.0000 is perfect)")

if __name__ == "__main__":
    calculate_rag_metrics()