"""
对话分析器 (Conversation Analyzer)

提供对话内容的分析方法，包括响应时间、敏感词检测、完整性检查等。
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class Message:
    """消息数据类"""
    id: str
    role: str  # 'user' 或 'assistant'
    content: str
    created_at: datetime
    metadata: Optional[Dict] = None


class ConversationAnalyzer:
    """对话分析器"""
    
    # 默认敏感词列表
    DEFAULT_SENSITIVE_WORDS = [
        "投诉", "举报", "差评", "退款", "骗子", "欺诈",
        "垃圾", "恶心", "太差", "烂", "坑人", "上当"
    ]
    
    # 问候语关键词
    GREETING_KEYWORDS = ["你好", "您好", "嗨", "hello", "hi", "欢迎"]
    
    # 结束语关键词
    FAREWELL_KEYWORDS = ["再见", "拜拜", "bye", "goodbye", "感谢", "谢谢"]
    
    # 响应超时阈值（秒）
    TIMEOUT_THRESHOLD = 30
    
    def __init__(self, sensitive_words: Optional[List[str]] = None):
        """
        初始化分析器
        
        Args:
            sensitive_words: 自定义敏感词列表
        """
        self.sensitive_words = sensitive_words or self.DEFAULT_SENSITIVE_WORDS
    
    def analyze_response_times(self, messages: List[Message]) -> Dict[str, Any]:
        """
        分析响应时间
        
        Args:
            messages: 消息列表
            
        Returns:
            响应时间分析结果
        """
        response_times = []
        timeout_count = 0
        
        for i in range(1, len(messages)):
            if messages[i].role == "assistant" and messages[i-1].role == "user":
                delta = (messages[i].created_at - messages[i-1].created_at).total_seconds()
                response_times.append(delta)
                
                if delta > self.TIMEOUT_THRESHOLD:
                    timeout_count += 1
        
        if not response_times:
            return {
                "avg_response_time": 0.0,
                "max_response_time": 0.0,
                "min_response_time": 0.0,
                "timeout_count": 0,
                "total_responses": 0
            }
        
        return {
            "avg_response_time": round(sum(response_times) / len(response_times), 2),
            "max_response_time": round(max(response_times), 2),
            "min_response_time": round(min(response_times), 2),
            "timeout_count": timeout_count,
            "total_responses": len(response_times)
        }
    
    def detect_sensitive_words(self, messages: List[Message]) -> Dict[str, Any]:
        """
        检测敏感词
        
        Args:
            messages: 消息列表
            
        Returns:
            敏感词检测结果
        """
        detected_words = []
        word_locations = []
        
        for msg in messages:
            content = msg.content.lower()
            for word in self.sensitive_words:
                if word.lower() in content:
                    detected_words.append(word)
                    word_locations.append({
                        "word": word,
                        "message_id": msg.id,
                        "role": msg.role,
                        "content_preview": msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                    })
        
        return {
            "detected": len(detected_words) > 0,
            "words": list(set(detected_words)),
            "count": len(detected_words),
            "locations": word_locations
        }
    
    def check_completeness(self, messages: List[Message]) -> Dict[str, Any]:
        """
        检查对话完整性
        
        Args:
            messages: 消息列表
            
        Returns:
            完整性检查结果
        """
        if not messages:
            return {
                "is_complete": False,
                "has_greeting": False,
                "has_farewell": False,
                "message_count": 0,
                "reason": "对话为空"
            }
        
        # 检查问候语（通常在对话开始）
        first_message = messages[0].content.lower()
        has_greeting = any(keyword.lower() in first_message for keyword in self.GREETING_KEYWORDS)
        
        # 检查结束语（通常在对话末尾）
        last_message = messages[-1].content.lower()
        has_farewell = any(keyword.lower() in last_message for keyword in self.FAREWELL_KEYWORDS)
        
        # 检查对话是否正常结束
        # 如果最后一条是用户消息且没有AI回复，可能对话未完成
        is_complete = not (messages[-1].role == "user" and len(messages) % 2 == 1)
        
        return {
            "is_complete": is_complete,
            "has_greeting": has_greeting,
            "has_farewell": has_farewell,
            "message_count": len(messages),
            "last_message_role": messages[-1].role
        }
    
    def analyze_sentiment(self, messages: List[Message]) -> Dict[str, Any]:
        """
        简单情感分析（基于关键词）
        
        Args:
            messages: 消息列表
            
        Returns:
            情感分析结果
        """
        positive_keywords = ["好", "棒", "优秀", "满意", "感谢", "谢谢", "喜欢", "不错"]
        negative_keywords = ["差", "烂", "糟糕", "失望", "不满", "讨厌", "垃圾", "恶心"]
        
        positive_count = 0
        negative_count = 0
        
        for msg in messages:
            if msg.role == "user":
                content = msg.content.lower()
                positive_count += sum(1 for word in positive_keywords if word in content)
                negative_count += sum(1 for word in negative_keywords if word in content)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment = "neutral"
            score = 0.5
        elif positive_count > negative_count:
            sentiment = "positive"
            score = positive_count / total
        else:
            sentiment = "negative"
            score = negative_count / total
        
        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    def calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """
        计算综合质量评分
        
        Args:
            metrics: 各项指标数据
            
        Returns:
            综合评分(0-100)
        """
        score = 100.0
        
        # 响应时间扣分
        response_time = metrics.get("avg_response_time", 0)
        if response_time > 10:
            score -= min(20, (response_time - 10) * 2)
        
        # 超次数扣分
        timeout_count = metrics.get("timeout_count", 0)
        score -= timeout_count * 10
        
        # 敏感词扣分
        sensitive_count = metrics.get("sensitive_word_count", 0)
        score -= sensitive_count * 15
        
        # 完整性扣分
        if not metrics.get("is_complete", True):
            score -= 10
        
        # 确保分数在0-100之间
        return max(0.0, min(100.0, score))
    
    def analyze_conversation(self, messages: List[Message]) -> Dict[str, Any]:
        """
        全面分析对话
        
        Args:
            messages: 消息列表
            
        Returns:
            完整分析结果
        """
        # 分析响应时间
        response_analysis = self.analyze_response_times(messages)
        
        # 检测敏感词
        sensitive_analysis = self.detect_sensitive_words(messages)
        
        # 检查完整性
        completeness = self.check_completeness(messages)
        
        # 情感分析
        sentiment = self.analyze_sentiment(messages)
        
        # 统计消息数
        user_count = sum(1 for m in messages if m.role == "user")
        ai_count = sum(1 for m in messages if m.role == "assistant")
        
        # 计算综合评分
        metrics = {
            "avg_response_time": response_analysis["avg_response_time"],
            "max_response_time": response_analysis["max_response_time"],
            "timeout_count": response_analysis["timeout_count"],
            "message_count": len(messages),
            "user_message_count": user_count,
            "ai_message_count": ai_count,
            "sensitive_word_count": sensitive_analysis["count"],
            "is_complete": completeness["is_complete"],
            "has_greeting": completeness["has_greeting"],
            "has_farewell": completeness["has_farewell"]
        }
        
        quality_score = self.calculate_quality_score(metrics)
        
        return {
            "score": round(quality_score, 2),
            "response_time": response_analysis,
            "sensitive_words": sensitive_analysis,
            "completeness": completeness,
            "sentiment": sentiment,
            "message_stats": {
                "total": len(messages),
                "user": user_count,
                "assistant": ai_count
            }
        }
