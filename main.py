"""
Main entry point for the AI Customer Service system.
This is a simplified version for demonstration and testing.
"""
import os
import sys
from rag.query_engine import QueryEngine
from models.factory import get_model

def main():
    """
    Main function for testing the RAG system.
    """
    # Get user question from command line or use default
    if len(sys.argv) > 1:
        user_question = " ".join(sys.argv[1:])
    else:
        user_question = "What is your return policy?"
    
    print(f"User question: {user_question}")
    
    # Initialize query engine
    query_engine = QueryEngine()
    
    # Get relevant context
    results = query_engine.query(user_question)
    context = "\n".join(results["context"]["documents"][0]) if results["context"]["documents"][0] else ""
    
    print(f"Retrieved context: {context[:200]}...")
    
    # Get model and generate response
    model = get_model()
    response = model.generate(user_question, context)
    
    print(f"AI response: {response}")

if __name__ == "__main__":
    main()