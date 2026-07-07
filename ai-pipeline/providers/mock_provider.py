"""
PetPal AI管线 - Mock提供商（测试用）
使用PIL绘制简单的测试角色和帧序列，无需调用任何外部API
"""

import sys
import math
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont
from providers.base import BaseProvider
from config import FRAME_WIDTH, FRAME_HEIGHT


class MockProvider(BaseProvider):
    """
    Mock提供商 - 用于测试和开发
    使用PIL绘制简单的彩色形状作为测试图片
    """

    def __init__(self):
        super().__init__("mock")
        # 为每个宠物生成一致的颜色方案
        self._color_cache = {}

    def _get_pet_colors(self, identifier: str = "default"):
        """获取宠物的配色方案（缓存保证一致性）"""
        if identifier not in self._color_cache:
            random.seed(hash(identifier) % (2**32))
            self._color_cache[identifier] = {
                "body": (
                    random.randint(150, 255),
                    random.randint(100, 200),
                    random.randint(80, 180),
                ),
                "eye": (
                    random.randint(30, 100),
                    random.randint(100, 200),
                    random.randint(150, 255),
                ),
                "nose": (255, random.randint(120, 180), random.randint(130, 170)),
                "accent": (
                    random.randint(200, 255),
                    random.randint(180, 230),
                    random.randint(50, 120),
                ),
            }
        return self._color_cache[identifier]

    def _draw_cat(self, draw: ImageDraw.ImageDraw, cx: int, cy: int,
                  size: int, colors: dict, frame_idx: int = 0,
                  total_frames: int = 1, action: str = "sit"):
        """绘制一个简化的猫咪"""
        body_color = colors["body"]
        eye_color = colors["eye"]
        nose_color = colors["nose"]
        s = size // 20  # 缩放因子

        # 身体（椭圆）
        body_w, body_h = s * 8, s * 6
        draw.ellipse(
            [cx - body_w, cy - body_h, cx + body_w, cy + body_h],
            fill=body_color, outline=(0, 0, 0, 128), width=max(1, s // 2)
        )

        # 头部（圆形）
        head_r = s * 6
        head_cy = cy - s * 8
        draw.ellipse(
            [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
            fill=body_color, outline=(0, 0, 0, 128), width=max(1, s // 2)
        )

        # 耳朵（三角形）
        ear_size = s * 3
        # 左耳
        draw.polygon([
            (cx - head_r + ear_size // 2, head_cy - head_r + ear_size),
            (cx - head_r - ear_size // 2, head_cy - head_r - ear_size),
            (cx - head_r + ear_size * 2, head_cy - head_r - ear_size // 2),
        ], fill=body_color, outline=(0, 0, 0, 128))
        # 右耳
        draw.polygon([
            (cx + head_r - ear_size // 2, head_cy - head_r + ear_size),
            (cx + head_r + ear_size // 2, head_cy - head_r - ear_size),
            (cx + head_r - ear_size * 2, head_cy - head_r - ear_size // 2),
        ], fill=body_color, outline=(0, 0, 0, 128))

        # 眼睛
        eye_r = s * 2
        eye_y = head_cy - s
        draw.ellipse(
            [cx - s * 3 - eye_r, eye_y - eye_r, cx - s * 3 + eye_r, eye_y + eye_r],
            fill=(255, 255, 255), outline=(0, 0, 0)
        )
        draw.ellipse(
            [cx - s * 3 - eye_r // 2, eye_y - eye_r // 2,
             cx - s * 3 + eye_r // 2, eye_y + eye_r // 2],
            fill=eye_color
        )
        # 高光
        draw.ellipse(
            [cx - s * 3 - eye_r // 4, eye_y - eye_r // 2,
             cx - s * 3, eye_y - eye_r // 4],
            fill=(255, 255, 255)
        )

        draw.ellipse(
            [cx + s * 3 - eye_r, eye_y - eye_r, cx + s * 3 + eye_r, eye_y + eye_r],
            fill=(255, 255, 255), outline=(0, 0, 0)
        )
        draw.ellipse(
            [cx + s * 3 - eye_r // 2, eye_y - eye_r // 2,
             cx + s * 3 + eye_r // 2, eye_y + eye_r // 2],
            fill=eye_color
        )
        draw.ellipse(
            [cx + s * 3 - eye_r // 4, eye_y - eye_r // 2,
             cx + s * 3, eye_y - eye_r // 4],
            fill=(255, 255, 255)
        )

        # 鼻子
        nose_y = head_cy + s * 2
        draw.polygon([
            (cx, nose_y + s),
            (cx - s, nose_y),
            (cx + s, nose_y),
        ], fill=nose_color)

        # 嘴巴
        draw.arc(
            [cx - s * 2, nose_y + s, cx, nose_y + s * 3],
            start=0, end=180, fill=(0, 0, 0), width=max(1, s // 2)
        )
        draw.arc(
            [cx, nose_y + s, cx + s * 2, nose_y + s * 3],
            start=0, end=180, fill=(0, 0, 0), width=max(1, s // 2)
        )

        # 尾巴（根据帧数有动画效果）
        tail_offset = math.sin(frame_idx / max(total_frames - 1, 1) * math.pi * 2) * s * 3
        tail_start_x = cx + body_w - s
        tail_start_y = cy - s * 2
        tail_end_x = tail_start_x + s * 6 + tail_offset
        tail_end_y = tail_start_y - s * 4
        draw.line(
            [tail_start_x, tail_start_y, tail_end_x, tail_end_y],
            fill=body_color, width=max(2, s * 2)
        )
        # 尾巴尖端
        draw.ellipse(
            [tail_end_x - s, tail_end_y - s, tail_end_x + s, tail_end_y + s],
            fill=colors["accent"]
        )

        # 前爪
        paw_y = cy + body_h - s
        draw.ellipse(
            [cx - s * 4, paw_y, cx - s * 2, paw_y + s * 2],
            fill=body_color, outline=(0, 0, 0, 128)
        )
        draw.ellipse(
            [cx + s * 2, paw_y, cx + s * 4, paw_y + s * 2],
            fill=body_color, outline=(0, 0, 0, 128)
        )

    def _draw_dog(self, draw: ImageDraw.ImageDraw, cx: int, cy: int,
                  size: int, colors: dict, frame_idx: int = 0,
                  total_frames: int = 1, action: str = "sit"):
        """绘制一个简化的狗狗"""
        body_color = colors["body"]
        eye_color = colors["eye"]
        nose_color = colors["nose"]
        s = size // 20

        # 身体（更圆润）
        body_w, body_h = s * 9, s * 7
        draw.ellipse(
            [cx - body_w, cy - body_h, cx + body_w, cy + body_h],
            fill=body_color, outline=(0, 0, 0, 128), width=max(1, s // 2)
        )

        # 头部（圆形，更大）
        head_r = s * 7
        head_cy = cy - s * 9
        draw.ellipse(
            [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
            fill=body_color, outline=(0, 0, 0, 128), width=max(1, s // 2)
        )

        # 耳朵（下垂的椭圆）
        ear_w, ear_h = s * 3, s * 5
        # 左耳
        draw.ellipse(
            [cx - head_r - ear_w // 2, head_cy - ear_h // 2,
             cx - head_r + ear_w, head_cy + ear_h],
            fill=tuple(max(0, c - 30) for c in body_color), outline=(0, 0, 0, 128)
        )
        # 右耳
        draw.ellipse(
            [cx + head_r - ear_w, head_cy - ear_h // 2,
             cx + head_r + ear_w // 2, head_cy + ear_h],
            fill=tuple(max(0, c - 30) for c in body_color), outline=(0, 0, 0, 128)
        )

        # 眼睛（更圆更大）
        eye_r = s * 2
        eye_y = head_cy - s
        for ex in [cx - s * 3, cx + s * 3]:
            draw.ellipse(
                [ex - eye_r, eye_y - eye_r, ex + eye_r, eye_y + eye_r],
                fill=(255, 255, 255), outline=(0, 0, 0)
            )
            draw.ellipse(
                [ex - eye_r // 2, eye_y - eye_r // 2,
                 ex + eye_r // 2, eye_y + eye_r // 2],
                fill=eye_color
            )
            draw.ellipse(
                [ex - eye_r // 4, eye_y - eye_r // 2,
                 ex, eye_y - eye_r // 4],
                fill=(255, 255, 255)
            )

        # 鼻子（大圆鼻）
        nose_y = head_cy + s * 2
        nose_r = s * 2
        draw.ellipse(
            [cx - nose_r, nose_y - nose_r, cx + nose_r, nose_y + nose_r],
            fill=nose_color, outline=(0, 0, 0)
        )

        # 嘴巴（开心的笑脸）
        mouth_y = nose_y + nose_r
        draw.arc(
            [cx - s * 3, mouth_y, cx + s * 3, mouth_y + s * 3],
            start=10, end=170, fill=(0, 0, 0), width=max(1, s // 2)
        )
        # 舌头
        if action in ("walk", "fetch", "spin"):
            tongue_offset = math.sin(frame_idx * 1.5) * s
            draw.ellipse(
                [cx - s + tongue_offset, mouth_y + s,
                 cx + s + tongue_offset, mouth_y + s * 3],
                fill=(255, 120, 120)
            )

        # 尾巴（摇摆动画）
        tail_angle = math.sin(frame_idx / max(total_frames - 1, 1) * math.pi * 2) * 0.5
        tail_start_x = cx + body_w - s * 2
        tail_start_y = cy - s * 3
        tail_len = s * 7
        tail_end_x = tail_start_x + math.cos(tail_angle - 0.8) * tail_len
        tail_end_y = tail_start_y + math.sin(tail_angle - 0.8) * tail_len
        draw.line(
            [tail_start_x, tail_start_y, tail_end_x, tail_end_y],
            fill=body_color, width=max(2, s * 2)
        )

        # 爪子
        paw_y = cy + body_h - s
        for px_off in [-s * 4, -s * 1, s * 1, s * 4]:
            draw.ellipse(
                [cx + px_off - s, paw_y, cx + px_off + s, paw_y + s * 2],
                fill=body_color, outline=(0, 0, 0, 128)
            )

    def generate_character(
        self,
        photo_path: str,
        prompt: str,
        negative_prompt: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """生成角色图（Mock版 - 用PIL绘制简单形状）"""
        # 根据prompt推断物种
        species = "cat" if "cat" in prompt.lower() else "dog"
        identifier = photo_path or "default"
        colors = self._get_pet_colors(identifier)

        # 创建透明背景图
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = width // 2, height // 2 + 30
        size = min(width, height)

        if species == "cat":
            self._draw_cat(draw, cx, cy, size, colors)
        else:
            self._draw_dog(draw, cx, cy, size, colors)

        # 保存
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output), "PNG")
        return str(output)

    def generate_animation_frames(
        self,
        prompt: str,
        negative_prompt: str,
        output_path: str,
        frame_count: int,
        width: int = 1024,
        height: int = 256,
    ) -> str:
        """生成帧序列图（Mock版）"""
        species = "cat" if "cat" in prompt.lower() else "dog"
        colors = self._get_pet_colors(prompt[:50])

        # 每个帧的尺寸
        frame_w = width // frame_count
        frame_h = height

        # 创建横向帧序列图
        img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # 绘制每一帧
        for i in range(frame_count):
            frame_cx = frame_w * i + frame_w // 2
            frame_cy = frame_h // 2 + 10
            size = min(frame_w, frame_h) - 10

            if species == "cat":
                self._draw_cat(draw, frame_cx, frame_cy, size, colors,
                              frame_idx=i, total_frames=frame_count)
            else:
                self._draw_dog(draw, frame_cx, frame_cy, size, colors,
                              frame_idx=i, total_frames=frame_count)

            # 帧分隔线
            if i > 0:
                line_x = frame_w * i
                draw.line(
                    [line_x, 0, line_x, height],
                    fill=(200, 200, 200, 128), width=1
                )

        # 保存
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output), "PNG")
        return str(output)

    def health_check(self) -> bool:
        return True


# ============================================================
# 命令行测试
# ============================================================
if __name__ == "__main__":
    print("🧪 MockProvider 测试")
    provider = MockProvider()

    # 测试角色生成
    test_output = Path(__file__).parent.parent / "output" / "test_mock"
    char_path = provider.generate_character(
        photo_path="/fake/photo.jpg",
        prompt="a cute chibi cat with orange tabby coloring",
        negative_prompt="",
        output_path=str(test_output / "character.png"),
        width=256,
        height=256,
    )
    print(f"  ✅ 角色图: {char_path}")

    # 测试帧序列生成
    frames_path = provider.generate_animation_frames(
        prompt="a chibi cat walking, 4 frames",
        negative_prompt="",
        output_path=str(test_output / "frames.png"),
        frame_count=4,
        width=512,
        height=128,
    )
    print(f"  ✅ 帧序列: {frames_path}")
    print("  完成!")
