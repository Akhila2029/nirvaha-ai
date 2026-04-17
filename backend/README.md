# Nirvaha Backend - Phase 1 Implementation Guide

## Overview

Nirvaha is a **Reflection-Based RAG Chatbot** that uses retrieval-augmented generation to provide calm, perceptive reflections on human experiences. The system is built with a minimal, transparent architecture (no frameworks like LangChain) for easy debugging and evaluation.

---

## System Architecture

### Components

1. **Embeddings Manager** (`embeddings.py`)
   - Uses `sentence-transformers` (all-MiniLM-L6-v2)
   - Generates 384-dimensional embeddings
   - Handles both single and batch encoding

2. **Vector Store** (`vector_store.py`)
   - ChromaDB persistent storage
   - Semantic similarity search
   - Returns top N relevant chunks

3. **RAG Service** (`rag_service.py`)
   - Orchestrates retrieval + LLM pipeline
   - Manages OpenAI/Groq fallback logic
   - Provides evaluation mode

4. **FastAPI Server** (`main.py`)
   - REST API endpoints
   - Request validation
   - Logging and error handling

### Data Flow

```
User Input
    ↓
Generate Embedding (384-dim)
    ↓
Vector Search (retrieve top 5 chunks)
    ↓
Construct Prompt with Context
    ↓
Call LLM (OpenAI → Groq fallback)
    ↓
Return Reflection + Metadata
```

---

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
OPENAI_API_KEY=sk-proj-...your-key-here...
GROQ_API_KEY=gsk_...your-key-here...
```

Get API keys from:
- OpenAI: https://platform.openai.com/account/api-keys
- Groq: https://console.groq.com

### Data File

- **Location**: `/data/reflections.txt`
- **Format**: One reflection statement per line
- **Example**:
  ```
  Failure can sometimes feel more personal than it actually is.
  People often interpret outcomes as reflections of their abilities rather than circumstances.
  Moments of disappointment can stay longer when expectations were high.
  ```

---

## API Endpoints

### 1. POST `/chat` - Get Reflection Response

**Request**:
```json
{
  "message": "I'm feeling overwhelmed by uncertainty"
}
```

**Response**:
```json
{
  "response": "It can sometimes feel difficult when clarity is expected. Uncertainty often reveals how attached we are to knowing the outcome.",
  "model_used": "openai",
  "chunk_count": 3
}
```

**Status Codes**:
- `200`: Success
- `400`: Empty or invalid message
- `500`: LLM generation failed

---

### 2. POST `/evaluate` - Compare RAG vs Baseline

Demonstrates that context retrieval improves response quality.

**Request**:
```json
{
  "message": "What happens when effort and results don't align?"
}
```

**Response**:
```json
{
  "user_input": "What happens when effort and results don't align?",
  "baseline": "Effort-result misalignment can feel frustrating. It often reveals gaps between expectations and outcomes.",
  "rag": "Effort-result misalignment can feel frustrating. The context shows that frustration arises when effort and results do not align. Progress is not always visible in the moment it is happening.",
  "baseline_model": "openai",
  "rag_model": "openai",
  "chunk_count": 2
}
```

---

### 3. GET `/health` - System Health Check

**Response**:
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "chunks_in_store": 15
}
```

---

### 4. GET `/` - API Info

Returns API endpoints and status.

---

## Response Style Guidelines

### ✅ MUST DO

- Use 2-4 sentences only
- Be calm, neutral, observational
- Acknowledge experience indirectly
- Mention general human patterns
- Offer soft reflective observation

### ❌ MUST AVOID

- Emotional labeling ("You are feeling...")
- Direct advice ("You should...")
- Cause explanations ("This is because...")
- Motivational language
- Philosophical tone

### ✅ Example Patterns

```
"It can sometimes..."
"It often..."
"At times..."
"In some situations..."
"People often..."
"Moments of... can..."
```

### ✅ Good Response Example

> "Uncertainty can feel uncomfortable when clarity is expected. People often interpret outcomes as reflections of their abilities rather than circumstances. Expectations can quietly shape how experiences are interpreted."

### ❌ Bad Response Example

> "You're feeling uncertain and overwhelmed. Don't worry, you should focus on controlling what you can. You're stronger than you think!"

---

## System Prompt

```
You are Nirvaha Companion, a calm and perceptive reflection guide.

You do not diagnose, advise, or explain.

You only offer short, grounded observations about human experience.

Keep responses between 2–4 sentences.

Avoid labeling the user directly.

Use neutral, modern, simple language.

STRICTLY AVOID:
- "You are feeling..."
- "You are experiencing..."
- Any emotional labeling
- Advice ("you should")
- Explanations of cause ("this is because")
- Motivational language
- Philosophical or spiritual tone
```

---

## Running the Backend

### Prerequisites

```bash
pip install -r requirements.txt
```

### Startup

```bash
python main.py
```

Expected output:
```
======================================================================
🚀 NIRVAHA BACKEND STARTUP
======================================================================
Looking for dataset at: ../data/reflections.txt
✓ Dataset loaded: 15 reflection chunks
✓ All chunks indexed into ChromaDB
✓ Vector store ready for retrieval
======================================================================
✓ STARTUP COMPLETE - System Ready
======================================================================

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Testing

```bash
python test_validation.py
```

This runs:
1. Embedding generation test
2. Vector store operations test
3. RAG pipeline test
4. Evaluation mode test
5. Edge case handling test

---

## Debugging

### View Detailed Logs

The system logs everything:
- User input
- Retrieved chunks with context
- Final prompt sent to LLM
- Model selection (OpenAI/Groq)
- Response generation success/failure
- Error traces

### Example Log Output

```
======================================================================
START: RAG Reflection Generation
User Input: What happens when you doubt yourself?
======================================================================
Step 1: Retrieving context chunks from vector store...
✓ Retrieved 3 chunks:
  [1] Doubt often appears strongest when outcomes are uncertain...
  [2] It is natural to question direction during moments of difficulty...
  [3] Reactions to failure often reflect internal standards more than...

