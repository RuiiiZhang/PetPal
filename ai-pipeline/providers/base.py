"""
PetPal AI管线 - AI提供商抽象基类
定义所有AI图像生成提供商的统一接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class BaseProvider(ABC):
    """AI图像生成提供商抽象基类"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def generate_character(
        self,
        photo_path: str,
        prompt: str,
        negative_prompt: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """
        生成角色图
        Args:
            photo_path: 参考照片路径
            prompt: 正向prompt
            negative_prompt: 反向prompt
            output_path: 输出文件路径
            width: 图片宽度
            height: 图片高度
        Returns:
            生成的图片路径
        """
        pass

    @abstractmethod
    def generate_animation_frames(
        self,
        prompt: str,
        negative_prompt: str,
        output_path: str,
        frame_count: int,
        width: int = 1024,
        height: int = 256,
    ) -> str:
        """
        生成动画帧序列图（一张包含所有帧的横向排列图片）
        Args:
            prompt: 正向prompt（包含帧序列描述）
            negative_prompt: 反向prompt
            output_path: 输出文件路径
            frame_count: 帧数量
            width: 总图片宽度
            height: 总图片高度
        Returns:
            生成的帧序列图片路径
        """
        pass

    def health_check(self) -> bool:
        """检查API是否可用"""
        return True

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name})>"
