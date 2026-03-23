#!/usr/bin/env python3
"""Debug import issues with detailed logging"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "services"))

def test_module(module_name, class_names=None):
    print(f"\n--- Testing {module_name} ---")
    try:
        mod = __import__(module_name)
        print(f"  Module imported: {mod.__name__}")
        if class_names:
            for cls_name in class_names:
                if hasattr(mod, cls_name):
                    print(f"    Class '{cls_name}' found")
                else:
                    print(f"    [WARN] Class '{cls_name}' NOT found")
                    # List available attributes
                    attrs = [a for a in dir(mod) if not a.startswith('_')]
                    print(f"    Available: {', '.join(attrs[:10])}")
        return True
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def main():
    print("=== Import Debug Test ===")
    results = []

    results.append(("llm_provider", test_module("llm_provider", ["LLMProvider", "OpenAIProvider", "LLMProviderFactory"])))
    results.append(("vector_store_service", test_module("vector_store_service", ["VectorStoreService"])))
    results.append(("document_parser", test_module("document_parser", ["DocumentParser"])))
    results.append(("web_scraper", test_module("web_scraper", ["WebScraper"])))
    results.append(("feishu_notifier", test_module("feishu_notifier", ["FeishuNotifier"])))

    print("\n=== Summary ===")
    for name, ok in results:
        status = "OK" if ok else "FAIL"
        print(f"  {name}: {status}")

    all_ok = all(ok for _, ok in results)
    if all_ok:
        print("\n[SUCCESS] All modules importable")
    else:
        print("\n[FAILURE] Some modules failed to import")

    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
