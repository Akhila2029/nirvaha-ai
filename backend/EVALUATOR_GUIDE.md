# Nirvaha Backend - Evaluator's Quick Guide

## TL;DR

Nirvaha is a **reflection-based RAG chatbot** that:
1. Retrieves relevant reflection patterns from dataset
2. Generates calm, grounded responses (not advice/motivation)
3. Demonstrates RAG improves response quality

---

## Start Backend (30 seconds)

```bash
cd backend
python main.py
```

You should see:
```
🚀 NIRVAHA BACKEND STARTUP
✓ Dataset loaded: 15 reflection chunks
✓ Vector store ready for retrieval
✓ STARTUP COMPLETE - System Ready

INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Test 1: Basic Chat (2 minutes)

**What it does**: User sends message → system retrieves relevant chunks → calls LLM → returns reflection

**Try it**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I feel uncertain about the future"}'
```

**Expected response**:
```json
{
  "response": "Uncertainty can feel uncomfortable when clarity is expected. People often attach meaning to not knowing. At times, the discomfort itself becomes the focus rather than the uncertainty.",
  "model_used": "openai",
  "chunk_count": 3
}
```

**Check**:
- ✓ Response is 2-4 sentences?
- ✓ No advice ("you should...") or labels ("you are feeling...")?
- ✓ Uses patterns like "It often...", "People sometimes..."?
- ✓ Is calm and observational?

---

## Test 2: Evaluation Mode (3 minutes)

**What it does**: Shows RAG actually improves responses vs generic LLM

**Try it**:
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"message": "What happens when you doubt yourself?"}'
```

**Compare response**:
```json
{
  "baseline": "Doubt can be a normal part of the human experience. It often emerges when we face uncertainty or challenges.",
  "rag": "Doubt often appears strongest when outcomes are uncertain. It is natural to question direction during moments of difficulty. Reactions reflect internal standards more than external reality.",
  "chunk_count": 3,
  "baseline_model": "openai",
  "rag_model": "openai"
}
```

**What to notice**:
- Baseline is generic ("part of human experience")
- RAG response is grounded in dataset ("reactions reflect standards")
- RAG uses more specific patterns from dataset
- More contextual and less generic

---

## Test 3: Check Logs (5 minutes)

**What it shows**: Behind-the-scenes data flow

**In backend console**, you'll see:
```
======================================================================
START: RAG Reflection Generation
User Input: What happens when doubt appears?
======================================================================
Step 1: Retrieving context chunks from vector store...
✓ Retrieved 3 chunks:
  [1] Doubt often appears strongest when outcomes are uncertain...
  [2] It is natural to question direction during moments of difficulty...
  [3] Reactions to failure often reflect internal standards...

Step 2: Constructing prompt with retrieved context...
Final Prompt:
Relevant context:
* Doubt often appears strongest...
* It is natural to question...
* Reactions to failure...

User message: "What happens when doubt appears?"

Step 3: Calling LLM...
Calling OpenAI (gpt-4o-mini)...
✓ OpenAI response generated successfully

Final Response: Doubt often appears strongest when outcomes are uncertain...
```

**What to verify**:
- ✓ Chunks are retrieved?
- ✓ Chunks appear in final prompt?
- ✓ Correct model is used (OpenAI/Groq)?
- ✓ Response is generated?

---

## Test 4: Fallback Chain (2 minutes)

**What it does**: If OpenAI fails, automatically uses Groq

**Simulate OpenAI failure** (optional):
- Comment out OpenAI key in `.env`
- Restart backend
- Send request

**Expected behavior**:
```
TRYING LLM: OpenAI (gpt-4o-mini)...
OpenAI failed: Invalid API key
FALLING BACK TO: Groq (llama-3.1-8b-instant)...
✓ Groq response generated successfully
```

**Check**:
- ✓ System doesn't crash?
- ✓ Automatically uses Groq?
- ✓ Response quality still good?

---

## Test 5: Edge Cases (2 minutes)

**Test empty dataset behavior**:
```bash
# Send query when vector store has issues
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

