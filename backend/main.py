import os
from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import traceback
from rag_service import rag_service
from vector_store import vector_store

# Logging setup with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NirvahaAPI")

app = FastAPI(
    title="Nirvaha AI - Phase 1 Minimal RAG",
    description="Reflection-based RAG chatbot with evaluation mode"
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    model_used: str = None
    chunk_count: int = None

class EvaluationResponse(BaseModel):
    user_input: str
    baseline: str
    rag: str
    baseline_model: str
    rag_model: str
    chunk_count: int

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Nirvaha AI Sanctuary API - Phase 1 Minimal RAG",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat [POST] - Get a reflection response",
            "evaluate": "/evaluate [POST] - Compare RAG vs baseline responses"
        }
    }

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize vector store and index dataset on startup."""
    logger.info("=" * 70)
    logger.info("🚀 NIRVAHA BACKEND STARTUP")
    logger.info("=" * 70)
    
    # Use absolute path relative to the backend directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", "reflections.txt")
    
    logger.info(f"Looking for dataset at: {data_path}")
    
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            if lines:
                logger.info(f"✓ Dataset loaded: {len(lines)} reflection chunks")
                vector_store.add_texts(lines)
                logger.info(f"✓ All chunks indexed into ChromaDB")
                logger.info(f"✓ Vector store ready for retrieval")
            else:
                logger.warning("⚠ Dataset file is empty")
        except Exception as e:
            logger.error(f"✗ Failed to initialize vector store: {e}")
            traceback.print_exc()
            raise
    else:
        logger.error(f"✗ Dataset file not found at {data_path}")
        raise FileNotFoundError(f"Data file required: {data_path}")
    
    logger.info("=" * 70)
    logger.info("✓ STARTUP COMPLETE - System Ready")
    logger.info("=" * 70 + "\n")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    
    Accepts user message, retrieves context, generates reflection response.
    Returns response with metadata.
    """
    message = request.message.strip() if request.message else ""
    
    if not message:
        logger.warning("Empty message received")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    logger.info(f"\n📨 Incoming chat request: {message[:80]}...")
    
    try:
        result = rag_service.get_reflection(message)
        
        return ChatResponse(
            response=result["response"],
            model_used=result["model_used"],
            chunk_count=result["chunk_count"]
        )
    
    except Exception as e:
        logger.error(f"✗ Chat generation failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate reflection: {str(e)}"
        )

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: ChatRequest):
    """
    Evaluation endpoint: Compare RAG response vs baseline.
    
    Demonstrates that context retrieval improves response quality.
    Returns both responses for comparison.
    """
    message = request.message.strip() if request.message else ""
    
    if not message:
        logger.warning("Empty message received for evaluation")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    logger.info(f"\n🔬 Incoming evaluation request: {message[:80]}...")
    
    try:
        result = rag_service.compare_responses(message)
        
        return EvaluationResponse(
            user_input=result["user_input"],
            baseline=result["baseline"],
            rag=result["rag"],
            baseline_model=result["baseline_model"],
            rag_model=result["rag_model"],
            chunk_count=result["chunk_count"]
        )
    
    except Exception as e:
        logger.error(f"✗ Evaluation failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run evaluation: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Quick health check endpoint."""
    try:
        # Verify vector store is accessible
        test_results = vector_store.search("test", n_results=1)
        return {
            "status": "healthy",
            "vector_store": "connected",
            "chunks_in_store": len(test_results) if test_results else 0
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
