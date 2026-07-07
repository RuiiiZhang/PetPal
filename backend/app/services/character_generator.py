"""
角色生成服务
调用 AI 生图 API 生成 Q版/手绘/写实 风格的角色预览图
"""

import os
from typing import Dict, Any
from app.core.config import settings
from app.services.ai_provider import ai_provider
from app.models.schemas import CharacterGenerationResult


# 风格 prompt 模板
STYLE_PROMPTS = {
    "cute": (
        "A super cute chibi style pet character, kawaii, big eyes, small body, "
        "round shape, pastel colors, pixel art inspired, game sprite, "
        "transparent background, front view, full body, {description}"
    ),
    "handdrawn": (
        "A hand-drawn style pet character illustration, watercolor texture, "
        "soft lines, artistic, cozy feeling, game sprite, transparent background, "
        "front view, full body, {description}"
    ),
    "realistic": (
        "A semi-realistic pet character, detailed fur texture, natural proportions, "
        "studio lighting, high quality render, game sprite, transparent background, "
        "front view, full body, {description}"
    ),
}

# 负面提示词
NEGATIVE_PROMPT = (
    "blurry, low quality, deformed, ugly, bad anatomy, watermark, text, "
    "background, multiple characters, cropped"
)


class CharacterGenerator:
    """角色生成服务"""

    async def generate(
        self,
        order_id: str,
        species: str,
        breed: str,
        style: str,
        features: Dict[str, Any],
        photo_path: str = ""
    ) -> CharacterGenerationResult:
        """
        生成宠物角色预览图。

        Args:
            order_id: 订单ID
            species: 物种（cat/dog/...）
            breed: 品种
            style: 风格（cute/handdrawn/realistic）
            features: 特征描述字典
            photo_path: 原始照片路径（用于图生图）

        Returns:
            CharacterGenerationResult: 包含生成的图片路径

        Raises:
            RuntimeError: 生成失败时抛出
        """
        # 构建输出路径
        output_dir = os.path.join(settings.OUTPUT_DIR, order_id)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "character_preview.png")

        # 构建 prompt
        description = self._build_description(species, breed, features)
        prompt_template = STYLE_PROMPTS.get(style, STYLE_PROMPTS["cute"])
        prompt = prompt_template.format(description=description)

        try:
            if photo_path and os.path.exists(photo_path):
                # 有参考图时，使用图生图
                image_path = await ai_provider.image_to_image(
                    image_path=photo_path,
                    prompt=prompt,
                    output_path=output_path,
                    strength=0.65
                )
            else:
                # 纯文生图
                image_path = await ai_provider.text_to_image(
                    prompt=prompt,
                    output_path=output_path,
                    width=512,
                    height=512,
                    negative_prompt=NEGATIVE_PROMPT
                )

            return CharacterGenerationResult(
                image_path=image_path,
                style=style,
                description=description
            )

        except Exception as e:
            raise RuntimeError(f"角色生成失败: {str(e)}")

    def _build_description(
        self, species: str, breed: str, features: Dict[str, Any]
    ) -> str:
        """
        根据宠物信息构建 AI 描述文本。

        Args:
            species: 物种
            breed: 品种
            features: 特征字典

        Returns:
            str: 描述文本
        """
        parts = [f"a {breed} {species}"]

        # 添加颜色信息
        color = features.get("color", "")
        if color:
            parts.append(f"with {color} fur")

        # 添加体型信息
        size = features.get("size", "")
        if size:
            parts.append(f"{size} sized")

        # 添加其他特征
        if features.get("top_name"):
            parts.append(f"breed: {features['top_name']}")

        return ", ".join(parts)


# 全局单例
character_generator = CharacterGenerator()
