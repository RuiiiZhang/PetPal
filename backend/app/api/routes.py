"""
PetPal API 路由
定义所有 API 端点
"""

import os
import json
import uuid
import shutil
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.schemas import (
    ApiResponse, GenerateCharacterRequest, ConfirmCharacterRequest,
    GenerateAnimationRequest, ConfirmAnimationRequest,
    CreatePaymentRequest, PaymentCallbackRequest
)
from app.models.db_models import Order
from app.services.pet_detector import pet_detector
from app.services.character_generator import character_generator
from app.services.animation_generator import animation_generator
from app.services.sprite_builder import sprite_builder
from app.services.desktop_pet_builder import desktop_pet_builder
from app.services.sticker_generator import sticker_generator
from app.services.package_builder import package_builder
from app.services.payment_service import payment_service

router = APIRouter()


# ==================== 辅助函数 ====================

def _success(data: dict = None, message: str = "success") -> dict:
    """构造成功响应"""
    return {"code": 0, "message": message, "data": data}


def _error(message: str, code: int = 1) -> dict:
    """构造错误响应"""
    return {"code": code, "message": message, "data": None}


def _get_order_or_404(db: Session, order_id: str) -> Order:
    """获取订单，不存在则抛出 404"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


# ==================== 健康检查 ====================

@router.get("/api/health")
async def health_check():
    """
    健康检查接口。
    用于负载均衡器或监控系统检查服务状态。
    """
    return _success({
        "status": "ok",
        "version": settings.APP_VERSION,
        "ai_provider": settings.AI_PROVIDER,
        "payment_mode": settings.PAYMENT_MODE,
        "timestamp": datetime.utcnow().isoformat()
    })


# ==================== 上传照片 ====================

@router.post("/api/upload")
async def upload_photo(
    photo: UploadFile = File(...),
    pet_name: str = Form("未命名"),
    style: str = Form("cute"),
    db: Session = Depends(get_db)
):
    """
    上传宠物照片，自动进行品种检测。

    接收参数:
        - photo: 宠物照片文件（支持 jpg/png/webp）
        - pet_name: 宠物名字
        - style: 风格选择 (cute/handdrawn/realistic)

    返回:
        - order_id: 订单ID
        - species: 识别的物种
        - breed: 识别的品种
        - features: 特征信息
    """
    # 验证风格
    valid_styles = ("cute", "handdrawn", "realistic")
    if style not in valid_styles:
        return _error(f"无效风格: {style}，可选: {', '.join(valid_styles)}")

    # 验证文件类型
    allowed_types = ("image/jpeg", "image/png", "image/webp")
    if photo.content_type not in allowed_types:
        return _error(f"不支持的文件类型: {photo.content_type}，支持: jpg/png/webp")

    # 生成订单ID
    order_id = str(uuid.uuid4())[:12]

    # 创建输出目录
    order_dir = os.path.join(settings.OUTPUT_DIR, order_id)
    os.makedirs(order_dir, exist_ok=True)

    # 保存上传文件
    upload_dir = os.path.join(settings.UPLOAD_DIR, order_id)
    os.makedirs(upload_dir, exist_ok=True)

    # 文件扩展名
    ext = os.path.splitext(photo.filename)[1] or ".jpg"
    photo_path = os.path.join(upload_dir, f"photo{ext}")

    with open(photo_path, "wb") as f:
        content = await photo.read()
        f.write(content)

    # 品种检测
    try:
        detection = await pet_detector.detect(photo_path)
    except Exception as e:
        # 检测失败不阻塞流程，使用默认值
        detection = type("Detection", (), {
            "species": "cat", "breed": "unknown",
            "confidence": 0.5, "features": {"error": str(e), "mock": True}
        })()

    # 创建订单记录
    order = Order(
        order_id=order_id,
        pet_name=pet_name,
        species=detection.species,
        breed=detection.breed,
        features=json.dumps(detection.features, ensure_ascii=False),
        style=style,
        photo_path=photo_path,
        status="detected",
    )
    db.add(order)
    db.commit()

    return _success({
        "order_id": order_id,
        "species": detection.species,
        "breed": detection.breed,
        "features": detection.features
    })


# ==================== 生成角色预览 ====================

@router.post("/api/generate-character")
async def generate_character(
    req: GenerateCharacterRequest,
    db: Session = Depends(get_db)
):
    """
    生成角色预览图。
    基于上传的宠物照片 + 品种信息 + 风格，调用 AI 生成角色。
    """
    order = _get_order_or_404(db, req.order_id)

    # 检查状态
    if order.status not in ("detected", "character_generated"):
        return _error(f"当前状态不允许生成角色: {order.status}")

    try:
        # 解析特征
        features = json.loads(order.features) if order.features else {}

        # 调用角色生成服务
        result = await character_generator.generate(
            order_id=order.order_id,
            species=order.species,
            breed=order.breed,
            style=order.style,
            features=features,
            photo_path=order.photo_path
        )

        # 更新订单
        order.character_path = result.image_path
        order.status = "character_generated"
        db.commit()

        return _success({
            "preview_url": f"/output/{order.order_id}/character_preview.png"
        })

    except Exception as e:
        order.status = "failed"
        db.commit()
        return _error(f"角色生成失败: {str(e)}")


# ==================== 确认角色 ====================

@router.post("/api/confirm-character")
async def confirm_character(
    req: ConfirmCharacterRequest,
    db: Session = Depends(get_db)
):
    """
    确认或重新生成角色。
    approved=true: 确认角色，进入动画生成阶段
    approved=false: 重新生成角色
    """
    order = _get_order_or_404(db, req.order_id)

    if order.status != "character_generated":
        return _error(f"当前状态不允许确认角色: {order.status}")

    if req.approved:
        order.status = "character_confirmed"
        db.commit()
        return _success({"status": "character_confirmed"})
    else:
        # 重新生成
        try:
            features = json.loads(order.features) if order.features else {}
            result = await character_generator.generate(
                order_id=order.order_id,
                species=order.species,
                breed=order.breed,
                style=order.style,
                features=features,
                photo_path=order.photo_path
            )
            order.character_path = result.image_path
            order.status = "character_generated"
            db.commit()
            return _success({"status": "regenerating", "preview_url": f"/output/{order.order_id}/character_preview.png"})
        except Exception as e:
            return _error(f"重新生成失败: {str(e)}")


# ==================== 生成动画 ====================

@router.post("/api/generate-animation")
async def generate_animation(
    req: GenerateAnimationRequest,
    db: Session = Depends(get_db)
):
    """
    生成动画帧序列。
    基于已确认的角色图，生成多个动作的动画。
    """
    order = _get_order_or_404(db, req.order_id)

    if order.status != "character_confirmed":
        return _error(f"当前状态不允许生成动画: {order.status}，请先确认角色")

    try:
        result = await animation_generator.generate(
            order_id=order.order_id,
            character_path=order.character_path,
            species=order.species,
            breed=order.breed,
            style=order.style
        )

        order.animation_path = result.gif_path
        order.status = "animation_generated"
        db.commit()

        return _success({
            "preview_url": f"/output/{order.order_id}/animation_preview.gif",
            "actions": result.actions
        })

    except Exception as e:
        order.status = "failed"
        db.commit()
        return _error(f"动画生成失败: {str(e)}")


# ==================== 确认动画 ====================

@router.post("/api/confirm-animation")
async def confirm_animation(
    req: ConfirmAnimationRequest,
    db: Session = Depends(get_db)
):
    """
    确认或重新生成动画。
    approved=true: 确认动画，进入支付阶段
    approved=false: 重新生成动画
    """
    order = _get_order_or_404(db, req.order_id)

    if order.status != "animation_generated":
        return _error(f"当前状态不允许确认动画: {order.status}")

    if req.approved:
        order.status = "animation_confirmed"
        db.commit()
        return _success({"status": "animation_confirmed"})
    else:
        try:
            result = await animation_generator.generate(
                order_id=order.order_id,
                character_path=order.character_path,
                species=order.species,
                breed=order.breed,
                style=order.style
            )
            order.animation_path = result.gif_path
            order.status = "animation_generated"
            db.commit()
            return _success({
                "status": "regenerating",
                "preview_url": f"/output/{order.order_id}/animation_preview.gif"
            })
        except Exception as e:
            return _error(f"重新生成失败: {str(e)}")


# ==================== 创建支付订单 ====================

@router.post("/api/payment/create")
async def create_payment(
    req: CreatePaymentRequest,
    db: Session = Depends(get_db)
):
    """
    创建支付订单。
    调用虎皮椒支付接口，返回支付链接。
    """
    order = _get_order_or_404(db, req.order_id)

    if order.status != "animation_confirmed":
        return _error(f"当前状态不允许支付: {order.status}，请先确认动画")

    try:
        result = await payment_service.create_order(
            order_id=order.order_id,
            pet_name=order.pet_name,
            plan=req.plan
        )

        # 更新订单支付信息
        order.plan = req.plan
        order.payment_amount = result["amount"]
        order.payment_id = result.get("payment_id", "")
        db.commit()

        return _success({
            "payment_url": result["payment_url"],
            "payment_id": result["payment_id"],
            "amount": result["amount"],
        })

    except Exception as e:
        return _error(f"创建支付订单失败: {str(e)}")


# ==================== 支付回调 ====================

@router.post("/api/payment/callback")
async def payment_callback(
    trade_no: str = Form(""),
    order_id: str = Form(""),
    money: str = Form(""),
    status: str = Form(""),
    hash: str = Form(""),
    db: Session = Depends(get_db)
):
    """
    虎皮椒支付回调接口。
    接收支付结果通知，更新订单状态。
    """
    try:
        # 验证回调签名
        params = {
            "trade_no": trade_no,
            "order_id": order_id,
            "money": money,
            "status": status,
            "hash": hash,
        }
        verify_result = await payment_service.verify_callback(params)

        if not verify_result["valid"]:
            return _error("签名验证失败")

        # 查找订单
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return _error("订单不存在")

        if order.payment_status == "paid":
            return _success({"message": "已处理"})

        # 更新支付状态
        order.payment_status = "paid"
        order.payment_id = verify_result.get("trade_no", trade_no)
        order.status = "paid"
        db.commit()

        # 自动开始构建产物
        await _build_delivery(order_id, db)

        return _success({"message": "回调处理成功"})

    except Exception as e:
        return _error(f"回调处理失败: {str(e)}")


# ==================== Mock 支付确认（测试用） ====================

@router.get("/api/payment/mock_pay")
async def mock_pay(
    order_id: str = Query(...),
    payment_id: str = Query(""),
    amount: float = Query(0),
    db: Session = Depends(get_db)
):
    """
    Mock 支付接口 - 直接模拟支付成功。
    仅在 payment_mode=mock 时有效。
    """
    if settings.PAYMENT_MODE != "mock":
        raise HTTPException(status_code=404, detail="非 Mock 模式，此接口不可用")

    order = _get_order_or_404(db, order_id)

    order.payment_status = "paid"
    order.payment_id = payment_id or f"MOCK_{int(datetime.utcnow().timestamp())}"
    order.payment_amount = amount or order.payment_amount
    order.status = "paid"
    db.commit()

    # 自动构建
    await _build_delivery(order_id, db)

    return _success({
        "message": "Mock 支付成功！",
        "order_id": order_id,
        "redirect": f"/api/order/{order_id}/status"
    })


# ==================== 查询订单状态 ====================

@router.get("/api/order/{order_id}/status")
async def get_order_status(
    order_id: str,
    db: Session = Depends(get_db)
):
    """
    查询订单状态。
    返回订单的当前处理进度和下载链接（如已完成）。
    """
    order = _get_order_or_404(db, order_id)

    data = {
        "order_id": order.order_id,
        "status": order.status,
        "payment_status": order.payment_status,
        "pet_name": order.pet_name,
        "species": order.species,
        "breed": order.breed,
        "style": order.style,
        "created_at": order.created_at.isoformat() if order.created_at else "",
        "download_url": None
    }

    # 如果已完成，提供下载链接
    if order.status == "completed" and order.result_path:
        data["download_url"] = f"/api/order/{order.order_id}/download"

    return _success(data)


# ==================== 下载产物 ====================

@router.get("/api/order/{order_id}/download")
async def download_result(
    order_id: str,
    db: Session = Depends(get_db)
):
    """
    下载最终交付物（ZIP包）。
    仅已支付且构建完成的订单可下载。
    """
    order = _get_order_or_404(db, order_id)

    # 检查支付状态
    if order.payment_status != "paid":
        return _error("订单未支付")

    # 检查是否已构建完成
    if order.status != "completed":
        return _error(f"产物尚未准备完成，当前状态: {order.status}")

    result_path = order.result_path
    if not result_path or not os.path.exists(result_path):
        return _error("产物文件不存在")

    return FileResponse(
        path=result_path,
        filename=f"{order.pet_name}_PetPal.zip",
        media_type="application/zip"
    )


# ==================== 内部构建流程 ====================

async def _build_delivery(order_id: str, db: Session):
    """
    内部函数：执行完整的产物构建流程。
    在支付成功后自动调用。

    流程：精灵表构建 → 桌宠打包 → 贴纸包生成 → 最终打包
    """
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        return

    try:
        order.status = "building"
        db.commit()

        output_dir = os.path.join(settings.OUTPUT_DIR, order_id)

        # 1. 构建精灵表
        frames_dir = os.path.join(output_dir, "frames")
        # 从动画生成结果获取动作列表
        actions = []
        if os.path.exists(frames_dir):
            for action_name in os.listdir(frames_dir):
                action_dir = os.path.join(frames_dir, action_name)
                if os.path.isdir(action_dir):
                    frame_files = [f for f in os.listdir(action_dir) if f.endswith(".png")]
                    actions.append({
                        "name": action_name,
                        "frame_count": len(frame_files),
                        "frame_dir": action_dir,
                        "fps": 8
                    })

        sprite_result = sprite_builder.build_sprite_sheet(
            order_id=order_id,
            frames_dir=frames_dir,
            actions=actions
        )

        # 2. 构建桌宠程序
        pet_dir = desktop_pet_builder.build(
            order_id=order_id,
            pet_name=order.pet_name,
            species=order.species,
            breed=order.breed,
            sprite_sheet_path=sprite_result["sprite_sheet_path"],
            sprite_metadata=sprite_result
        )

        # 3. 生成贴纸包
        sticker_result = sticker_generator.generate_sticker_pack(
            order_id=order_id,
            sprite_sheet_path=sprite_result["sprite_sheet_path"],
            sprite_metadata=sprite_result
        )

        # 4. 最终打包
        package_path = package_builder.build_package(
            order_id=order_id,
            pet_name=order.pet_name,
            desktop_pet_dir=pet_dir,
            sticker_pack_zip=sticker_result.get("sticker_pack_zip", ""),
            plan=order.plan or "standard"
        )

        # 更新订单
        order.result_path = package_path
        order.status = "completed"
        db.commit()

    except Exception as e:
        order.status = "failed"
        db.commit()
        # 不抛出，避免影响回调响应
        print(f"[PetPal] 构建失败 order_id={order_id}: {e}")
