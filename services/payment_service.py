"""
Payment Service for AI Customer Service System
Handles payment processing for Alipay and WeChat Pay
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import uuid
import json
import os

try:
    from alipay import AliPay
except ImportError:
    AliPay = None
    logging.warning("alipay-sdk-python not installed")

try:
    import wechatpayv3
except ImportError:
    wechatpayv3 = None
    logging.warning("wechatpay-apiv3 not installed")


class PaymentService:
    """
    Unified payment service for Chinese payment providers
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize payment service
        
        Args:
            config: Configuration dictionary with API keys and settings
        """
        self.config = config or {}
        self.alipay_client = None
        self.wechat_client = None
        
        self._initialize_alipay()
        self._initialize_wechat()
        
        logging.info("PaymentService initialized")
    
    def _initialize_alipay(self):
        """
        Initialize Alipay client if credentials are available
        """
        app_id = self.config.get("alipay_app_id") or os.getenv("ALIPAY_APP_ID")
        app_private_key = self.config.get("alipay_private_key") or os.getenv("ALIPAY_PRIVATE_KEY")
        alipay_public_key = self.config.get("alipay_public_key") or os.getenv("ALIPAY_PUBLIC_KEY")
        
        if AliPay and app_id and app_private_key and alipay_public_key:
            try:
                self.alipay_client = AliPay(
                    appid=app_id,
                    app_notify_url=self.config.get("alipay_notify_url"),
                    app_private_key_string=app_private_key,
                    alipay_public_key_string=alipay_public_key,
                    sign_type="RSA2",
                    debug=False  # Set True for sandbox
                )
                logging.info("Alipay client initialized")
            except Exception as e:
                logging.error(f"Failed to initialize Alipay: {e}")
        else:
            logging.warning("Alipay credentials not fully configured")
    
    def _initialize_wechat(self):
        """
        Initialize WeChat Pay client if credentials are available
        """
        api_key = self.config.get("wechat_api_key") or os.getenv("WECHAT_API_KEY")
        mch_id = self.config.get("wechat_mch_id") or os.getenv("WECHAT_MCH_ID")
        cert_serial_no = self.config.get("wechat_cert_serial_no") or os.getenv("WECHAT_CERT_SERIAL_NO")
        private_key_path = self.config.get("wechat_private_key_path") or os.getenv("WECHAT_PRIVATE_KEY_PATH")
        
        if wechatpayv3 and api_key and mch_id and private_key_path:
            try:
                # Initialize WeChat Pay v3 client
                self.wechat_client = wechatpayv3.WechatPay(
                    apiv3_key=api_key,
                    mchid=mch_id,
                    appid=self.config.get("wechat_app_id") or os.getenv("WECHAT_APP_ID"),
                    cert_serial_no=cert_serial_no,
                    private_key_path=private_key_path
                )
                logging.info("WeChat Pay client initialized")
            except Exception as e:
                logging.error(f"Failed to initialize WeChat Pay: {e}")
        else:
            logging.warning("WeChat Pay credentials not fully configured")
    
    def create_order(self, user_id: str, plan_id: str, amount: float, currency: str = "CNY",
                    payment_method: str = "alipay", order_id: Optional[str] = None) -> Dict:
        """
        Create a payment order
        
        Args:
            user_id: User ID
            plan_id: Subscription plan ID
            amount: Order amount
            currency: Currency code (default CNY)
            payment_method: Payment method ('alipay' or 'wechat')
            order_id: Optional custom order ID
            
        Returns:
            Order information dictionary
        """
        if not order_id:
            order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
        
        order_data = {
            "order_id": order_id,
            "user_id": user_id,
            "plan_id": plan_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        # Generate payment URL based on method
        if payment_method == "alipay" and self.alipay_client:
            try:
                # Create Alipay order string
                order_string = self.alipay_client.api_alipay_trade_page_pay(
                    out_trade_no=order_id,
                    total_amount=str(amount),
                    subject=f"AI客服系统 - {plan_id} 订阅",
                    return_url=self.config.get("alipay_return_url", "https://yourdomain.com/payment/success"),
                    notify_url=self.config.get("alipay_notify_url")
                )
                
                # In production, this would be the gateway URL
                payment_url = f"https://openapi.alipaydev.com/gateway.do?{order_string}" if self.alipay_client.debug else f"https://openapi.alipay.com/gateway.do?{order_string}"
                
                order_data["payment_url"] = payment_url
                order_data["qr_code"] = None  # Would generate QR code from payment_url
                order_data["status"] = "awaiting_payment"
                
                logging.info(f"Created Alipay order: {order_id}")
                return order_data
                
            except Exception as e:
                logging.error(f"Failed to create Alipay order: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "order_id": order_id
                }
        
        elif payment_method == "wechat" and self.wechat_client:
            try:
                # Create WeChat Pay native order (QR code)
                amount_int = int(amount * 100)  # Convert to cents
                
                transaction_id = f"WX{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}"
                
                # Prepare parameters for WeChat Pay v3
                params = {
                    "mchid": self.wechat_client.mchid,
                    "appid": self.wechat_client.appid,
                    "description": f"AI客服系统 - {plan_id} 订阅",
                    "out_trade_no": order_id,
                    "notify_url": self.config.get("wechat_notify_url"),
                    "amount": {
                        "total": amount_int,
                        "currency": currency
                    },
                    "payer": {
                        # For native QR code, payer info not needed
                    }
                }
                
                # Get prepay ID or QR code
                result = self.wechat_client.native(params)
                
                order_data["payment_url"] = result.get("code_url")
                order_data["qr_code"] = result.get("code_url")  # QR code data
                order_data["status"] = "awaiting_payment"
                
                logging.info(f"Created WeChat Pay order: {order_id}")
                return order_data
                
            except Exception as e:
                logging.error(f"Failed to create WeChat Pay order: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "order_id": order_id
                }
        
        else:
            # Fallback: create manual order (for testing or unsupported methods)
            order_data["payment_url"] = None
            order_data["qr_code"] = None
            order_data["status"] = "manual_payment_required"
            logging.warning(f"Payment method {payment_method} not available, created manual order")
            return order_data
    
    def verify_payment(self, order_id: str, payment_method: str = "alipay") -> Dict:
        """
        Verify payment status for an order
        
        Args:
            order_id: Order ID to check
            payment_method: Payment method used
            
        Returns:
            Payment verification result
        """
        if payment_method == "alipay" and self.alipay_client:
            try:
                response = self.alipay_client.api_alipay_trade_query(out_trade_no=order_id)
                
                if response.get("code") == "10000":
                    trade_status = response.get("trade_status")
                    is_success = trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"]
                    
                    return {
                        "success": True,
                        "order_id": order_id,
                        "paid": is_success,
                        "trade_status": trade_status,
                        "amount": response.get("total_amount"),
                        "pay_time": response.get("send_pay_date"),
                        "raw_response": response
                    }
                else:
                    return {
                        "success": False,
                        "error": response.get("msg", "Unknown error"),
                        "order_id": order_id
                    }
                    
            except Exception as e:
                logging.error(f"Error verifying Alipay payment: {e}")
                return {"success": False, "error": str(e), "order_id": order_id}
        
        elif payment_method == "wechat" and self.wechat_client:
            try:
                # Query WeChat Pay order status
                params = {
                    "mchid": self.wechat_client.mchid,
                    "out_trade_no": order_id
                }
                
                result = self.wechat_client.query_order(params)
                
                trade_state = result.get("trade_state")
                is_success = trade_state == "SUCCESS"
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "paid": is_success,
                    "trade_status": trade_state,
                    "amount": result.get("amount", {}).get("total") / 100 if result.get("amount") else None,
                    "pay_time": result.get("success_time"),
                    "raw_response": result
                }
                
            except Exception as e:
                logging.error(f"Error verifying WeChat Pay: {e}")
                return {"success": False, "error": str(e), "order_id": order_id}
        
        else:
            return {
                "success": False,
                "error": f"Payment method {payment_method} not supported or not configured",
                "order_id": order_id
            }
    
    def process_callback(self, payment_method: str, callback_data: Dict, signature: Optional[str] = None) -> Dict:
        """
        Process payment callback/webhook
        
        Args:
            payment_method: Payment method (alipay/wechat)
            callback_data: Callback data from payment provider
            signature: Signature for verification (WeChat)
            
        Returns:
            Processed payment result
        """
        if payment_method == "alipay" and self.alipay_client:
            try:
                # Verify Alipay signature
                success = self.alipay_client.verify(callback_data, signature)
                if not success:
                    return {"success": False, "error": "Invalid signature"}
                
                # Extract order details
                order_id = callback_data.get("out_trade_no")
                trade_no = callback_data.get("trade_no")
                trade_status = callback_data.get("trade_status")
                amount = callback_data.get("total_amount")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "paid": trade_status in ["TRADE_SUCCESS", "TRADE_FINISHED"],
                    "provider_trade_id": trade_no,
                    "amount": amount,
                    "raw_data": callback_data
                }
                
            except Exception as e:
                logging.error(f"Error processing Alipay callback: {e}")
                return {"success": False, "error": str(e)}
        
        elif payment_method == "wechat" and self.wechat_client:
            try:
                # Verify WeChat Pay signature
                if not wechatpayv3.WechatPay.verify(callback_data, signature, self.wechat_client.api_key):
                    return {"success": False, "error": "Invalid signature"}
                
                # Parse notification
                resource = callback_data.get("resource", {})
                ciphertext = resource.get("ciphertext")
                
                if ciphertext:
                    # Decrypt the data (simplified)
                    decrypted = self.wechat_client.decrypt(ciphertext)
                    
                    return {
                        "success": True,
                        "order_id": decrypted.get("out_trade_no"),
                        "paid": decrypted.get("trade_state") == "SUCCESS",
                        "provider_trade_id": decrypted.get("transaction_id"),
                        "amount": decrypted.get("amount", {}).get("total"),
                        "raw_data": decrypted
                    }
                else:
                    return {"success": False, "error": "Missing ciphertext in WeChat callback"}
                    
            except Exception as e:
                logging.error(f"Error processing WeChat callback: {e}")
                return {"success": False, "error": str(e)}
        
        else:
            return {"success": False, "error": f"Unsupported payment method: {payment_method}"}
    
    def get_supported_methods(self) -> list:
        """Get list of available payment methods"""
        methods = []
        if self.alipay_client:
            methods.append("alipay")
        if self.wechat_client:
            methods.append("wechat")
        return methods


# Test function
def test_payment_service():
    """
    Test the payment service
    """
    print("Testing Payment Service...")
    
    service = PaymentService()
    
    print("Supported payment methods:", service.get_supported_methods())
    
    if service.alipay_client:
        print("✓ Alipay client initialized")
    else:
        print("✗ Alipay client not available (check credentials)")
    
    if service.wechat_client:
        print("✓ WeChat Pay client initialized")
    else:
        print("✗ WeChat Pay client not available (check credentials)")
    
    print("PaymentService test complete")


if __name__ == "__main__":
    test_payment_service()