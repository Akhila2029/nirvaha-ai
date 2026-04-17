import os
import chromadb
from chromadb.config import Settings
from embeddings import embeddings_manager

class VectorStoreManager:
    def __init__(self, persist_directory="db/chroma_db"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection_name = "reflections"
        # Get or create collection
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_texts(self, texts: list, metadatas: list = None):
        """Add texts to the collection. Auto-generates IDs and embeddings."""
        if not texts:
            return
            
        ids = [f"id_{i}" for i in range(len(texts))]
        embeddings = embeddings_manager.get_embeddings_batch(texts)
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas or [None] * len(texts),
            ids=ids
        )

    def search(self, query_text: str, n_results: int = 3):
        """Perform similarity search and return texts."""
        query_embedding = embeddings_manager.get_embedding(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        # Extract the text content from results
        return results['documents'][0] if results['documents'] else []

vector_store = VectorStoreManager()
