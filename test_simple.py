#!/usr/bin/env python3
"""Simple test script"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Starting simple tests...")
print(f"Project root: {project_root}")

# Test 1: Check file structure
test_files = [
    "backend/app.py",
    "backend/utils/logger.py",
    "backend/utils/error_handler.py",
    "backend/utils/health_checker.py",
    "backend/routes/api.py",
]

passed = 0
failed = 0

for f in test_files:
    path = project_root / f
    if path.exists():
        print(f"[OK] {f} exists")
        passed += 1
    else:
        print(f"[FAIL] {f} missing")
        failed += 1

# Test 2: Try imports
try:
    from backend.utils.error_handler import APIError, ValidationError
    print("[OK] error_handler imports work")
    passed += 1
except Exception as e:
    print(f"[FAIL] error_handler import failed: {e}")
    failed += 1

try:
    from backend.utils.logger import setup_logger
    print("[OK] logger imports work")
    passed += 1
except Exception as e:
    print(f"[FAIL] logger import failed: {e}")
    failed += 1

try:
    from backend.utils.health_checker import HealthChecker
    print("[OK] health_checker imports work")
    passed += 1
except Exception as e:
    print(f"[FAIL] health_checker import failed: {e}")
    failed += 1

print(f"\n=== Test Results ===")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {passed + failed}")

if failed == 0:
    print("All tests passed!")
    sys.exit(0)
else:
    print("Some tests failed!")
    sys.exit(1)
