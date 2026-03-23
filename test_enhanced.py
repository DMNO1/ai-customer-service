#!/usr/bin/env python3
"""
Comprehensive test suite for Enhanced AI Customer Service System
Tests all service modules with and without external dependencies
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "skipped": []
}


def log_test(name: str, status: str, message: str = ""):
    """Log test result with visual indicators"""
    icon = {"PASS": "✓", "FAIL": "✗", "SKIP": "⊘"}.get(status, "?")
    print(f"{icon} {name:<40} {status}")
    if message:
        print(f"   → {message}")
    
    test_results[status.lower()].append(name)


async def test_all():
    """Run all tests"""
    print("="*70)
    print("AI CUSTOMER SERVICE - ENHANCED SYSTEM TEST SUITE")
    print("="*70)
    print()
    
    # Import tests (won't fail if modules missing)
    tests = [
        ("Configuration & Environment", test_environment),
        ("Vector Store Service", test_vector_store),
        ("Document Parser", test_document_parser),
        ("Web Scraper", test_web_scraper),
        ("LLM Provider Manager", test_llm_manager),
        ("Feishu Notifier", test_feishu_notifier),
        ("Payment Service", test_payment_service),
        ("Email Service", test_email_service),
        ("Enhanced Main Service", test_enhanced_service),
        ("Database Models", test_database_models),
        ("API Endpoints", test_api_endpoints),
    ]
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                await test_func()
            else:
                test_func()
        except Exception as e:
            log_test(test_name, "FAIL", str(e))
    
    # Print summary
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    total = len(tests)
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    skipped = len(test_results["skipped"])
    
    print(f"Total tests:  {total}")
    print(f"Passed:       {passed}")
    print(f"Failed:       {failed}")
    print(f"Skipped:      {skipped}")
    print(f"Success rate: {passed/total*100:.1f}%" if total > 0 else "No tests run")
    print("="*70)
    
    return failed == 0


def should_skip(module_name: str) -> Tuple[bool, str]:
    """Check if a test should be skipped due to missing dependencies"""
    try:
        __import__(module_name)
        return False, ""
    except ImportError as e:
        missing = str(e).split("'")[1] if "'" in str(e) else str(e)
        return True, f"Missing dependency: {missing}"


def test_environment():
    """Test environment configuration"""
    import dotenv
    
    # Check if .env exists
    env_path = Path(".env")
    if env_path.exists():
        log_test("Environment file", "PASS", ".env exists")
    else:
        log_test("Environment file", "SKIP", ".env not found (copy from .env.example)")
    
    # Check key environment variables
    key_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "DATABASE_URL",
        "FEISHU_APP_ID"
    ]
    
    missing_vars = [var for var in key_vars if not os.getenv(var)]
    if missing_vars:
        log_test("Environment variables", "SKIP", f"Missing: {', '.join(missing_vars)}")
    else:
        log_test("Environment variables", "PASS", "All key vars present")


def test_vector_store():
    """Test Vector Store Service"""
    skip, reason = should_skip("chromadb")
    if skip:
        log_test("Vector Store Service", "SKIP", reason)
        return
    
    try:
        from services.vector_store_service import VectorStoreService
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            service = VectorStoreService(persist_directory=tmpdir)
            log_test("VectorStoreService init", "PASS")
            
            # Test create collection
            service.vector_store.create_collection("test_kb")
            log_test("Create collection", "PASS")
            
            # Test list knowledge bases
            kbs = service.list_knowledge_bases()
            assert "test_kb" in kbs, "test_kb not in list"
            log_test("List knowledge bases", "PASS")
            
    except Exception as e:
        log_test("VectorStoreService", "FAIL", str(e))


def test_document_parser():
    """Test Document Parser"""
    skip, reason = should_skip("PyPDF2")
    if skip:
        log_test("Document Parser", "SKIP", reason)
        return
    
    try:
        from services.document_parser import DocumentParser
        
        parser = DocumentParser()
        log_test("DocumentParser init", "PASS")
        
        # Test with a sample text file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document.\nIt has multiple lines.\nTesting parser.")
            temp_path = f.name
        
        try:
            content = parser.parse_document(temp_path)
            assert len(content) > 0, "Empty content"
            assert "test document" in content.lower(), "Content not parsed correctly"
            log_test("Document parsing", "PASS")
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        log_test("DocumentParser", "FAIL", str(e))


def test_web_scraper():
    """Test Web Scraper"""
    skip, reason = should_skip("playwright")
    if skip:
        log_test("Web Scraper", "SKIP", reason)
        return
    
    try:
        from services.web_scraper import WebScraper
        
        scraper = WebScraper(timeout=5)
        log_test("WebScraper init", "PASS")
        
        # Test content extraction from HTML
        sample_html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <main>
                    <h1>Test Content</h1>
                    <p>This is a paragraph.</p>
                    <p>Another paragraph.</p>
                </main>
            </body>
        </html>
        """
        
        content = scraper.extract_content(sample_html)
        assert "test content" in content.lower(), f"Content extraction failed: {content}"
        log_test("Content extraction", "PASS")
        
    except Exception as e:
        log_test("WebScraper", "FAIL", str(e))


