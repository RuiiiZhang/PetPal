"""
PetPal AI管线 - 帧图切割脚本
从AI生成的帧序列行图中切割出单帧图片
用法: python scripts/crop_frames.py <frame_strip_path> --frames N [--output-dir DIR]
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
from config import FRAME_WIDTH, FRAME_HEIGHT


def crop_frames_from_strip(
    strip_path: str,
    frame_count: int,
    output_dir: str,
    frame_width: int = None,
    frame_height: int = None,
    prefix: str = "frame",
) -> list[str]:
    """
    从横向帧序列图中均匀切割出单帧
    Args:
        strip_path: 帧序列图路径（横向排列）
        frame_count: 帧数量
        output_dir: 输出目录
        frame_width: 每帧宽度（None则自动计算）
        frame_height: 每帧高度（None则使用原图高度）
        prefix: 输出文件名前缀
    Returns:
        切割后的帧图路径列表
    """
    strip = Image.open(strip_path)
    strip_w, strip_h = strip.size

    # 确保RGBA
    if strip.mode != "RGBA":
        strip = strip.convert("RGBA")

    # 自动计算每帧尺寸
    if frame_width is None:
        frame_width = strip_w // frame_count
    if frame_height is None:
        frame_height = strip_h

    # 限制到标准帧尺寸
    target_w = frame_width or FRAME_WIDTH
    target_h = frame_height or FRAME_HEIGHT

    print(f"  [帧切割] 原图尺寸: {strip_w}x{strip_h}")
    print(f"  [帧切割] 帧数: {frame_count}, 每帧: {target_w}x{target_h}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    for i in range(frame_count):
        # 计算裁剪区域
        left = (strip_w // frame_count) * i
        upper = 0
        right = left + (strip_w // frame_count)
        lower = strip_h

        # 裁剪
        frame = strip.crop((left, upper, right, lower))

        # 缩放到标准尺寸
        if frame.size != (target_w, target_h):
            frame = frame.resize((target_w, target_h), Image.LANCZOS)

        # 保存
        frame_file = output_path / f"{prefix}_{i:03d}.png"
        frame.save(str(frame_file), "PNG")
        results.append(str(frame_file))

    print(f"  [帧切割] ✅ 切割完成: {len(results)} 帧 → {output_dir}")
    return results


def crop_frames_from_grid(
    sheet_path: str,
    cols: int,
    rows: int,
    output_dir: str,
    prefix: str = "frame",
) -> list[str]:
    """
    从网格排列的帧图中切割帧（多行动画）
    Args:
        sheet_path: 帧图路径
        cols: 列数
        rows: 行数
        output_dir: 输出目录
        prefix: 文件名前缀
    Returns:
        帧图路径列表
    """
    sheet = Image.open(sheet_path)
    if sheet.mode != "RGBA":
        sheet = sheet.convert("RGBA")

    sheet_w, sheet_h = sheet.size
    cell_w = sheet_w // cols
    cell_h = sheet_h // rows

    print(f"  [帧切割] 网格模式: {cols}列 x {rows}行, 单元格: {cell_w}x{cell_h}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    idx = 0
    for row in range(rows):
        for col in range(cols):
            left = col * cell_w
            upper = row * cell_h
            right = left + cell_w
            lower = upper + cell_h

            frame = sheet.crop((left, upper, right, lower))
            frame_file = output_path / f"{prefix}_{idx:03d}.png"
            frame.save(str(frame_file), "PNG")
            results.append(str(frame_file))
            idx += 1

    print(f"  [帧切割] ✅ 切割完成: {len(results)} 帧")
    return results


def auto_crop_frames(
    strip_path: str,
    frame_count: int,
    output_dir: str,
) -> list[str]:
    """
    智能切割：自动检测帧分隔线并切割
    通过分析像素列的透明度/颜色变化来定位帧边界
    """
    strip = Image.open(strip_path)
    if strip.mode != "RGBA":
        strip = strip.convert("RGBA")

    strip_w, strip_h = strip.size
    import numpy as np
    data = np.array(strip)

    # 寻找垂直分隔线（全透明或白色的列）
    separators = []
    for x in range(1, strip_w - 1):
        col = data[:, x, :]
        # 检查是否为透明列（alpha=0）
        transparent_ratio = (col[:, 3] == 0).sum() / strip_h
        # 检查是否为白色列
        white_ratio = ((col[:, 0] > 250) & (col[:, 1] > 250) & (col[:, 2] > 250)).sum() / strip_h

        if transparent_ratio > 0.8 or white_ratio > 0.9:
            separators.append(x)

    # 将连续的separator合并为边界
    boundaries = []
    if separators:
        current = separators[0]
        for s in separators[1:]:
            if s - current > 5:
                boundaries.append(current)
                current = s
            current = s
        boundaries.append(current)

    # 根据边界切割
    if len(boundaries) >= frame_count - 1:
        print(f"  [帧切割] 自动检测到 {len(boundaries)} 条分隔线")
        return _crop_by_boundaries(strip, boundaries, frame_count, output_dir)
    else:
        print(f"  [帧切割] 未检测到足够分隔线，使用均匀切割")
        return crop_frames_from_strip(strip_path, frame_count, output_dir)


def _crop_by_boundaries(
    strip: Image.Image,
    boundaries: list[int],
    frame_count: int,
    output_dir: str,
) -> list[str]:
    """根据检测到的边界切割帧"""
    strip_w, strip_h = strip.size
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 构建帧区域
    regions = []
    prev = 0
    for b in boundaries[:frame_count - 1]:
        regions.append((prev, b))
        prev = b + 1
    regions.append((prev, strip_w))

    # 只取前frame_count个区域
    regions = regions[:frame_count]

    results = []
    for i, (left, right) in enumerate(regions):
        frame = strip.crop((left, 0, right, strip_h))
        # 缩放到标准帧尺寸
        frame = frame.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
        frame_file = output_path / f"frame_{i:03d}.png"
        frame.save(str(frame_file), "PNG")
        results.append(str(frame_file))

    print(f"  [帧切割] ✅ 智能切割完成: {len(results)} 帧")
    return results


# ============================================================
# 命令行入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PetPal 帧图切割工具")
    parser.add_argument("input", help="帧序列图路径")
    parser.add_argument("--frames", "-n", type=int, required=True,
                       help="帧数量")
    parser.add_argument("--output-dir", "-o", default=None,
                       help="输出目录")
    parser.add_argument("--width", type=int, default=None,
                       help="每帧宽度")
    parser.add_argument("--height", type=int, default=None,
                       help="每帧高度")
    parser.add_argument("--auto", action="store_true",
                       help="自动检测分隔线")
    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)

    output_dir = args.output_dir or str(
        Path(args.input).parent / "frames"
    )

    if args.auto:
        frames = auto_crop_frames(args.input, args.frames, output_dir)
    else:
        frames = crop_frames_from_strip(
            args.input, args.frames, output_dir,
            frame_width=args.width, frame_height=args.height
        )

    print(f"\n📦 切割完成，共 {len(frames)} 帧:")
    for f in frames:
        print(f"  {f}")