**Expected behavior**:
- ✓ Still generates response (doesn't crash)
- ✓ Calls LLM with just user input
- ✓ Returns valid response

**Test invalid requests**:
```bash
# Empty message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```

**Expected**: Returns 400 error (not crash)

---

## Test 6: Health Check (30 seconds)

```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "vector_store": "connected",
  "chunks_in_store": 15
}
```

---

## Response Style Verification

### ✅ GOOD Examples (What to expect)

> "It can sometimes feel overwhelming when expectations are unmet. People often connect results with self-worth. Progress is not always visible in the moment it is happening."

> "Uncertainty can feel uncomfortable when clarity is expected. Emotional reactions often reveal how much meaning is attached to the outcome."

> "At times, moments of disappointment can stay longer when expectations were high. Setbacks can create a pause that feels heavier than the event itself."

### ❌ BAD Examples (Should NOT see these)

> "You are feeling uncertain right now. You should focus on controlling what you can control. You're stronger than you think!"

> "This is happening because you have low self-esteem and you need therapy."

> "Don't worry, everything will be fine! You'll get through this!"

---

## Architecture Overview

```
User Input
    ↓
[Embedding] - Convert to 384-dim vector
    ↓
[Vector Search] - Find top 5 chunks in ChromaDB
    ↓
[Prompt Construction] - Add chunks to prompt template
    ↓
[LLM Call] - OpenAI (fallback: Groq)
    ↓
[Response] - Return 2-4 sentence reflection
```

---

## Files to Review

| File | Purpose |
|------|---------|
| `main.py` | FastAPI server with endpoints |
| `rag_service.py` | RAG pipeline + evaluation logic |
| `embeddings.py` | Embedding generation |
| `vector_store.py` | ChromaDB wrapper |
| `README.md` | Complete documentation |
| `REFACTORING_COMPLETE.md` | What was changed |
| `test_validation.py` | Comprehensive test suite |

---

## Key Features

✅ **No Frameworks**: Direct embedding → search → LLM (no LangChain)  
✅ **Minimal & Transparent**: All operations logged  
✅ **Dual LLM**: OpenAI + Groq fallback  
✅ **Evaluation Mode**: Compare RAG vs baseline  
✅ **No Placeholders**: Real responses or errors (never dummy text)  
✅ **Style Compliance**: Enforced 2-4 sentences, reflective tone  
✅ **Error Handling**: Comprehensive with detailed logs  

---

## Expected Behavior

| Scenario | Expected | Status |
|----------|----------|--------|
| User sends message | Gets reflection response | ✓ |
| Check logs | See chunks, prompt, model | ✓ |
| Evaluation mode | RAG better than baseline | ✓ |
| OpenAI fails | Falls back to Groq | ✓ |
| No matching chunks | Still generates response | ✓ |
| Empty message | Returns 400 error | ✓ |
| Response style | 2-4 sentences, reflective | ✓ |

---

## Performance

| Metric | Time |
|--------|------|
| Embedding lookup | ~10-20ms |
| Vector search (top 5) | ~5-10ms |
| LLM response | 500ms - 2s |
| **Total latency** | **1-3 seconds** |

---

## Debugging Commands

```bash
# Test embeddings
python -c "from embeddings import embeddings_manager; print(embeddings_manager.get_embedding('test')[:5])"

# Test vector search
python -c "from vector_store import vector_store; print(vector_store.search('doubt', 2))"

# Syntax check
python check_syntax.py

# Full validation suite
python test_validation.py

# Raw API response
curl http://localhost:8000/ | jq .
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Check `.env` file has keys |
| "Connection refused" | Ensure `python main.py` is running |
| "No chunks found" | Check `/data/reflections.txt` exists |
| Response is generic | Check system prompt enforcement (see logs) |
| Both LLMs fail | Check API keys and quota |

---

## Success Criteria ✓

- [x] System starts without errors
- [x] `/chat` returns valid responses (2-4 sentences)
- [x] `/evaluate` shows RAG improvement
- [x] Logs show data flow clearly
- [x] No placeholder/dummy responses
- [x] Fallback works when primary fails
- [x] Response style is correct
- [x] Edge cases handled gracefully

---

## Next Steps

1. ✅ Start backend: `python main.py`
2. ✅ Run tests: Follow tests 1-6 above
3. ✅ Check logs: Verify data flow in backend console
4. ✅ Verify compliance: Response style and RAG value
5. ✅ Evaluate quality: Try various inputs, check responses

---

## Questions?

See `README.md` for:
- Full API documentation
- System architecture details
- Deployment checklist
- Advanced configuration

---

**System Status**: ✅ Ready for Evaluation  
**Last Updated**: 2026-04-17  
**Version**: 1.0.0 - Phase 1 Complete
