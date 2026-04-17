import os
import openai
from groq import Groq
from dotenv import load_dotenv
import logging
from vector_store import vector_store

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NirvahaRAG")

SYSTEM_INSTRUCTION = """You are Nirvaha Companion, a calm and perceptive reflection guide.

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

USE THESE PATTERNS:
- "It can sometimes..."
- "It often..."
- "At times..."
- "In some situations..."
"""

class RAGService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.openai_model = "gpt-4o-mini"
        self.groq_model = "llama-3.1-8b-instant"

    def _build_rag_prompt(self, user_input: str, chunks: list) -> str:
        """Build the final prompt with context chunks."""
        context_lines = []
        if chunks:
            for i, chunk in enumerate(chunks[:5], 1):  # Max 5 chunks
                context_lines.append(f"* {chunk}")
        
        context_text = "\n".join(context_lines) if context_lines else "(No relevant context found)"
        
        prompt = f"""Relevant context:

{context_text}

User message:
"{user_input}"

Instruction:
Generate a calm, concise reflection response. Use 2-4 sentences only. Follow the system guidelines strictly."""
        
        return prompt

    def _call_llm(self, prompt: str, model_name: str) -> tuple:
        """Call an LLM and return response + actual model used."""
        try:
            if model_name == "openai":
                logger.info(f"Calling OpenAI ({self.openai_model})...")
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                content = response.choices[0].message.content.strip()
                logger.info(f"✓ OpenAI response generated successfully")
                return content, "openai"
            
            elif model_name == "groq":
                logger.info(f"Calling Groq ({self.groq_model})...")
                response = self.groq_client.chat.completions.create(
                    model=self.groq_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                content = response.choices[0].message.content.strip()
                logger.info(f"✓ Groq response generated successfully")
                return content, "groq"
        
        except Exception as e:
            logger.error(f"LLM call failed ({model_name}): {str(e)}")
            raise

    def get_reflection(self, user_input: str) -> dict:
        """
        Generate a reflection response using RAG pipeline.
        
        Returns:
            dict with 'response' (str), 'model_used' (str), 'chunks_used' (list)
        """
        logger.info(f"\n{'='*60}")
        logger.info("START: RAG Reflection Generation")
        logger.info(f"User Input: {user_input}")
        logger.info(f"{'='*60}")
        
        chunks = []
        
        # 1. RETRIEVAL: Fetch relevant chunks from vector store
        try:
            logger.info("Step 1: Retrieving context chunks from vector store...")
            chunks = vector_store.search(user_input, n_results=5)
            if chunks:
                logger.info(f"✓ Retrieved {len(chunks)} chunks:")
                for i, chunk in enumerate(chunks, 1):
                    logger.info(f"  [{i}] {chunk[:80]}...")
            else:
                logger.warning("⚠ No chunks found in vector store - will proceed without context")
        except Exception as e:
            logger.error(f"Retrieval failed: {e}. Attempting to proceed without context.")
            chunks = []

        # 2. PROMPT CONSTRUCTION
        logger.info("Step 2: Constructing prompt with retrieved context...")
        prompt = self._build_rag_prompt(user_input, chunks)
        logger.info(f"Final Prompt:\n{prompt}\n")

        # 3. LLM EXECUTION WITH FALLBACK
        response = None
        model_used = None
        
        # Try OpenAI first
        try:
            response, model_used = self._call_llm(prompt, "openai")
        except Exception as e:
            logger.warning(f"OpenAI failed, attempting fallback to Groq...")
            try:
                response, model_used = self._call_llm(prompt, "groq")
            except Exception as groq_error:
                logger.error(f"Both OpenAI and Groq failed!")
                logger.error(f"OpenAI error: {e}")
                logger.error(f"Groq error: {groq_error}")
                raise Exception("All LLM providers failed. Cannot generate response.") from groq_error

        # 4. RESPONSE VALIDATION
        if not response:
            raise Exception("LLM returned empty response")
        
        logger.info(f"Final Response ({model_used}): {response}")
        logger.info(f"{'='*60}")
        logger.info("END: RAG Reflection Generation\n")
        
        return {
            "response": response,
            "model_used": model_used,
            "chunks_used": chunks,
            "chunk_count": len(chunks)
        }

    def compare_responses(self, user_input: str) -> dict:
        """
        EVALUATION MODE: Compare RAG response vs baseline response.
        
        Returns:
            dict with 'baseline' (str), 'rag' (str), 'baseline_model' (str), 'rag_model' (str)
        """
        logger.info(f"\n{'='*70}")
        logger.info("EVALUATION MODE: Comparing RAG vs Baseline Responses")
        logger.info(f"User Input: {user_input}")
        logger.info(f"{'='*70}")
        
        # BASELINE: Response WITHOUT retrieval (direct LLM call)
        logger.info("\n--- BASELINE: Direct LLM Response (No Retrieval) ---")
        baseline_prompt = f"""User message:
"{user_input}"

Instruction:
Generate a calm, concise reflection response. Use 2-4 sentences only. Follow the system guidelines strictly."""
        
        baseline_response = None
        baseline_model = None
        try:
            baseline_response, baseline_model = self._call_llm(baseline_prompt, "openai")
        except Exception as e:
            logger.warning("Baseline OpenAI failed, trying Groq...")
            try:
                baseline_response, baseline_model = self._call_llm(baseline_prompt, "groq")
            except Exception as ge:
                logger.error(f"Baseline generation failed: {ge}")
                baseline_response = "Baseline generation failed"
                baseline_model = "error"
        
        logger.info(f"Baseline Response ({baseline_model}): {baseline_response}")
        
        # RAG: Response WITH retrieval
        logger.info("\n--- RAG: Retrieved Context + LLM Response ---")
        rag_result = self.get_reflection(user_input)
        rag_response = rag_result["response"]
        rag_model = rag_result["model_used"]
        
        result = {
            "user_input": user_input,
            "baseline": baseline_response,
            "baseline_model": baseline_model,
            "rag": rag_response,
            "rag_model": rag_model,
            "chunks_retrieved": rag_result["chunks_used"],
            "chunk_count": rag_result["chunk_count"],
            "evaluation_summary": f"Baseline ({baseline_model}): {baseline_response[:100]}... | RAG ({rag_model}): {rag_response[:100]}..."
        }
        
        logger.info(f"\n{'='*70}")
        logger.info("EVALUATION COMPLETE")
        logger.info(f"Summary: {result['evaluation_summary']}")
        logger.info(f"{'='*70}\n")
        
        return result

rag_service = RAGService()
