"""测试Quality模块导入"""
try:
    from quality import QualityService, QualityReport, ConversationAnalyzer
    print("Quality模块导入成功")
    
    # 测试创建服务
    service = QualityService()
    print("QualityService创建成功")
    
    # 测试分析器
    analyzer = ConversationAnalyzer()
    print("ConversationAnalyzer创建成功")
    
    print("\n所有测试通过！")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
