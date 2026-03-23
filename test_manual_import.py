#!/usr/bin/env python
"""测试导入AICustomerService"""
from main_service import AICustomerService

print("✅ AICustomerService 导入成功！")

# 尝试无API密钥初始化（正如test_system.py做的）
service = AICustomerService(config={
    "vector_store_dir": "./test_manual_db",
    "scraper_timeout": 5,
    "log_level": "WARNING"
})

print("✅ AICustomerService 初始化成功（无API密钥）！")
print(f"服务组件：")
print(f"  - vector_store: {type(service.vector_store)}")
print(f"  - document_parser: {type(service.document_parser)}")
print(f"  - web_scraper: {type(service.web_scraper)}")
print(f"  - llm_manager: {type(service.llm_manager)}")
print(f"已注册的LLM提供商: {service.llm_manager.list_providers()}")
