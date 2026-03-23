import os
import sys
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_postgres():
    """Check PostgreSQL connection."""
    try:
        import psycopg2
        # Use direct connection string for health check
        conn_str = "postgresql://postgres:postgres@localhost:5432/ai_customer_service"
        conn = psycopg2.connect(conn_str)
        conn.close()
        return True
    except Exception as e:
        logger.error(f"PostgreSQL check failed: {e}")
        return False

def check_qdrant():
    """Check Qdrant connection."""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6333)
        client.get_collections()
        return True
    except Exception as e:
        logger.error(f"Qdrant check failed: {e}")
        return False

def check_redis():
    """Check Redis connection."""
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        return False

def check_stripe_api():
    """Check Stripe API connectivity."""
    try:
        import stripe
        api_key = os.getenv("STRIPE_API_KEY")
        if not api_key:
            logger.warning("STRIPE_API_KEY is not set, skipping Stripe check.")
            return True
        stripe.api_key = api_key
        stripe.Balance.retrieve()
        return True
    except Exception as e:
        logger.error(f"Stripe API check failed: {e}")
        return False

def check_sendgrid_api():
    """Check SendGrid API connectivity."""
    try:
        from sendgrid import SendGridAPIClient
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            logger.warning("SENDGRID_API_KEY is not set, skipping SendGrid check.")
            return True
        sg = SendGridAPIClient(api_key=api_key)
        response = sg.client.user.profile.get()
        return response.status_code == 200
    except Exception as e:
        logger.error(f"SendGrid API check failed: {e}")
        return False

def send_feishu_alert(message: str):
    """Send an alert message to Feishu via webhook."""
    webhook_url = os.getenv("FEISHU_ALERT_WEBHOOK")
    if not webhook_url:
        logger.warning("FEISHU_ALERT_WEBHOOK is not set, cannot send alert.")
        return
    
    payload = {
        "msg_type": "text",
        "content": {
            "text": f"[AI Customer Service Alert] {message}"
        }
    }
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send Feishu alert: {response.text}")
    except Exception as e:
        logger.error(f"Exception while sending Feishu alert: {e}")

def main():
    logger.info("Starting system health check...")
    checks = {
        "PostgreSQL": check_postgres(),
        "Qdrant": check_qdrant(),
        "Redis": check_redis(),
        "Stripe API": check_stripe_api(),
        "SendGrid API": check_sendgrid_api(),
    }

    all_passed = all(checks.values())
    if all_passed:
        logger.info("All system health checks passed.")
        return 0
    else:
        failed_services = [service for service, ok in checks.items() if not ok]
        error_message = f"Health check failed at {datetime.now().isoformat()}. Failed services: {', '.join(failed_services)}"
        logger.error(error_message)
        send_feishu_alert(error_message)
        return 1

if __name__ == "__main__":
    sys.exit(main())