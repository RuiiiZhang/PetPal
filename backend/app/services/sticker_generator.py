"""
贴纸包生成服务
从精灵表切割出多个独立 GIF 贴纸
"""

import os
import json
from typing import Dict, Any, List, Tuple
from PIL import Image
from app.core.config import settings


class StickerGenerator:
    """动态贴纸包生成服务"""

    def generate_sticker_pack(
        self,
        order_id: str,
        sprite_sheet_path: str,
        sprite_metadata: Dict[str, Any],
        sticker_count: int = 10
    ) -> Dict[str, Any]:
        """
        从精灵表生成动态贴纸包。

        将精灵表中的每个动作切割为独立的 GIF 动画贴纸。

        Args:
            order_id: 订单ID
            sprite_sheet_path: 精灵表图片路径
            sprite_metadata: 精灵表元数据
            sticker_count: 期望生成的贴纸数量（实际取所有动作）

        Returns:
            dict: {
                "sticker_dir": str,       # 贴纸目录
                "sticker_pack_zip": str,   # 贴纸包ZIP路径
                "sticker_count": int,      # 实际生成数量
                "stickers": list           # 贴纸列表
            }

        Raises:
            RuntimeError: 生成失败时抛出
        """
        try:
            output_dir = os.path.join(settings.OUTPUT_DIR, order_id)
            sticker_dir = os.path.join(output_dir, "stickers")
            os.makedirs(sticker_dir, exist_ok=True)

            # 加载精灵表
            sprite_sheet = Image.open(sprite_sheet_path).convert("RGBA")
            frame_w = sprite_metadata.get("frame_width", 128)
            frame_h = sprite_metadata.get("frame_height", 128)
            actions = sprite_metadata.get("actions", [])

            stickers = []

            for row_idx, action in enumerate(actions):
                action_name = action.get("name", f"sticker_{row_idx}")
                frame_count = action.get("frame_count", 4)
                fps = action.get("fps", 8)

                # 从精灵表提取该动作的帧
                frames = []
                for col_idx in range(frame_count):
                    x = col_idx * frame_w
                    y = row_idx * frame_h

                    # 裁剪帧
                    frame = sprite_sheet.crop((x, y, x + frame_w, y + frame_h))

                    # 检查帧是否为空（全透明）
                    if self._is_frame_empty(frame):
                        continue

                    frames.append(frame)

                if not frames:
                    continue

                # 生成单个 GIF 贴纸
                gif_path = os.path.join(sticker_dir, f"{action_name}.gif")
                self._save_gif(frames, gif_path, fps)

                # 同时生成静态 PNG 版本（首帧）
                png_path = os.path.join(sticker_dir, f"{action_name}.png")
                frames[0].save(png_path, "PNG")

                stickers.append({
                    "name": action_name,
                    "gif_path": gif_path,
                    "png_path": png_path,
                    "frame_count": len(frames),
                    "fps": fps,
                    "width": frame_w,
                    "height": frame_h
                })

            # 打包为 ZIP
            sticker_pack_zip = os.path.join(output_dir, "sticker_pack.zip")
            self._create_sticker_zip(sticker_dir, sticker_pack_zip, stickers)

            return {
                "sticker_dir": sticker_dir,
                "sticker_pack_zip": sticker_pack_zip,
                "sticker_count": len(stickers),
                "stickers": stickers
            }

        except Exception as e:
            raise RuntimeError(f"贴纸包生成失败: {str(e)}")

    def _is_frame_empty(self, frame: Image.Image) -> bool:
        """
        检查帧是否为空（全透明或全白）。

        Args:
            frame: RGBA 帧图片

        Returns:
            bool: True 表示空帧
        """
        if frame.mode != "RGBA":
            frame = frame.convert("RGBA")

        # 检查 alpha 通道
        alpha = frame.split()[3]
        extrema = alpha.getextrema()
        if extrema == (0, 0):
            return True  # 全透明

        return False

    def _save_gif(self, frames: List[Image.Image], output_path: str, fps: int = 8):
        """
        将帧列表保存为 GIF 动画。

        Args:
            frames: RGBA 帧列表
            output_path: 输出 GIF 路径
            fps: 帧率
        """
        if not frames:
            return

        # 转为 RGB（GIF 不支持 RGBA，用白色背景替代）
        gif_frames = []
        for frame in frames:
            bg = Image.new("RGBA", frame.size, (255, 255, 255, 255))
            bg.paste(frame, mask=frame.split()[3])
            gif_frames.append(bg.convert("RGB").quantize(colors=128))

        duration = int(1000 / fps)  # 毫秒

        gif_frames[0].save(
            output_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=duration,
            loop=0,
            disposal=2,  # 每帧清除
            transparency=0
        )

    def _create_sticker_zip(
        self, sticker_dir: str, zip_path: str, stickers: List[Dict]
    ):
        """
        将贴纸文件打包为 ZIP。

        Args:
            sticker_dir: 贴纸目录
            zip_path: 输出 ZIP 路径
            stickers: 贴纸信息列表
        """
        import zipfile

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for sticker in stickers:
                # 添加 GIF
                if os.path.exists(sticker["gif_path"]):
                    zf.write(
                        sticker["gif_path"],
                        os.path.basename(sticker["gif_path"])
                    )
                # 添加 PNG
                if os.path.exists(sticker["png_path"]):
                    zf.write(
                        sticker["png_path"],
                        os.path.basename(sticker["png_path"])
                    )

            # 添加贴纸说明文件
            sticker_info = {
                "count": len(stickers),
                "stickers": [
                    {
                        "name": s["name"],
                        "frames": s["frame_count"],
                        "size": f"{s['width']}x{s['height']}",
                    }
                    for s in stickers
                ]
            }
            zf.writestr(
                "sticker_info.json",
                json.dumps(sticker_info, indent=2, ensure_ascii=False)
            )


# 全局单例
sticker_generator = StickerGenerator()
