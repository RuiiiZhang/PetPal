"""
PetPal Pydantic 模型
定义 API 请求/响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ==================== 枚举定义 ====================

class PetStyle(str, Enum):
    """宠物风格"""
    CUTE = "cute"           # Q版可爱
    HANDDRAWN = "handdrawn" # 手绘风
    REALISTIC = "realistic" # 写实风


class OrderStatus(str, Enum):
    """订单状态流转"""
    CREATED = "created"
    DETECTED = "detected"
    CHARACTER_GENERATED = "character_generated"
    CHARACTER_CONFIRMED = "character_confirmed"
    ANIMATION_GENERATED = "animation_generated"
    ANIMATION_CONFIRMED = "animation_confirmed"
    PAID = "paid"
    BUILDING = "building"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentStatus(str, Enum):
    """支付状态"""
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


# ==================== 通用响应 ====================

class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = Field(0, description="0=成功, 1=失败")
    message: str = Field("success", description="提示信息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")


# ==================== 请求模型 ====================

class GenerateCharacterRequest(BaseModel):
    """生成角色预览请求"""
    order_id: str = Field(..., description="订单ID")


class ConfirmCharacterRequest(BaseModel):
    """确认角色请求"""
    order_id: str = Field(..., description="订单ID")
    approved: bool = Field(..., description="是否通过")


class GenerateAnimationRequest(BaseModel):
    """生成动画请求"""
    order_id: str = Field(..., description="订单ID")


class ConfirmAnimationRequest(BaseModel):
    """确认动画请求"""
    order_id: str = Field(..., description="订单ID")
    approved: bool = Field(..., description="是否通过")


class CreatePaymentRequest(BaseModel):
    """创建支付订单请求"""
    order_id: str = Field(..., description="订单ID")
    plan: str = Field("standard", description="套餐: basic/standard/premium")


class PaymentCallbackRequest(BaseModel):
    """支付回调请求（虎皮椒）"""
    trade_no: str = Field("", description="虎皮椒交易号")
    order_id: str = Field("", description="商户订单号")
    money: str = Field("", description="支付金额")
    status: str = Field("", description="支付状态")
    hash: str = Field("", description="签名校验")


# ==================== 响应数据模型 ====================

class UploadResponse(BaseModel):
    """上传接口响应数据"""
    order_id: str
    species: str
    breed: str
    features: Dict[str, Any]


class CharacterPreviewResponse(BaseModel):
    """角色预览响应数据"""
    preview_url: str


class ConfirmCharacterResponse(BaseModel):
    """确认角色响应数据"""
    status: str


class AnimationPreviewResponse(BaseModel):
    """动画预览响应数据"""
    preview_url: str
    actions: List[Dict[str, Any]]


class ConfirmAnimationResponse(BaseModel):
    """确认动画响应数据"""
    status: str


class PaymentCreateResponse(BaseModel):
    """创建支付响应数据"""
    payment_url: str
    payment_id: str


class OrderStatusResponse(BaseModel):
    """订单状态响应数据"""
    order_id: str
    status: str
    payment_status: str
    pet_name: str
    species: str
    breed: str
    style: str
    download_url: Optional[str] = None
    created_at: str


# ==================== AI 服务内部模型 ====================

class PetDetectionResult(BaseModel):
    """品种检测结果"""
    species: str
    breed: str
    confidence: float = 0.0
    features: Dict[str, Any] = {}


class CharacterGenerationResult(BaseModel):
    """角色生成结果"""
    image_path: str
    style: str
    description: str = ""


class AnimationGenerationResult(BaseModel):
    """动画生成结果"""
    frames_dir: str
    gif_path: str
    actions: List[Dict[str, Any]] = []


class SpriteSheetResult(BaseModel):
    """精灵表结果"""
    sprite_sheet_path: str
    frame_count: int
    frame_width: int = 128
    frame_height: int = 128
