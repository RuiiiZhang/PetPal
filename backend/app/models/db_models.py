"""
PetPal SQLAlchemy ORM 模型
定义数据库表结构
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.core.database import Base


class Order(Base):
    """
    订单表 - 核心业务表
    记录从上传到交付的完整订单生命周期
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 订单唯一标识（UUID）
    order_id = Column(String(64), unique=True, index=True, nullable=False)

    # ==================== 宠物信息 ====================
    pet_name = Column(String(100), nullable=False, default="未命名")
    species = Column(String(50), default="")
    breed = Column(String(100), default="")
    features = Column(Text, default="{}")
    style = Column(String(20), default="cute")

    # ==================== 文件路径 ====================
    photo_path = Column(String(500), default="")
    character_path = Column(String(500), default="")
    animation_path = Column(String(500), default="")
    result_path = Column(String(500), default="")

    # ==================== 状态 ====================
    status = Column(String(30), default="created", nullable=False)
    payment_status = Column(String(20), default="unpaid", nullable=False)

    # ==================== 支付信息 ====================
    payment_id = Column(String(100), default="")
    payment_amount = Column(Float, default=0.0)
    plan = Column(String(20), default="standard")

    # ==================== 时间戳 ====================
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Order(order_id={self.order_id}, status={self.status})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "order_id": self.order_id,
            "pet_name": self.pet_name,
            "species": self.species,
            "breed": self.breed,
            "style": self.style,
            "status": self.status,
            "payment_status": self.payment_status,
            "photo_path": self.photo_path,
            "character_path": self.character_path,
            "animation_path": self.animation_path,
            "result_path": self.result_path,
            "plan": self.plan,
            "payment_amount": self.payment_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
