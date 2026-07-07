"""
动画生成服务
调用 AI 视频 API 生成动作帧序列
"""

import os
import json
from typing import Dict, Any, List
from app.core.config import settings
from app.services.ai_provider import ai_provider
from app.models.schemas import AnimationGenerationResult


# 默认动作列表
DEFAULT_ACTIONS = [
    {"name": "idle", "frames": 8, "description": "待机呼吸动画"},
    {"name": "walk", "frames": 8, "description": "行走循环"},
    {"name": "sit", "frames": 4, "description": "坐下"},
    {"name": "sleep", "frames": 6, "description": "睡觉"},
    {"name": "happy", "frames": 6, "description": "开心跳跃"},
    {"name": "wave", "frames": 6, "description": "挥手打招呼"},
    {"name": "eat", "frames": 6, "description": "吃东西"},
    {"name": "play", "frames": 8, "description": "玩耍"},
    {"name": "look_around", "frames": 6, "description": "左右张望"},
    {"name": "yawn", "frames": 4, "description": "打哈欠"},
]


class AnimationGenerator:
    """动画生成服务"""

    async def generate(
        self,
        order_id: str,
        character_path: str,
        species: str,
        breed: str,
        style: str,
        custom_actions: List[Dict] = None
    ) -> AnimationGenerationResult:
        """
        生成角色动画帧序列。

        Args:
            order_id: 订单ID
            character_path: 角色图片路径
            species: 物种
            breed: 品种
            style: 风格
            custom_actions: 自定义动作列表（可选）

        Returns:
            AnimationGenerationResult: 包含帧目录、GIF路径、动作列表

        Raises:
            RuntimeError: 生成失败时抛出
        """
        # 输出目录
        output_dir = os.path.join(settings.OUTPUT_DIR, order_id)
        frames_dir = os.path.join(output_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        # 选择动作列表
        actions = custom_actions or self._get_default_actions(species)

        try:
            # 调用 AI 生成动画帧
            result = await ai_provider.generate_animation_frames(
                image_path=character_path,
                actions=actions,
                output_dir=frames_dir
            )

            # 生成预览 GIF
            gif_path = os.path.join(output_dir, "animation_preview.gif")
            await self._create_preview_gif(result["frames_dir"], gif_path, actions)

            return AnimationGenerationResult(
                frames_dir=result["frames_dir"],
                gif_path=gif_path,
                actions=result.get("actions", actions)
            )

        except Exception as e:
            raise RuntimeError(f"动画生成失败: {str(e)}")

    def _get_default_actions(self, species: str) -> List[Dict]:
        """
        根据物种返回默认动作列表。
        不同物种有略微不同的默认动作。

        Args:
            species: 物种

        Returns:
            list: 动作列表
        """
        # 基础动作（所有物种通用）
        base_actions = [
            {"name": "idle", "frames": 8},
            {"name": "walk", "frames": 8},
            {"name": "sit", "frames": 4},
            {"name": "sleep", "frames": 6},
            {"name": "happy", "frames": 6},
        ]

        # 物种特定动作
        species_actions = {
            "cat": [
                {"name": "wave", "frames": 6},
                {"name": "lick", "frames": 4},
                {"name": "stretch", "frames": 6},
                {"name": "pounce", "frames": 6},
                {"name": "yawn", "frames": 4},
            ],
            "dog": [
                {"name": "wave", "frames": 6},
                {"name": "fetch", "frames": 6},
                {"name": "beg", "frames": 4},
                {"name": "shake", "frames": 6},
                {"name": "pant", "frames": 4},
            ],
            "bird": [
                {"name": "fly", "frames": 8},
                {"name": "sing", "frames": 6},
                {"name": "hop", "frames": 6},
                {"name": "preen", "frames": 4},
                {"name": "head_bob", "frames": 6},
            ],
            "rabbit": [
                {"name": "hop", "frames": 6},
                {"name": "wiggle_nose", "frames": 4},
                {"name": "binky", "frames": 8},
                {"name": "flop", "frames": 4},
                {"name": "eat", "frames": 6},
            ],
        }

        specific = species_actions.get(species, species_actions.get("cat", []))
        return base_actions + specific

    async def _create_preview_gif(
        self, frames_dir: str, gif_path: str, actions: list
    ) -> str:
        """
        从帧目录创建预览 GIF（取 idle 动作作为预览）。

        Args:
            frames_dir: 帧目录
            gif_path: 输出 GIF 路径
            actions: 动作列表

        Returns:
            str: GIF 文件路径
        """
        from PIL import Image

        # 优先使用 idle 动作
        idle_dir = os.path.join(frames_dir, "idle")
        if not os.path.exists(idle_dir):
            # 使用第一个动作目录
            subdirs = [d for d in os.listdir(frames_dir) if os.path.isdir(os.path.join(frames_dir, d))]
            if subdirs:
                idle_dir = os.path.join(frames_dir, subdirs[0])
            else:
                # 没有帧目录，创建简单的占位 GIF
                img = Image.new("RGBA", (128, 128), (200, 200, 200, 255))
                img.save(gif_path, "GIF")
                return gif_path

        # 收集帧图片
        frame_files = sorted([
            os.path.join(idle_dir, f)
            for f in os.listdir(idle_dir)
            if f.endswith(".png")
        ])

        if not frame_files:
            img = Image.new("RGBA", (128, 128), (200, 200, 200, 255))
            img.save(gif_path, "GIF")
            return gif_path

        # 生成 GIF
        frames = []
        for f_path in frame_files:
            frame = Image.open(f_path).convert("RGBA")
            # 转为 P 模式（GIF 需要）
            # 创建白色背景
            bg = Image.new("RGBA", frame.size, (255, 255, 255, 255))
            bg.paste(frame, mask=frame.split()[3])
            frames.append(bg.convert("RGB").quantize(colors=256))

        # 保存为 GIF
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=125,  # 8fps = 125ms per frame
            loop=0
        )

        return gif_path


# 全局单例
animation_generator = AnimationGenerator()
