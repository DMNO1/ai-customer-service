"""
Core Services Test - Simplified Dry Run V2
Tests the essential services without complex dependencies
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_document_parser():
    """Test Document Parser Service"""
    print("Testing Document Parser Service...")
    try:
        from services.document_parser import DocumentParser
        parser = DocumentParser()
        
        # Create a test file
        test_file = Path("test_sample.txt")
        test_file.write_text("This is a test document for AI customer service system.", encoding='utf-8')
        
        # Parse the file - parse_document returns string, not dict
        result = parser.parse_document(str(test_file))
        
        # Cleanup
        test_file.unlink()
        
        if result and len(result) > 0:
            print("[OK] Document Parser: Working correctly")
            return True
        else:
            print("[FAIL] Document Parser: Parse result invalid")
            return False
    except Exception as e:
        print(f"[FAIL] Document Parser: {str(e)}")
        return False

def test_web_scraper():
    """Test Web Scraper Service"""
    print("Testing Web Scraper Service...")
    try:
        from services.web_scraper import WebScraper
        scraper = WebScraper()
        
        # Test with extract_content method
        html = "<html><body><p>This is test content for web scraping.</p></body></html>"
        result = scraper.extract_content(html)
        
        if result and len(result) > 0:
            print("[OK] Web Scraper: Working correctly")
            return True
        else:
            print("[FAIL] Web Scraper: Extraction result invalid")
            return False
    except Exception as e:
        print(f"[FAIL] Web Scraper: {str(e)}")
        return False

def test_llm_provider():
    """Test LLM Provider Factory"""
    print("Testing LLM Provider Factory...")
    try:
        from services.llm_provider import LLMProviderFactory
        
        # Use list_available_providers (class method)
        providers = LLMProviderFactory.list_available_providers()
        
        if providers and len(providers) > 0:
            print(f"[OK] LLM Provider: Available providers - {', '.join(providers)}")
            return True
        else:
            print("[FAIL] LLM Provider: No providers available")
            return False
    except Exception as e:
        print(f"[FAIL] LLM Provider: {str(e)}")
        return False

def test_email_service():
    """Test Email Service"""
    print("Testing Email Service...")
    try:
        from services.email_service import EmailService
        service = EmailService()
        print("[OK] Email Service: Initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Email Service: {str(e)}")
        return False

def test_payment_service():
    """Test Payment Service"""
    print("Testing Payment Service...")
    try:
        from services.payment_service import PaymentService
        service = PaymentService()
        print("[OK] Payment Service: Initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Payment Service: {str(e)}")
        return False

def test_feishu_notifier():
    """Test Feishu Notifier"""
    print("Testing Feishu Notifier...")
    try:
        from services.feishu_notifier import FeishuNotifier
        notifier = FeishuNotifier()
        print("[OK] Feishu Notifier: Initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Feishu Notifier: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("AI CUSTOMER SERVICE - CORE SERVICES TEST V2")
    print("=" * 60)
    print()
    
    tests = [
        ("Document Parser", test_document_parser),
        ("Web Scraper", test_web_scraper),
        ("LLM Provider", test_llm_provider),
        ("Email Service", test_email_service),
        ("Payment Service", test_payment_service),
        ("Feishu Notifier", test_feishu_notifier),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        print()
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name}: {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[OK] All core services are working correctly!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} service(s) need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
