"""
Test script for AI Customer Service System
Validates code structure and imports without making external calls
"""

import os
import sys
import logging
from pathlib import Path

# Add the business directory to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported without errors"""
    logger.info("Testing module imports...")
    
    try:
        from vector_store_service import VectorStoreService
        logger.info("✓ Successfully imported VectorStoreService")
    except ImportError as e:
        logger.error(f"✗ Failed to import VectorStoreService: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error importing VectorStoreService: {e}")
        return False

    try:
        from document_parser import DocumentParser
        logger.info("✓ Successfully imported DocumentParser")
    except ImportError as e:
        logger.error(f"✗ Failed to import DocumentParser: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error importing DocumentParser: {e}")
        return False

    try:
        from web_scraper import WebScraper
        logger.info("✓ Successfully imported WebScraper")
    except ImportError as e:
        logger.error(f"✗ Failed to import WebScraper: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error importing WebScraper: {e}")
        return False

    try:
        from llm_provider import LLMManager, OpenAIProvider, ClaudeProvider, ZhipuAIProvider, DashScopeProvider
        logger.info("✓ Successfully imported LLMProvider modules")
    except ImportError as e:
        logger.error(f"✗ Failed to import LLMProvider modules: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error importing LLMProvider modules: {e}")
        return False

    try:
        from main_service import AICustomerService
        logger.info("✓ Successfully imported AICustomerService")
    except ImportError as e:
        logger.error(f"✗ Failed to import AICustomerService: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Error importing AICustomerService: {e}")
        return False

    return True

def test_instantiation():
    """Test that classes can be instantiated without external dependencies"""
    logger.info("Testing class instantiation...")
    
    try:
        # Test DocumentParser (doesn't need external services)
        from document_parser import DocumentParser
        parser = DocumentParser()
        logger.info("✓ Successfully instantiated DocumentParser")
    except Exception as e:
        logger.error(f"✗ Failed to instantiate DocumentParser: {e}")
        return False

    try:
        # Test WebScraper (doesn't need external services for instantiation)
        from web_scraper import WebScraper
        scraper = WebScraper(timeout=5)  # Short timeout for testing
        logger.info("✓ Successfully instantiated WebScraper")
    except Exception as e:
        logger.error(f"✗ Failed to instantiate WebScraper: {e}")
        return False

    try:
        # Test LLMManager (doesn't need API keys for instantiation)
        from llm_provider import LLMManager
        manager = LLMManager()
        logger.info("✓ Successfully instantiated LLMManager")
    except Exception as e:
        logger.error(f"✗ Failed to instantiate LLMManager: {e}")
        return False

    return True

def test_structure():
    """Test the overall structure of the system"""
    logger.info("Testing system structure...")
    
    try:
        from main_service import AICustomerService
        import os
        
        # Temporarily unset API keys to test initialization without them
        original_keys = {}
        for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ZHIPU_API_KEY", "DASHSCOPE_API_KEY"]:
            original_keys[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
        
        try:
            # Test service initialization without API keys
            service = AICustomerService(config={
                "vector_store_dir": "./test_chroma_db",
                "scraper_timeout": 5,
                "log_level": "WARNING"
            })
            logger.info("✓ Successfully instantiated AICustomerService without API keys")
        finally:
            # Restore original environment variables
            for key, value in original_keys.items():
                if value is not None:
                    os.environ[key] = value
        
        # Verify that the service has all expected components
        assert hasattr(service, 'vector_store'), "Service missing vector_store"
        assert hasattr(service, 'document_parser'), "Service missing document_parser"
        assert hasattr(service, 'web_scraper'), "Service missing web_scraper"
        assert hasattr(service, 'llm_manager'), "Service missing llm_manager"
        
        logger.info("✓ All components present in AICustomerService")
        
    except Exception as e:
        logger.error(f"✗ Failed structural test: {e}")
        return False

    return True

def test_files_exist():
    """Verify all required files exist"""
    logger.info("Testing file existence...")
    
    required_files = [
        "vector_store_service.py",
        "document_parser.py", 
        "web_scraper.py",
        "llm_provider.py",
        "main_service.py",
        "requirements.txt"
    ]
    
    all_found = True
    for file in required_files:
        file_path = Path(__file__).parent / file
        if file_path.exists():
            logger.info(f"✓ Found required file: {file}")
        else:
            logger.error(f"✗ Missing required file: {file}")
            all_found = False
    
    return all_found

def run_tests():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("STARTING AI CUSTOMER SERVICE VALIDATION TESTS")
    logger.info("=" * 60)
    
    tests = [
        ("File Existence", test_files_exist),
        ("Module Imports", test_imports), 
        ("Class Instantiation", test_instantiation),
        ("System Structure", test_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        result = test_func()
        results.append((test_name, result))
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY:")
    logger.info("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED! AI Customer Service system is ready.")
        logger.info("Next step: Install dependencies with 'pip install -r requirements.txt'")
    else:
        logger.info("❌ SOME TESTS FAILED! Please fix the issues above.")
    
    logger.info("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)