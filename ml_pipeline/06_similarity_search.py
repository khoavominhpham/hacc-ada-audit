import os
import chromadb
from openai import OpenAI

client = OpenAI()

db_path = os.path.join("ml_pipeline", "chroma_db")
chroma_client = chromadb.PersistentClient(path=db_path)
collection = chroma_client.get_collection(name="wcag_guidelines")

def answer_with_rag(query, top_k=3):
    print(f"Embedding user query: '{query}'...")
    
    # 1. Retrieve the relevant vectors
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_vector = response.data[0].embedding
    
    print(f"Retrieving top {top_k} nearest neighbors...")
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    
    # Extract the text from the results
    retrieved_chunks = results['documents'][0]
    
    # Print retrieved context for logging/UAT
    for i, chunk in enumerate(retrieved_chunks):
        print(f"\n--- RETRIEVED CONTEXT {i+1} ---")
        print(chunk)
        
    # 2. Generate the grounded answer (eliminating hallucinations)
    print("\nGenerating grounded answer via LLM...")
    
    # Combine the retrieved chunks into a single context block
    context_block = "\n\n".join(retrieved_chunks)
    
    system_prompt = (
        "You are a strict ADA and WCAG compliance assistant. "
        "You must answer the user's question based ONLY on the provided Context. "
        "If the answer is not contained in the Context, you must explicitly state 'I do not have enough information to answer this based on the guidelines.' "
        "Do not invent or assume any rules."
    )
    
    user_prompt = f"Context:\n{context_block}\n\nQuestion: {query}"
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini", # Using the faster, cost-effective model for the reasoning step
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0 # Force deterministic, factual answers
    )
    
    print(f"\n🤖 FINAL AI ANSWER:\n{completion.choices[0].message.content}\n")

if __name__ == "__main__":
    test_query = "What is the requirement for image alt text?"
    answer_with_rag(test_query)