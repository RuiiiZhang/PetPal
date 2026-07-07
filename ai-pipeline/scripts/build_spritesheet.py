"""
PetPal AI管线 - 精灵表构建脚本
从帧图排列成精灵表PNG，支持横向排列和网格排列
用法: python scripts/build_spritesheet.py <frames_dir> --action NAME [--output OUTPUT]
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont
from config import (
    FRAME_WIDTH, FRAME_HEIGHT, SPRITESHEET_FRAME_GAP,
    SPRITESHEET_PADDING, SPRITESHEET_LABEL_HEIGHT
)


def build_spritesheet(
    frame_paths: list[str],
    output_path: str,
    action_name: str = "",
    frame_width: int = None,
    frame_height: int = None,
    gap: int = None,
    padding: int = None,
    show_label: bool = True,
) -> str:
    """
    从帧图列表构建精灵表（横向排列）
    Args:
        frame_paths: 帧图路径列表（按顺序排列）
        output_path: 输出精灵表路径
        action_name: 动作名称（用于标注）
        frame_width: 帧宽度
        frame_height: 帧高度
        gap: 帧间隔
        padding: 内边距
        show_label: 是否显示底部标注
    Returns:
        精灵表路径
    """
    frame_w = frame_width or FRAME_WIDTH
    frame_h = frame_height or FRAME_HEIGHT
    gap = gap if gap is not None else SPRITESHEET_FRAME_GAP
    padding = padding if padding is not None else SPRITESHEET_PADDING
    label_h = SPRITESHEET_LABEL_HEIGHT if show_label else 0

    n = len(frame_paths)
    print(f"  [精灵表] 构建精灵表: {n} 帧, 帧尺寸 {frame_w}x{frame_h}")

    # 计算精灵表尺寸
    total_w = padding * 2 + n * frame_w + (n - 1) * gap
    total_h = padding * 2 + frame_h + label_h

    # 创建透明背景画布
    sheet = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # 绘制每帧
    for i, frame_path in enumerate(frame_paths):
        # 加载帧图
        frame = Image.open(frame_path).convert("RGBA")

        # 缩放到标准尺寸
        if frame.size != (frame_w, frame_h):
            frame = frame.resize((frame_w, frame_h), Image.LANCZOS)

        # 粘贴到精灵表
        x = padding + i * (frame_w + gap)
        y = padding
        sheet.paste(frame, (x, y), frame)

    # 绘制帧分隔指示线（浅色虚线效果）
    line_color = (200, 200, 200, 80)
    for i in range(1, n):
        x = padding + i * (frame_w + gap) - gap // 2
        draw.line([(x, padding), (x, padding + frame_h)],
                 fill=line_color, width=1)

    # 绘制底部标注
    if show_label and action_name:
        label_y = padding + frame_h + 5
        # 尝试加载字体
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except (IOError, OSError):
                font = ImageFont.load_default()

        # 标注文本
        text = f"{action_name} ({n} frames, {frame_w}x{frame_h})"
        # 文本居中
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (total_w - text_w) // 2
        draw.text((text_x, label_y), text, fill=(100, 100, 100, 200), font=font)

    # 保存
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(output), "PNG")

    print(f"  [精灵表] ✅ 精灵表已生成: {output} ({total_w}x{total_h})")
    return str(output)


def build_multi_action_spritesheet(
    action_frames: dict[str, list[str]],
    output_path: str,
    frame_width: int = None,
    frame_height: int = None,
) -> str:
    """
    构建包含多个动作的完整精灵表
    每个动作占据一行，左侧标注动作名
    Args:
        action_frames: {"action_name": ["frame1.png", "frame2.png", ...]}
        output_path: 输出路径
    Returns:
        精灵表路径
    """
    frame_w = frame_width or FRAME_WIDTH
    frame_h = frame_height or FRAME_HEIGHT
    gap = SPRITESHEET_FRAME_GAP
    padding = SPRITESHEET_PADDING
    label_w = 100  # 左侧标注区域宽度
    row_gap = 20   # 行间距离

    actions = list(action_frames.items())
    n_actions = len(actions)

    # 计算总尺寸
    max_frames = max(len(frames) for _, frames in actions)
    total_w = padding * 2 + label_w + max_frames * (frame_w + gap)
    total_h = padding * 2 + n_actions * (frame_h + row_gap)

    sheet = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # 加载字体
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except (IOError, OSError):
        font = ImageFont.load_default()

    for row_idx, (action_name, frame_paths) in enumerate(actions):
        y = padding + row_idx * (frame_h + row_gap)

        # 绘制动作名称
        draw.text(
            (padding, y + frame_h // 2 - 6),
            action_name,
            fill=(80, 80, 80, 255),
            font=font
        )

        # 绘制每帧
        for col_idx, frame_path in enumerate(frame_paths):
            frame = Image.open(frame_path).convert("RGBA")
            if frame.size != (frame_w, frame_h):
                frame = frame.resize((frame_w, frame_h), Image.LANCZOS)

            x = padding + label_w + col_idx * (frame_w + gap)
            sheet.paste(frame, (x, y), frame)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(str(output), "PNG")

    print(f"  [精灵表] ✅ 多动作精灵表: {output} ({total_w}x{total_h}, {n_actions}个动作)")
    return str(output)


# ============================================================
# 命令行入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PetPal 精灵表构建工具")
    parser.add_argument("input_dir", help="帧图目录")
    parser.add_argument("--action", "-a", default="action",
                       help="动作名称")
    parser.add_argument("--output", "-o", default=None,
                       help="输出路径")
    parser.add_argument("--width", type=int, default=None,
                       help="帧宽度")
    parser.add_argument("--height", type=int, default=None,
                       help="帧高度")
    parser.add_argument("--no-label", action="store_true",
                       help="不显示底部标注")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"❌ 目录不存在: {args.input_dir}")
        sys.exit(1)

    # 收集帧图
    extensions = {".png", ".jpg", ".jpeg", ".webp"}
    frame_files = sorted([
        f for f in input_dir.iterdir()
        if f.suffix.lower() in extensions
    ])

    if not frame_files:
        print(f"❌ 未找到图片文件: {args.input_dir}")
        sys.exit(1)

    frame_paths = [str(f) for f in frame_files]
    print(f"📦 找到 {len(frame_paths)} 帧图")

    output = args.output or str(input_dir.parent / "spritesheet.png")
    result = build_spritesheet(
        frame_paths, output, args.action,
        frame_width=args.width, frame_height=args.height,
        show_label=not args.no_label
    )
    print(f"\n✅ 精灵表已生成: {result}")
