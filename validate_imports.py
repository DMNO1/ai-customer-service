#!/usr/bin/env python3
"""
Simple import validator for enhanced system
"""

def main():
    print("Validating imports...")
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent / "services"))
        
        # Test each core module
        print("\n1. Testing LLM Provider...")
        from llm_provider import LLMProviderFactory, OpenAIProvider
        print("   [OK] llm_provider loaded")
        
        print("\n2. Testing Vector Store...")
        from vector_store_service import VectorStoreService
        print("   [OK] vector_store_service loaded")
        
        print("\n3. Testing Document Parser...")
        from document_parser import DocumentParser
        print("   [OK] document_parser loaded")
        
        print("\n4. Testing Web Scraper...")
        from web_scraper import WebScraper
        print("   [OK] web_scraper loaded")
        
        print("\n5. Testing Feishu Notifier...")
        from feishu_notifier import FeishuNotifier
        print("   [OK] feishu_notifier loaded")
        
        print("\n6. Testing Payment Service...")
        try:
            from payment_service import PaymentService
            print("   [OK] payment_service loaded")
        except ImportError as e:
            print(f"   [SKIP] payment_service: {e}")
        
        print("\n7. Testing Email Service...")
        try:
            from email_service import EmailService
            print("   [OK] email_service loaded")
        except ImportError as e:
            print(f"   [SKIP] email_service: {e}")
        
        print("\n8. Testing Enhanced Main Service...")
        from main_service_enhanced import EnhancedAICustomerService, APIErrorHandler
        print("   [OK] main_service_enhanced loaded")
        
        print("\n9. Testing Database Models...")
        # Import from root models.py (not the models package which contains LLM adapters)
        import importlib.util
        models_path = Path(__file__).parent / "models.py"
        spec = importlib.util.spec_from_file_location("root_models", models_path)
        root_models = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(root_models)
        User = root_models.User
        KnowledgeBase = root_models.KnowledgeBase
        Document = root_models.Document
        print("   [OK] models loaded")
        
        print("\n10. Testing API Module...")
        from api.main import app
        print("   [OK] api.main loaded")
        
        print("\n" + "="*60)
        print("SUCCESS! All core components are importable.")
        print("="*60)
        
        # Quick functionality test
        print("\nQuick functionality test:")
        factory = LLMProviderFactory()
        print(f"  - LLM Factory created (providers: {factory.list_available_providers()})")
        
        parser = DocumentParser()
        print(f"  - Document parser created")
        
        notifier = FeishuNotifier()
        print(f"  - Feishu notifier created")
        
        print("\n[SUCCESS] System ready to run!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1)