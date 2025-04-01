from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demonstrate_embeddings():
    # 1. Initialize the Sentence Transformer
    logger.info("Initializing Sentence Transformer...")
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    
    # 2. Sample text chunks (medical style rules)
    text_chunks = [
        "adverse events should be abbreviated as AE after first mention",
        "treatment-emergent adverse events must be written as TEAE",
        "serious adverse event should be written as SAE",
        "use 'Subject' instead of 'Patient' throughout the document",
        "measurements should use SI units",
        "p-value should be written as P value"
    ]
    
    # 3. Create embeddings
    logger.info("Creating embeddings...")
    embeddings = model.encode(text_chunks)
    logger.info(f"Embedding shape: {embeddings.shape}")  # Should be (6, 384)
    
    # 4. Initialize FAISS index
    logger.info("Initializing FAISS index...")
    dimension = embeddings.shape[1]  # 384 for this model
    index = faiss.IndexFlatL2(dimension)
    
    # 5. Add embeddings to index
    logger.info("Adding embeddings to FAISS index...")
    index.add(embeddings.astype('float32'))
    
    # 6. Test queries
    test_queries = [
        "how to write adverse event abbreviation",
        "what's the correct way to refer to patients",
        "format for p-values in statistics"
    ]
    
    # 7. Search similar rules
    logger.info("\nTesting queries...")
    query_embeddings = model.encode(test_queries)
    
    # 8. For each query, find the most similar rules
    k = 2  # Number of similar results to return
    for i, query in enumerate(test_queries):
        logger.info(f"\nQuery: {query}")
        
        # Get distances and indices of similar items
        D, I = index.search(
            query_embeddings[i:i+1].astype('float32'),
            k
        )
        
        # Show results
        for dist, idx in zip(D[0], I[0]):
            logger.info(f"Match (distance={dist:.2f}): {text_chunks[idx]}")

if __name__ == "__main__":
    demonstrate_embeddings()
