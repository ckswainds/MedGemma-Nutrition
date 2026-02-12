# """Test script for RAG Engine module."""

# import sys
# import logging

# logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# print("=" * 60)
# print("Testing RAG Engine Initialization")
# print("=" * 60)

# try:
#     from modules.rag_engine import get_rag_engine, retrieve_context, search_guidelines
    
#     print("\n[STEP 1] Getting RAG Engine Instance...")
#     engine = get_rag_engine()
    
#     if engine:
#         print("✅ RAG Engine instance created successfully")
    
#     print("\n[STEP 2] Checking Vector Store Status...")
#     if engine.vector_store is not None:
#         print("✅ Vector store initialized")
#     else:
#         print("⚠️  Vector store not available (may require Ollama running)")
    
#     print("\n[STEP 3] Checking Embeddings Status...")
#     if engine.embeddings is not None:
#         print("✅ Embeddings initialized")
#     else:
#         print("⚠️  Embeddings not available (requires Ollama)")
    
#     print("\n[STEP 4] Testing Retrieve Context Function...")
#     test_query = "diabetes nutrition"
#     context, docs = retrieve_context(test_query)
#     print(f"✅ retrieve_context() executed successfully")
#     print(f"   - Query: '{test_query}'")
#     print(f"   - Context length: {len(context)} characters")
#     print(f"   - Documents retrieved: {len(docs)}")
    
#     print("\n[STEP 5] Testing Search Guidelines Function...")
#     search_result = search_guidelines("hypertension diet")
#     print(f"✅ search_guidelines() executed successfully")
#     print(f"   - Result length: {len(search_result)} characters")
    
#     print("\n[STEP 6] Testing Fallback Guidance...")
#     print("Sample guidance for different conditions:")
#     for condition in ["diabetes", "hypertension", "anemia", "pcos", "kidney"]:
#         result = search_guidelines(f"{condition} nutrition")
#         if result:
#             preview = result.split('\n')[0][:50]
#             print(f"   ✅ {condition}: {preview}...")
    
#     print("\n" + "=" * 60)
#     print("✅ RAG ENGINE TEST COMPLETED SUCCESSFULLY!")
#     print("=" * 60)
    
# except ImportError as e:
#     print(f"\n❌ Import Error: {e}")
#     print("   Make sure all required packages are installed")
    
# except Exception as e:
#     print(f"\n❌ Error: {e}")
#     import traceback
#     traceback.print_exc()
from modules.rag_engine import RAGEngine,get_rag_engine
# rag=RAGEngine()
# serialized_context, retrieved_docs=rag.retrieve_context("can i eat apples")
# print(len(serialized_context),len(retrieved_docs))
get_rag_engine(True)