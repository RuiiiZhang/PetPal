"""
支付服务
虎皮椒支付 API 集成，支持 Mock 模式
"""

import os
import time
import hashlib
import json
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings


class PaymentService:
    """虎皮椒支付服务"""

    # 套餐价格映射
    PLAN_PRICES = {
        "basic": 19.9,
        "standard": 29.9,
        "premium": 49.9,
    }

    def __init__(self):
        self.mode = settings.PAYMENT_MODE  # "mock" 或 "production"
        self.appid = settings.XUNHU_APPID
        self.appsecret = settings.XUNHU_APPSECRET
        self.api_url = settings.XUNHU_API_URL
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """关闭 HTTP 客户端"""
        await self._client.aclose()

    def get_plan_price(self, plan: str) -> float:
        """
        获取套餐价格。

        Args:
            plan: 套餐名称 (basic/standard/premium)

        Returns:
            float: 价格（元）

        Raises:
            ValueError: 无效套餐名
        """
        price = self.PLAN_PRICES.get(plan)
        if price is None:
            raise ValueError(f"无效套餐: {plan}，可选: basic/standard/premium")
        return price

    async def create_order(
        self,
        order_id: str,
        pet_name: str,
        plan: str = "standard",
        callback_url: str = None
    ) -> Dict[str, Any]:
        """
        创建支付订单。

        Args:
            order_id: 商户订单号
            pet_name: 宠物名称（用于商品描述）
            plan: 套餐类型
            callback_url: 支付回调URL（可选，默认使用配置）

        Returns:
            dict: {"payment_url": str, "payment_id": str, "amount": float}

        Raises:
            RuntimeError: 创建订单失败
        """
        price = self.get_plan_price(plan)
        plan_names = {
            "basic": "基础版桌宠",
            "standard": "标准版桌宠+贴纸",
            "premium": "高级版全套",
        }
        title = f"PetPal-{pet_name}-{plan_names.get(plan, plan)}"

        if self.mode == "mock":
            return await self._mock_create_order(order_id, title, price)

        # 真实虎皮椒 API
        return await self._xunhu_create_order(order_id, title, price, callback_url)

    async def verify_callback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证支付回调。

        Args:
            params: 回调参数字典

        Returns:
            dict: {
                "valid": bool,
                "order_id": str,
                "trade_no": str,
                "amount": float,
                "status": str
            }

        Raises:
            RuntimeError: 验证失败
        """
        if self.mode == "mock":
            return self._mock_verify_callback(params)

        # 真实验证
        return await self._xunhu_verify_callback(params)

    # ==================== Mock 实现 ====================

    async def _mock_create_order(
        self, order_id: str, title: str, price: float
    ) -> Dict[str, Any]:
        """
        Mock 创建订单 - 直接返回模拟支付链接。

        用于开发测试，无需真实支付。
        """
        mock_payment_id = f"MOCK_{int(time.time())}_{order_id}"
        # 模拟支付链接（实际上点击即可"支付成功"）
        payment_url = f"/api/payment/mock_pay?order_id={order_id}&payment_id={mock_payment_id}&amount={price}"

        return {
            "payment_url": payment_url,
            "payment_id": mock_payment_id,
            "amount": price,
            "title": title,
            "mode": "mock"
        }

    def _mock_verify_callback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Mock 验证回调 - 直接返回成功"""
        return {
            "valid": True,
            "order_id": params.get("order_id", ""),
            "trade_no": params.get("trade_no", f"MOCK_TRADE_{int(time.time())}"),
            "amount": float(params.get("money", 0)),
            "status": "paid"
        }

    # ==================== 虎皮椒真实实现 ====================

    async def _xunhu_create_order(
        self,
        order_id: str,
        title: str,
        price: float,
        callback_url: str = None
    ) -> Dict[str, Any]:
        """
        虎皮椒 API 创建订单。
        
        文档: https://www.xunhupay.com/doc/api/pay.html
        """
        if not self.appid or not self.appsecret:
            raise RuntimeError("虎皮椒支付配置缺失，请检查 XUNHU_APPID 和 XUNHU_APPSECRET")

        nonce = int(time.time())
        notify_url = callback_url or settings.PAYMENT_CALLBACK_URL

        # 构建请求参数
        data = {
            "version": "1.1",
            "appid": self.appid,
            "trade_order_id": order_id,
            "total_fee": f"{price:.2f}",
            "title": title,
            "nonce": nonce,
            "notify_url": notify_url,
            "payment": "alipay",  # 默认支付宝
            "time": str(int(time.time())),
        }

        # 生成签名
        data["hash"] = self._generate_sign(data)

        resp = await self._client.post(self.api_url, data=data)
        resp.raise_for_status()
        result = resp.json()

        if result.get("errcode") != 0:
            raise RuntimeError(f"虎皮椒创建订单失败: {result.get('errmsg', '未知错误')}")

        return {
            "payment_url": result.get("url", ""),
            "payment_id": result.get("transaction_id", ""),
            "amount": price,
            "title": title,
            "mode": "production"
        }

    async def _xunhu_verify_callback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        虎皮椒回调验证。
        验证签名，确保回调来自虎皮椒。
        """
        received_hash = params.get("hash", "")

        # 移除 hash 字段后重新计算签名
        verify_params = {k: v for k, v in params.items() if k != "hash"}
        expected_hash = self._generate_sign(verify_params)

        is_valid = received_hash == expected_hash

        return {
            "valid": is_valid,
            "order_id": params.get("order_id", ""),
            "trade_no": params.get("trade_no", ""),
            "amount": float(params.get("money", 0)),
            "status": "paid" if params.get("status") == "OD" else "failed"
        }

    def _generate_sign(self, params: Dict[str, Any]) -> str:
        """
        生成虎皮椒 API 签名。

        签名规则：按参数名ASCII码排序，拼接后加 appsecret，做 MD5。

        Args:
            params: 请求参数字典

        Returns:
            str: MD5 签名
        """
        # 按 key 排序
        sorted_keys = sorted(params.keys())
        sign_str = ""
        for key in sorted_keys:
            value = params[key]
            if value is not None and value != "":
                sign_str += f"{key}={value}&"

        sign_str += f"appsecret={self.appsecret}"
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest()


# 全局单例
payment_service = PaymentService()