def test_llm_manager():
    """Test LLM Provider Manager"""
    try:
        from services.llm_provider import LLMManager
        
        manager = LLMManager()
        log_test("LLMManager init", "PASS")
        
        # List providers (should be empty if no keys set)
        providers = manager.list_providers()
        log_test("List providers", "PASS", f"Available: {providers if providers else 'None'}")
        
        # Test error when no providers
        try:
            manager.chat_completion([{"role": "user", "content": "test"}])
            log_test("No provider error", "FAIL", "Should have raised error")
        except ValueError:
            log_test("No provider error", "PASS", "Correctly raises error when no providers")
        
    except Exception as e:
        log_test("LLMManager", "FAIL", str(e))


def test_feishu_notifier():
    """Test Feishu Notifier"""
    try:
        from services.feishu_notifier import FeishuNotifier
        
        notifier = FeishuNotifier()
        log_test("FeishuNotifier init", "PASS")
        
        # Test config detection
        config_status = []
        if notifier.webhook_url:
            config_status.append("webhook")
        if notifier.app_id:
            config_status.append("app_id")
        
        if config_status:
            log_test("Configuration", "PASS", f"Configured: {', '.join(config_status)}")
        else:
            log_test("Configuration", "SKIP", "No credentials configured")
        
    except Exception as e:
        log_test("FeishuNotifier", "FAIL", str(e))


def test_payment_service():
    """Test Payment Service"""
    skip, reason = should_skip("alipay")
    if skip:
        log_test("Payment Service", "SKIP", reason)
        return
    
    try:
        from services.payment_service import PaymentService
        
        service = PaymentService()
        log_test("PaymentService init", "PASS")
        
        # Test supported methods
        methods = service.get_supported_methods()
        log_test("Supported methods", "PASS", f"Available: {methods if methods else 'None'}")
        
    except Exception as e:
        log_test("PaymentService", "FAIL", str(e))


def test_email_service():
    """Test Email Service"""
    skip, reason = should_skip("jinja2")
    if skip:
        log_test("Email Service", "SKIP", reason)
        return
    
    try:
        from services.email_service import EmailService, EmailTemplate
        
        service = EmailService()
        log_test("EmailService init", "PASS")
        
        # Test SMTP config detection
        if service.smtp_host:
            log_test("SMTP Config", "PASS", f"Host: {service.smtp_host}")
        else:
            log_test("SMTP Config", "SKIP", "No SMTP configured")
        
    except Exception as e:
        log_test("EmailService", "FAIL", str(e))


def test_enhanced_service():
    """Test Enhanced Main Service"""
    try:
        from main_service_enhanced import EnhancedAICustomerService, APIErrorHandler
        
        # Test APIErrorHandler
        handler = APIErrorHandler()
        error_info = handler.handle_exception(ValueError("Test error"), "test_context")
        assert "error_id" in error_info, "Missing error_id"
        log_test("APIErrorHandler", "PASS")
        
        # Initialize enhanced service
        service = EnhancedAICustomerService()
        log_test("EnhancedAICustomerService init", "PASS")
        
        # Test health check
        health = service.get_system_health()
        assert "status" in health, "Missing status in health"
        assert "components" in health, "Missing components in health"
        log_test("Health check", "PASS", f"Status: {health['status']}")
        
    except Exception as e:
        log_test("EnhancedAICustomerService", "FAIL", str(e))


def test_database_models():
    """Test Database Models"""
    skip, reason = should_skip("sqlalchemy")
    if skip:
        log_test("Database Models", "SKIP", reason)
        return
    
    try:
        from models import User, KnowledgeBase, Document, Conversation, Message, Subscription, AuditLog
        
        # Import successful
        log_test("Models import", "PASS")
        
        # Check model relationships
        assert hasattr(User, 'knowledge_bases'), "User missing knowledge_bases relationship"
        assert hasattr(KnowledgeBase, 'documents'), "KnowledgeBase missing documents relationship"
        log_test("Model relationships", "PASS")
        
    except Exception as e:
        log_test("Database Models", "FAIL", str(e))


def test_api_endpoints():
    """Test API module"""
    skip, reason = should_skip("flask")
    if skip:
        log_test("API Endpoints", "SKIP", reason)
        return
    
    try:
        from main_service_enhanced import create_flask_app
        from main_service_enhanced import EnhancedAICustomerService
        import inspect
        
        # Check function exists
        assert inspect.isfunction(create_flask_app), "create_flask_app not a function"
        log_test("create_flask_app function", "PASS")
        
        # Try creating app with a minimal service
        service = EnhancedAICustomerService()
        app = create_flask_app(service)
        log_test("Flask app creation", "PASS")
        
        # Check routes are registered
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ['/health', '/knowledge/base', '/knowledge/bases', '/chat']
        for route in expected_routes:
            assert route in routes, f"Missing route: {route}"
        log_test("Route registration", "PASS", f"{len(routes)} routes")
        
    except Exception as e:
        log_test("API Endpoints", "FAIL", str(e))


if __name__ == "__main__":
    # Ensure we're in the right directory
    required_dirs = ["services", "api", "database"]
    for d in required_dirs:
        if not Path(d).exists():
            print(f"ERROR: Required directory '{d}' not found.")
            print("Please run this script from the ai-customer-service directory.")
            sys.exit(1)
    
    # Run tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(test_all())
    loop.close()
    
    sys.exit(0 if success else 1)