"""
支付 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Optional
import uuid
from datetime import datetime

from app.api.schemas import OrderCreate, OrderResponse
from app.core.exceptions import PaymentException
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/payment", tags=["payment"])

# 内存订单存储（生产用数据库）
_orders = {}

@router.post("/create-order", response_model=OrderResponse)
async def create_order(data: OrderCreate):
    """创建支付订单"""
    order_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # TODO: 查询套餐价格
    amount_map = {
        "basic": 99.00,
        "pro": 299.00,
        "enterprise": 999.00
    }
    amount = amount_map.get(data.plan_id, 0)

    _orders[order_id] = {
        "id": order_id,
        "plan_id": data.plan_id,
        "amount": amount,
        "status": "pending",
        "payment_method": data.payment_method,
        "created_at": now,
        "paid_at": None
    }

    logger.info("order_created", order_id=order_id, plan=data.plan_id, amount=amount)

    # 生成支付跳转链接（简化，实际需要调用支付宝/微信 SDK）
    payment_url = f"/api/v1/payment/{data.payment_method}/pay?order_id={order_id}"

    return OrderResponse(
        id=order_id,
        amount=amount,
        status="pending",
        payment_method=data.payment_method,
        payment_url=payment_url,
        created_at=now
    )

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    """查询订单状态"""
    order = _orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return OrderResponse(**order)

@router.post("/alipay/notify")
async def alipay_notify(request: Request):
    """支付宝回调通知（异步）"""
    form_data = await request.form()
    logger.info("alipay_notify_received", data=dict(form_data))

    # TODO: 验证签名 + 更新订单状态
    # 这里仅作占位
    return {"success": True}

@router.post("/wechat/notify")
async def wechat_notify(request: Request):
    """微信支付回调通知"""
    xml_data = await request.body()
    logger.info("wechat_notify_received", xml_length=len(xml_data))

    # TODO: 解析 XML + 验签 + 更新订单
    return {"success": True}

@router.post("/orders/{order_id}/invoice")
async def generate_invoice(order_id: str):
    """申请开发票"""
    order = _orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if order["status"] != "paid":
        raise HTTPException(status_code=400, detail="订单未支付，无法开票")

    # TODO: 调用开票系统 API
    logger.info("invoice_requested", order_id=order_id)

    return {
        "success": True,
        "download_url": f"/api/v1/invoices/{order_id}.pdf",
        "expires_at": datetime.utcnow().timestamp() + 7 * 24 * 3600  # 7天有效
    }
