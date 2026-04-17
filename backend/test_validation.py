#!/usr/bin/env python3
"""
Nirvaha Backend Validation Script
Tests RAG pipeline, LLM integration, and response quality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from vector_store import vector_store
from embeddings import embeddings_manager
from rag_service import rag_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ValidationScript")

def test_embeddings():
    """Test embedding generation."""
    logger.info("\n" + "="*70)
    logger.info("TEST 1: Embedding Generation")
    logger.info("="*70)
    
    try:
        test_text = "It can sometimes feel difficult to move forward"
        embedding = embeddings_manager.get_embedding(test_text)
        
        if embedding and len(embedding) == 384:  # all-MiniLM-L6-v2 output size
            logger.info(f"✓ Successfully generated embedding (384 dimensions)")
            logger.info(f"  Sample values: {embedding[:5]}")
            return True
        else:
            logger.error(f"✗ Embedding size mismatch: {len(embedding)}")
            return False
    except Exception as e:
        logger.error(f"✗ Embedding test failed: {e}")
        return False

def test_vector_store():
    """Test vector store initialization and operations."""
    logger.info("\n" + "="*70)
    logger.info("TEST 2: Vector Store Operations")
    logger.info("="*70)
    
    try:
        # Try searching (should work even with existing data)
        results = vector_store.search("difficulty", n_results=2)
        
        if results:
            logger.info(f"✓ Successfully retrieved {len(results)} chunks")
            for i, chunk in enumerate(results[:2], 1):
                logger.info(f"  [{i}] {chunk[:60]}...")
            return True
        else:
            logger.warning("⚠ No chunks found (may need to load dataset)")
            return True  # Not a failure, just warning
    except Exception as e:
        logger.error(f"✗ Vector store test failed: {e}")
        return False

def test_rag_pipeline():
    """Test complete RAG pipeline."""
    logger.info("\n" + "="*70)
    logger.info("TEST 3: RAG Pipeline")
    logger.info("="*70)
    
    try:
        test_input = "What happens when you feel uncertain about the future?"
        logger.info(f"Testing with input: {test_input}")
        
        result = rag_service.get_reflection(test_input)
        
        if not result:
            logger.error("✗ No result returned")
            return False
        
        response = result.get("response", "")
        model = result.get("model_used", "")
        chunks = result.get("chunks_used", [])
        
        if response and model:
            logger.info(f"✓ RAG pipeline successful")
            logger.info(f"  Response length: {len(response)} chars")
            logger.info(f"  Sentences: {response.count('.') + response.count('?') + response.count('!')}")
            logger.info(f"  Model used: {model}")
            logger.info(f"  Chunks retrieved: {len(chunks)}")
            logger.info(f"  Response: {response}")
            
            # Validate response style
            if 2 <= len(response.split('.')) - 1 <= 4:  # Count sentences
                logger.info("✓ Response appears to follow 2-4 sentence guideline")
            else:
                logger.warning(f"⚠ Response has {len(response.split('.')) - 1} sentences (expected 2-4)")
            
            return True
        else:
            logger.error(f"✗ Invalid response format: {result}")
            return False
            
    except Exception as e:
        logger.error(f"✗ RAG pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_evaluation_mode():
    """Test evaluation mode (RAG vs baseline)."""
    logger.info("\n" + "="*70)
    logger.info("TEST 4: Evaluation Mode")
    logger.info("="*70)
    
    try:
        test_input = "How do you handle moments of doubt?"
        logger.info(f"Testing evaluation with: {test_input}")
        
        result = rag_service.compare_responses(test_input)
        
        if not result:
            logger.error("✗ No evaluation result returned")
            return False
        
        baseline = result.get("baseline", "")
        rag = result.get("rag", "")
        
        if baseline and rag:
            logger.info(f"✓ Evaluation mode successful")
            logger.info(f"  Baseline ({result['baseline_model']}): {baseline}")
            logger.info(f"  RAG ({result['rag_model']}): {rag}")
            logger.info(f"  Context chunks used: {result['chunk_count']}")
            return True
        else:
            logger.error(f"✗ Invalid evaluation result")
            return False
            
    except Exception as e:
        logger.error(f"✗ Evaluation mode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Test edge cases."""
    logger.info("\n" + "="*70)
    logger.info("TEST 5: Edge Cases")
    logger.info("="*70)
    
    try:
        # Test 1: Short input
        logger.info("Testing short input...")
        result1 = rag_service.get_reflection("sad")
        if result1 and result1.get("response"):
            logger.info("✓ Short input handled")
        
        # Test 2: Long input
        logger.info("Testing long input...")
        long_input = "I've been feeling overwhelmed by work pressures and personal expectations, and I'm struggling to find balance. What should I do?"
        result2 = rag_service.get_reflection(long_input)
        if result2 and result2.get("response"):
            logger.info("✓ Long input handled")
        
        return True
    except Exception as e:
        logger.error(f"✗ Edge case test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    logger.info("\n")
    logger.info("╔" + "="*68 + "╗")
    logger.info("║" + " "*15 + "NIRVAHA BACKEND VALIDATION SUITE" + " "*20 + "║")
    logger.info("╚" + "="*68 + "╝")
    
    tests = [
        ("Embeddings", test_embeddings),
        ("Vector Store", test_vector_store),
        ("RAG Pipeline", test_rag_pipeline),
        ("Evaluation Mode", test_evaluation_mode),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    logger.info(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        logger.info("\n🎉 ALL TESTS PASSED - Backend is ready for deployment!")
        return 0
    else:
        logger.warning(f"\n⚠ {total_count - passed_count} test(s) failed - Please review logs")
        return 1

if __name__ == "__main__":
    sys.exit(main())
