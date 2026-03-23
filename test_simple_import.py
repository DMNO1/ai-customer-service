#!/usr/bin/env python
"""Test importing AICustomerService"""
from main_service import AICustomerService

print("SUCCESS: AICustomerService imported successfully!")

# Try to initialize without API keys (as test_system.py does)
service = AICustomerService(config={
    "vector_store_dir": "./test_simple_db",
    "scraper_timeout": 5,
    "log_level": "WARNING"
})

print("SUCCESS: AICustomerService initialized successfully (no API keys)!")
print("Service components:")
print("  - vector_store: " + str(type(service.vector_store)))
print("  - document_parser: " + str(type(service.document_parser)))
print("  - web_scraper: " + str(type(service.web_scraper)))
print("  - llm_manager: " + str(type(service.llm_manager)))
print("Registered LLM providers: " + str(service.llm_manager.list_providers()))
