"""
PetPal 数据库模块
SQLite 数据库初始化、Session 管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 需要
    echo=settings.DEBUG,
)

# Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM 基类
Base = declarative_base()


def init_db():
    """
    初始化数据库：创建所有表。
    在应用启动时调用。
    """
    # 导入所有模型以确保它们被注册到 Base.metadata
    from app.models import db_models  # noqa: F401
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    获取数据库 Session 的依赖注入函数。
    用于 FastAPI 的 Depends()。
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
