import os
import logging
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("NirvahaEmbeddings")

class EmbeddingsManager:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """Initialize local HuggingFace embeddings via sentence-transformers."""
        try:
            logger.info(f"Loading local embedding model: {model_name}...")
            self.model = SentenceTransformer(model_name)
            logger.info("Local embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def get_embedding(self, text: str):
        """Generate embedding for a single text string."""
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def get_embeddings_batch(self, texts: list):
        """Generate embeddings for a list of text strings."""
        try:
            return self.model.encode(texts).tolist()
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise

embeddings_manager = EmbeddingsManager()
