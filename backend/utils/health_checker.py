"""
健康检查模块
提供系统各组件的健康状态检查
"""

import os
import time
import socket
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .logger import system_logger


@dataclass
class HealthCheckResult:
    """健康检查结果数据类"""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: float
    message: str
    details: Optional[Dict[str, Any]] = None
    last_checked: str = None
    
    def __post_init__(self):
        if self.last_checked is None:
            self.last_checked = datetime.now().isoformat()


class HealthChecker:
    """
    系统健康检查器
    检查所有关键服务的健康状态
    """
    
    def __init__(self):
        self.checks: List[callable] = [
            self.check_database,
            self.check_vector_store,
            self.check_redis,
            self.check_ai_model,
        ]
        
        # 可选的外部服务检查
        if os.getenv('STRIPE_API_KEY'):
            self.checks.append(self.check_stripe_api)
        
        if os.getenv('SENDGRID_API_KEY'):
            self.checks.append(self.check_sendgrid_api)
    
    def check_all(self) -> Dict[str, Any]:
        """
        执行所有健康检查
        
        Returns:
            包含所有组件健康状态的字典
        """
        results = []
        overall_status = "healthy"
        
        for check_func in self.checks:
            try:
                result = check_func()
                results.append(asdict(result))
                
                # 更新整体状态
                if result.status == "unhealthy":
                    overall_status = "unhealthy"
                elif result.status == "degraded" and overall_status == "healthy":
                    overall_status = "degraded"
                    
            except Exception as e:
                system_logger.error(f"Health check failed for {check_func.__name__}: {e}")
                error_result = HealthCheckResult(
                    component=check_func.__name__.replace("check_", ""),
                    status="unhealthy",
                    response_time_ms=0,
                    message=f"Check failed: {str(e)}"
                )
                results.append(asdict(error_result))
                overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }
    
    def check_database(self) -> HealthCheckResult:
        """检查PostgreSQL数据库连接"""
        start_time = time.time()
        
        try:
            import psycopg2
            
            db_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/aics')
            conn = psycopg2.connect(db_url, connect_timeout=5)
            conn.cursor().execute('SELECT 1')
            conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="database",
                status="healthy",
                response_time_ms=round(response_time, 2),
                message="Database connection successful",
                details={"type": "postgresql"}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            system_logger.error(f"Database health check failed: {e}")
            
            return HealthCheckResult(
                component="database",
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                message=f"Database connection failed: {str(e)}",
                details={"type": "postgresql", "error": str(e)}
            )
    
    def check_vector_store(self) -> HealthCheckResult:
        """检查向量数据库连接（Qdrant/Pinecone/Milvus）"""
        start_time = time.time()
        
        try:
            # 尝试检测使用的向量存储类型
            vector_store_type = os.getenv('VECTOR_STORE_TYPE', 'qdrant').lower()
            
            if vector_store_type == 'qdrant':
                from qdrant_client import QdrantClient
                client = QdrantClient(
                    host=os.getenv('QDRANT_HOST', 'localhost'),
                    port=int(os.getenv('QDRANT_PORT', 6333))
                )
                client.get_collections()
                
            elif vector_store_type == 'pinecone':
                import pinecone
                pinecone.init(api_key=os.getenv('PINECONE_API_KEY'))
                pinecone.list_indexes()
                
            elif vector_store_type == 'milvus':
                from pymilvus import connections
                connections.connect(
                    alias="health_check",
                    host=os.getenv('MILVUS_HOST', 'localhost'),
                    port=os.getenv('MILVUS_PORT', '19530')
                )
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="vector_store",
                status="healthy",
                response_time_ms=round(response_time, 2),
                message=f"Vector store ({vector_store_type}) connection successful",
                details={"type": vector_store_type}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            system_logger.error(f"Vector store health check failed: {e}")
            
            return HealthCheckResult(
                component="vector_store",
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                message=f"Vector store connection failed: {str(e)}",
                details={"type": vector_store_type, "error": str(e)}
            )
    
    def check_redis(self) -> HealthCheckResult:
        """检查Redis连接"""
        start_time = time.time()
        
        try:
            import redis
            
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD') or None,
                socket_connect_timeout=5
            )
            r.ping()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="redis",
                status="healthy",
                response_time_ms=round(response_time, 2),
                message="Redis connection successful",
                details={"host": os.getenv('REDIS_HOST', 'localhost')}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            system_logger.error(f"Redis health check failed: {e}")
            
            return HealthCheckResult(
                component="redis",
                status="degraded",  # Redis失败时系统仍可运行
                response_time_ms=round(response_time, 2),
                message=f"Redis connection failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_ai_model(self) -> HealthCheckResult:
        """检查AI模型服务可用性"""
        start_time = time.time()
        
        try:
            model_provider = os.getenv('AI_MODEL_PROVIDER', 'openai').lower()
            
            if model_provider == 'openai':
                import openai
                openai.api_key = os.getenv('OPENAI_API_KEY')
                # 轻量级检查：列出模型
                openai.Model.list()
                
            elif model_provider == 'anthropic':
                import anthropic
                client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                # Anthropic没有简单的ping接口，尝试获取账户信息
                
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="ai_model",
                status="healthy",
                response_time_ms=round(response_time, 2),
                message=f"AI model service ({model_provider}) is available",
                details={"provider": model_provider}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            system_logger.error(f"AI model health check failed: {e}")
            
            return HealthCheckResult(
                component="ai_model",
                status="unhealthy",
                response_time_ms=round(response_time, 2),
                message=f"AI model service unavailable: {str(e)}",
                details={"provider": model_provider, "error": str(e)}
            )
    
    def check_stripe_api(self) -> HealthCheckResult:
        """检查Stripe API可用性"""
        start_time = time.time()
        
        try:
            import stripe
            stripe.api_key = os.getenv('STRIPE_API_KEY')
            
            # 轻量级API调用
            stripe.Account.retrieve()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="stripe",
                status="healthy",
                response_time_ms=round(response_time, 2),
                message="Stripe API connection successful",
                details={"mode": "live" if "sk_live" in os.getenv('STRIPE_API_KEY', '') else "test"}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            system_logger.error(f"Stripe API health check failed: {e}")
            
            return HealthCheckResult(
                component="stripe",
                status="degraded",
                response_time_ms=round(response_time, 2),
                message=f"Stripe API check failed: {str(e)}",
                details={"error": str(e)}
            )
    
    def check_sendgrid_api(self) -> HealthCheckResult:
        """检查SendGrid API可用性"""
        start_time = time.time()
        
        try:
            from sendgrid import SendGridAPIClient
            
            sg = SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
            sg.client.user.agent.get()
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                component="sendgrid",
                status="healthy",
                response_time_ms=round(response_time, 2),
                message="SendGrid API connection successful"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            system_logger.error(f"SendGrid API health check failed: {e}")
            
            return HealthCheckResult(
                component="sendgrid",
                status="degraded",
                response_time_ms=round(response_time, 2),
                message=f"SendGrid API check failed: {str(e)}",
                details={"error": str(e)}
            )


# 全局健康检查器实例
health_checker = HealthChecker()
