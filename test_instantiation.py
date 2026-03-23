#!/usr/bin/env python3
"""Test instantiation of core classes without heavy dependencies"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "services"))

def test_instantiation():
    print("=== Testing Class Instantiation ===\n")

    # Test LLMProviderFactory (lightweight)
    print("1. LLMProviderFactory")
    try:
        from llm_provider import LLMProviderFactory
        factory = LLMProviderFactory()
        print(f"   [OK] Created factory")
        print(f"   Available providers: {LLMProviderFactory.list_available_providers()}")
    except Exception as e:
        print(f"   [ERROR] {e}")
        traceback.print_exc()
        return False

    # Test DocumentParser (lightweight)
    print("\n2. DocumentParser")
    try:
        from document_parser import DocumentParser
        parser = DocumentParser()
        print(f"   [OK] Created parser")
    except Exception as e:
        print(f"   [ERROR] {e}")
        traceback.print_exc()
        return False

    # Test WebScraper (lightweight)
    print("\n3. WebScraper")
    try:
        from web_scraper import WebScraper
        scraper = WebScraper()
        print(f"   [OK] Created scraper")
    except Exception as e:
        print(f"   [ERROR] {e}")
        traceback.print_exc()
        return False

    # Test FeishuNotifier (lightweight)
    print("\n4. FeishuNotifier")
    try:
        from feishu_notifier import FeishuNotifier
        notifier = FeishuNotifier()
        print(f"   [OK] Created notifier")
        print(f"   Webhook configured: {bool(notifier.webhook_url)}")
    except Exception as e:
        print(f"   [ERROR] {e}")
        traceback.print_exc()
        return False

    # Skip VectorStoreService because it requires OpenAI API key and network
    print("\n5. VectorStoreService (SKIPPED - requires API key)")
    print("   [SKIP] Skipped to avoid network/API dependency")

    print("\n" + "="*60)
    print("[SUCCESS] All lightweight tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_instantiation()
    sys.exit(0 if success else 1)
