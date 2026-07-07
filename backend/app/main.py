"""
PetPal FastAPI 主入口
包含 CORS 配置、路由注册、启动/关闭事件
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router
from app.services.ai_provider import ai_provider
from app.services.pet_detector import pet_detector
from app.services.payment_service import payment_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # === 启动事件 ===
    print(f"\n{'='*50}")
    print(f"  🐾 PetPal Backend v{settings.APP_VERSION}")
    print(f"  📦 AI Provider: {settings.AI_PROVIDER}")
    print(f"  💰 Payment Mode: {settings.PAYMENT_MODE}")
    print(f"  📂 Upload Dir: {settings.UPLOAD_DIR}")
    print(f"  📂 Output Dir: {settings.OUTPUT_DIR}")
    print(f"  🗄️  Database: {settings.DATABASE_URL}")
    print(f"{'='*50}\n")

    # 初始化数据库
    init_db()
    print("✅ Database initialized")

    yield

    # === 关闭事件 ===
    print("\n🐾 PetPal shutting down...")
    await ai_provider.close()
    await pet_detector.close()
    await payment_service.close()
    print("👋 Goodbye!")


# 创建 FastAPI 应用
app = FastAPI(
    title="PetPal API",
    description="自动宠物桌宠搭建平台 - 上传宠物照片，AI生成角色和动画，打包桌宠程序和动态贴纸包",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# ==================== CORS 配置 ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # 前端开发服务器
        "http://localhost:5173",      # Vite 开发服务器
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://petpal.app",         # 生产域名
        "https://www.petpal.app",
        "*",                          # 开发阶段允许所有来源（生产环境应限制）
    ],
    allow_credentials=True,
    allow_methods=["*"],               # 允许所有 HTTP 方法
    allow_headers=["*"],               # 允许所有请求头
    expose_headers=["Content-Disposition"],  # 暴露下载头
)


# ==================== 路由注册 ====================

app.include_router(router, tags=["PetPal API"])


# ==================== 静态文件服务 ====================

# 挂载输出目录，用于预览图片和 GIF
if os.path.exists(settings.OUTPUT_DIR):
    app.mount("/output", StaticFiles(directory=settings.OUTPUT_DIR), name="output")

# 挂载上传目录（用于调试）
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ==================== 根路径 ====================

@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "name": "PetPal API",
        "version": settings.APP_VERSION,
        "description": "自动宠物桌宠搭建平台",
        "endpoints": {
            "health": "GET /api/health",
            "upload": "POST /api/upload",
            "generate_character": "POST /api/generate-character",
            "confirm_character": "POST /api/confirm-character",
            "generate_animation": "POST /api/generate-animation",
            "confirm_animation": "POST /api/confirm-animation",
            "create_payment": "POST /api/payment/create",
            "payment_callback": "POST /api/payment/callback",
            "order_status": "GET /api/order/{order_id}/status",
            "download": "GET /api/order/{order_id}/download",
            "docs": "/docs",
        }
    }


# ==================== 全局异常处理 ====================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    import traceback
    traceback.print_exc()
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "code": 1,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None
        }
    )


# ==================== 启动入口 ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