Step 2: Constructing prompt with retrieved context...

Step 3: Calling LLM...
Calling OpenAI (gpt-4o-mini)...
✓ OpenAI response generated successfully

Final Response: It can sometimes feel overwhelming to question your own judgment...
```

---

## Evaluation Mode Usage

### Purpose

Demonstrate that RAG (Retrieval-Augmented Generation) improves response quality by:
1. Generating a baseline response (without context)
2. Generating a RAG response (with retrieved context)
3. Comparing both responses

### Example

```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"message": "How do you handle setbacks?"}'
```

### Response Interpretation

- **Baseline**: Generic response based only on the question
- **RAG**: More grounded, contextual response using dataset
- **Chunks Retrieved**: Number of dataset references used
- **Model Used**: Which LLM provider generated the response

---

## Edge Cases Handled

| Case | Behavior |
|------|----------|
| Empty message | Returns 400 error |
| No matching chunks | Calls LLM with just user input |
| OpenAI fails | Automatically falls back to Groq |
| Groq fails | Returns 500 error with details |
| Empty dataset | Still responds (no chunks available) |
| Invalid embeddings | Caught and logged, uses fallback |

---

## LLM Models

### Primary: OpenAI

- **Model**: gpt-4o-mini
- **Context Window**: 128,000 tokens
- **Temperature**: 0.7
- **Max Tokens**: 150

### Fallback: Groq

- **Model**: llama-3.1-8b-instant
- **Speed**: Ultra-fast inference
- **Temperature**: 0.7
- **Max Tokens**: 150

---

## Vector Store Details

### ChromaDB Configuration

- **Persistence**: `backend/db/chroma_db/`
- **Collection**: "reflections"
- **Embedding Dimension**: 384 (all-MiniLM-L6-v2)
- **Similarity Metric**: Cosine distance

### Adding New Data

1. Add lines to `/data/reflections.txt`
2. Restart the backend
3. Startup event will re-index all chunks

---

## Performance

- **Embedding Generation**: ~1-2ms per chunk
- **Vector Search**: ~10-20ms for top 5
- **LLM Response Time**: 500ms - 2s (depends on OpenAI/Groq)
- **Total Request Latency**: ~1-3 seconds

---

## Troubleshooting

### Issue: "API key not found"

**Solution**: 
1. Create `.env` file with your keys
2. Restart the backend
3. Check keys are correct format

### Issue: "No chunks found"

**Solution**:
1. Verify `/data/reflections.txt` exists
2. Restart backend (startup event indexes data)
3. Check logs for indexing errors

### Issue: "Both LLM providers failed"

**Solution**:
1. Verify API keys are valid
2. Check internet connection
3. Verify OpenAI/Groq quotas not exceeded
4. Check logs for specific error messages

### Issue: "Response is too short/long"

**Solution**:
1. Check system prompt is enforced correctly
2. LLM may ignore constraints; adjust temperature
3. Review logs to see actual LLM output

---

## Deployment Checklist

- [ ] `.env` file created with valid API keys
- [ ] `/data/reflections.txt` populated with reflection statements
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Syntax check: `python -m py_compile main.py rag_service.py`
- [ ] Validation tests pass: `python test_validation.py`
- [ ] Backend starts without errors: `python main.py`
- [ ] Can hit `/health` endpoint successfully
- [ ] `/chat` endpoint returns valid responses
- [ ] `/evaluate` endpoint shows RAG improvement
- [ ] Logs are clear and verbose

---

## Example Conversations

### Example 1: Setback

**Input**: "I failed an important exam"

**Baseline** (no context):
> "Failing an exam can feel like a significant setback. It's natural to feel disappointed when results don't match your expectations."

**RAG** (with context):
> "Failure can sometimes feel more personal than it actually is. Reactions to failure often reflect internal standards more than external reality. Setbacks can create a pause that feels heavier than the event itself."

---

### Example 2: Uncertainty

**Input**: "I'm not sure about my career path"

**Baseline** (no context):
> "Career uncertainty is something many people experience. It's okay to feel uncertain about the future."

**RAG** (with context):
> "Uncertainty can feel uncomfortable when clarity is expected. It is natural to question direction during moments of difficulty. Expectations can quietly shape how experiences are interpreted."

---

## Future Enhancements

- [ ] Add more dataset sources
- [ ] Fine-tune embeddings for reflection domain
- [ ] Add conversation history/context
- [ ] Implement response quality scoring
- [ ] Add A/B testing framework
- [ ] Multi-language support

---

## License & Attribution

Built for Phase 1 PRD evaluation. Uses open-source components:
- FastAPI
- ChromaDB
- Sentence-Transformers
- OpenAI/Groq APIs

---

## Support

For issues or questions:
1. Check logs for detailed error messages
2. Review troubleshooting section above
3. Validate system with `test_validation.py`
4. Check API key configuration

---

**Version**: 1.0.0  
**Status**: Phase 1 - Ready for Evaluation  
**Last Updated**: 2026-04-17
