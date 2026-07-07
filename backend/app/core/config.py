"""
PetPal 配置管理模块
通过环境变量或 .env 文件管理所有配置项
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


# 项目根目录（backend/）
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """PetPal 全局配置"""

    # ==================== 基础配置 ====================
    APP_NAME: str = "PetPal"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "petpal-secret-key-change-in-production"

    # ==================== 数据库配置 ====================
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'petpal.db'}"

    # ==================== 文件存储路径 ====================
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    OUTPUT_DIR: str = str(BASE_DIR / "output")
    DATA_DIR: str = str(BASE_DIR / "data")

    # ==================== AI 服务配置 ====================
    # AI 提供商选择: "flux" / "midjourney" / "coze" / "mock"
    AI_PROVIDER: str = "mock"

    # 百度 AI 宠物识别 API（品种检测）
    BAIDU_API_KEY: str = ""
    BAIDU_SECRET_KEY: str = ""

    # Flux 生图 API
    FLUX_API_KEY: str = ""
    FLUX_API_URL: str = "https://api.flux.ai/v1/generate"

    # Midjourney 代理 API
    MJ_API_KEY: str = ""
    MJ_API_URL: str = "https://api.midjourney-proxy.com/v1/generate"

    # Coze 内置 AI
    COZE_API_KEY: str = ""
    COZE_API_URL: str = "https://api.coze.cn/v1/workflow/run"

    # AI 视频/动画生成 API
    AI_VIDEO_API_KEY: str = ""
    AI_VIDEO_API_URL: str = ""

    # ==================== 支付配置 ====================
    # 虎皮椒支付
    # 支付模式: "production" 真实支付 / "mock" 模拟支付（测试用）
    PAYMENT_MODE: str = "mock"

    XUNHU_APPID: str = ""
    XUNHU_APPSECRET: str = ""
    XUNHU_API_URL: str = "https://api.xunhupay.com/payment/do.html"
    PAYMENT_CALLBACK_URL: str = "https://your-domain.com/api/payment/callback"

    # ==================== 套餐价格 ====================
    PRICE_BASIC: float = 19.9      # 基础版：桌宠程序
    PRICE_STANDARD: float = 29.9   # 标准版：桌宠 + 贴纸包
    PRICE_PREMIUM: float = 49.9    # 高级版：桌宠 + 贴纸包 + 源文件

    # ==================== 桌宠构建配置 ====================
    TAURI_TEMPLATE_DIR: str = str(BASE_DIR / "templates" / "tauri")

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# 全局配置单例
settings = Settings()

# 确保必要目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.DATA_DIR, exist_ok=True)
