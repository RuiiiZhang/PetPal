"""
精灵表构建服务
将动画帧去背景后排列成精灵表 PNG 和 GIF
"""

import os
import glob
from typing import List, Dict, Any, Tuple
from PIL import Image
from app.core.config import settings


class SpriteBuilder:
    """精灵表构建服务"""

    def build_sprite_sheet(
        self,
        order_id: str,
        frames_dir: str,
        actions: List[Dict[str, Any]],
        frame_size: Tuple[int, int] = (128, 128),
        background_removal: bool = True
    ) -> Dict[str, Any]:
        """
        从帧目录构建精灵表。

        Args:
            order_id: 订单ID
            frames_dir: 帧序列根目录
            actions: 动作列表 [{"name": "idle", "frame_count": 8, "frame_dir": "..."}]
            frame_size: 单帧尺寸 (width, height)
            background_removal: 是否去除背景

        Returns:
            dict: {"sprite_sheet_path": str, "frame_count": int, "frame_width": int, "frame_height": int}

        Raises:
            RuntimeError: 构建失败时抛出
        """
        try:
            output_dir = os.path.join(settings.OUTPUT_DIR, order_id)
            os.makedirs(output_dir, exist_ok=True)

            # 收集所有帧
            all_frames = []
            action_layout = []  # 记录每个动作在精灵表中的位置

            for action in actions:
                action_name = action.get("name", "unknown")
                frame_dir = action.get("frame_dir", os.path.join(frames_dir, action_name))

                if not os.path.exists(frame_dir):
                    continue

                # 收集并排序帧文件
                frame_files = sorted(glob.glob(os.path.join(frame_dir, "*.png")))

                if not frame_files:
                    continue

                start_idx = len(all_frames)

                for f_path in frame_files:
                    img = Image.open(f_path).convert("RGBA")

                    # 去背景处理
                    if background_removal:
                        img = self._remove_background(img)

                    # 调整到标准帧尺寸
                    img = img.resize(frame_size, Image.Resampling.LANCZOS)
                    all_frames.append(img)

                action_layout.append({
                    "name": action_name,
                    "start_frame": start_idx,
                    "frame_count": len(frame_files),
                    "fps": action.get("fps", 8)
                })

            if not all_frames:
                raise RuntimeError("没有找到有效的帧图片")

            # 计算精灵表布局
            frame_w, frame_h = frame_size
            cols = max(action.get("frame_count", 1) for action in action_layout) if action_layout else 4
            rows = len(action_layout) if action_layout else 1

            # 创建精灵表
            sheet_w = cols * frame_w
            sheet_h = rows * frame_h
            sprite_sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

            # 按行动作排列帧
            for row_idx, action_info in enumerate(action_layout):
                for col_idx in range(action_info["frame_count"]):
                    frame_idx = action_info["start_frame"] + col_idx
                    if frame_idx < len(all_frames):
                        x = col_idx * frame_w
                        y = row_idx * frame_h
                        sprite_sheet.paste(all_frames[frame_idx], (x, y))

            # 保存精灵表 PNG
            sprite_sheet_path = os.path.join(output_dir, "sprite_sheet.png")
            sprite_sheet.save(sprite_sheet_path, "PNG")

            # 保存布局元数据
            metadata = {
                "frame_width": frame_w,
                "frame_height": frame_h,
                "columns": cols,
                "rows": rows,
                "total_frames": len(all_frames),
                "actions": action_layout
            }

            metadata_path = os.path.join(output_dir, "sprite_metadata.json")
            import json
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            return {
                "sprite_sheet_path": sprite_sheet_path,
                "metadata_path": metadata_path,
                "frame_count": len(all_frames),
                "frame_width": frame_w,
                "frame_height": frame_h,
                "actions": action_layout
            }

        except Exception as e:
            raise RuntimeError(f"精灵表构建失败: {str(e)}")

    def _remove_background(self, img: Image.Image) -> Image.Image:
        """
        简易背景去除。
        基于四角颜色采样，将相似颜色像素变为透明。

        Args:
            img: RGBA 图片

        Returns:
            Image: 去背景后的图片
        """
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        pixels = img.load()
        w, h = img.size

        # 采样四角颜色
        corners = [
            pixels[0, 0],
            pixels[w - 1, 0],
            pixels[0, h - 1],
            pixels[w - 1, h - 1],
        ]

        # 计算平均背景色
        bg_r = sum(c[0] for c in corners) // 4
        bg_g = sum(c[1] for c in corners) // 4
        bg_b = sum(c[2] for c in corners) // 4

        # 颜色距离阈值
        threshold = 50

        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                distance = ((r - bg_r) ** 2 + (g - bg_g) ** 2 + (b - bg_b) ** 2) ** 0.5
                if distance < threshold:
                    pixels[x, y] = (r, g, b, 0)  # 透明

        return img


# 全局单例
sprite_builder = SpriteBuilder()
