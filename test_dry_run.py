"""
Test script for AI Customer Service System
Performs dry run tests of the core functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the services directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / "services"))

def test_vector_store_service():
    """Test the Vector Store Service"""
    print("Testing Vector Store Service...")
    
    try:
        from services.vector_store_service import VectorStoreService
        
        # Initialize the service
        vss = VectorStoreService(persist_directory="./test_chroma_db")
        print("√ VectorStoreService initialized successfully")
        
        # Test similarity search with a dummy query
        results = vss.similarity_search("test_kb", "dummy query", k=2)
        print(f"√ Similarity search completed, found {len(results)} results")
        
        return True
    except Exception as e:
        print(f"x Error in Vector Store Service test: {str(e)}")
        return False

def test_document_parser():
    """Test the Document Parser Service"""
    print("\nTesting Document Parser Service...")
    
    try:
        from services.document_parser import DocumentParser
        
        # Initialize the service
        parser = DocumentParser()
        print("√ DocumentParser initialized successfully")
        
        # Test with a dummy txt file
        test_file = "./test_sample.txt"
        
        # Create a sample text file for testing
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("This is a test document for the AI Customer Service system.\nIt contains sample content for testing purposes.")
        
        # Parse the test file
        content = parser.parse_document(test_file)
        print(f"√ Document parsed successfully, content length: {len(content)} characters")
        
        # Clean up test file
        os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"x Error in Document Parser test: {str(e)}")
        return False

def test_web_scraper():
    """Test the Web Scraper Service"""
    print("\nTesting Web Scraper Service...")
    
    try:
        from services.web_scraper import WebScraper
        
        # Initialize the service
        scraper = WebScraper(delay=0.1)  # Short delay for testing
        print("√ WebScraper initialized successfully")
        
        # Test with a simple HTML content instead of making actual requests
        sample_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <main>
                    <h1>Test Content</h1>
                    <p>This is a sample content for testing the web scraper.</p>
                    <p>It includes multiple paragraphs to verify extraction.</p>
                </main>
            </body>
        </html>
        """
        
        content = scraper.extract_content(sample_html)
        print(f"√ Content extracted successfully, length: {len(content)} characters")
        
        return True
    except Exception as e:
        print(f"x Error in Web Scraper test: {str(e)}")
        return False

def test_llm_provider():
    """Test the LLM Provider Factory"""
    print("\nTesting LLM Provider Factory...")
    
    try:
        from services.llm_provider import LLMProviderFactory
        
        # Initialize the factory
        factory = LLMProviderFactory()
        print("√ LLMProviderFactory initialized successfully")
        
        # List available providers
        providers = factory.list_available_providers()
        print(f"√ Available providers: {providers}")
        
        return True
    except Exception as e:
        print(f"x Error in LLM Provider test: {str(e)}")
        return False

def test_api_endpoints():
    """Test the API endpoints by importing main module"""
    print("\nTesting API Module...")
    
    try:
        from api.main import app
        print("√ API module imported successfully")
        print(f"√ App title: {app.title}")
        
        return True
    except Exception as e:
        print(f"✗ Error in API test: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("="*60)
    print("AI CUSTOMER SERVICE - DRY RUN TESTS")
    print("="*60)
    
    tests = [
        ("Vector Store Service", test_vector_store_service),
        ("Document Parser", test_document_parser),
        ("Web Scraper", test_web_scraper),
        ("LLM Provider", test_llm_provider),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-"*60)
    print(f"Total: {len(results)}, Passed: {passed}, Failed: {len(results)-passed}")
    
    if passed == len(results):
        print("\n*** ALL TESTS PASSED! The system is ready for deployment.")
        return True
    else:
        print(f"\n*** {len(results)-passed} TEST(S) FAILED! Please fix issues before deployment.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)