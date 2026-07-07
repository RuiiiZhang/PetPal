"""
PetPal AI管线 - GIF合成脚本
从帧图合成GIF动画，支持循环播放和帧率控制
用法: python scripts/generate_gif.py <frames_dir> --fps 3 --output output.gif
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
from config import GIF_LOOP, GIF_OPTIMIZE, FRAME_WIDTH, FRAME_HEIGHT


def generate_gif(
    frame_paths: list[str],
    output_path: str,
    fps: int = 3,
    loop: int = None,
    optimize: bool = None,
    frame_width: int = None,
    frame_height: int = None,
) -> str:
    """
    从帧图列表合成GIF动画
    Args:
        frame_paths: 帧图路径列表（按播放顺序）
        output_path: 输出GIF路径
        fps: 帧率（每秒帧数）
        loop: 循环次数（0=无限循环）
        optimize: 是否优化GIF大小
        frame_width: 输出帧宽度（None保持原尺寸）
        frame_height: 输出帧高度
    Returns:
        GIF文件路径
    """
    loop = loop if loop is not None else GIF_LOOP
    optimize = optimize if optimize is not None else GIF_OPTIMIZE

    if not frame_paths:
        raise ValueError("帧图列表为空")

    n = len(frame_paths)
    duration = int(1000 / fps)  # 毫秒

    print(f"  [GIF合成] 帧数:{n} FPS:{fps} 间隔:{duration}ms 循环:{'∞' if loop == 0 else loop}")

    # 加载并处理所有帧
    frames = []
    for i, path in enumerate(frame_paths):
        img = Image.open(path)

        # 转换为RGBA
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # 调整尺寸
        if frame_width and frame_height:
            if img.size != (frame_width, frame_height):
                img = img.resize((frame_width, frame_height), Image.LANCZOS)

        # 转换为P模式（带透明度处理）用于GIF
        # 创建白色背景合成
        background = Image.new("RGBA", img.size, (255, 255, 255, 0))
        composite = Image.alpha_composite(background, img)

        # 量化颜色以减少GIF大小
        if optimize:
            # 使用自适应调色板
            p_img = composite.convert("RGB").quantize(
                colors=128,
                method=Image.Quantize.MEDIANCUT,
            )
        else:
            p_img = composite.convert("RGB").convert("P", palette=Image.ADAPTIVE)

        # 处理透明度：找到最接近透明的颜色并设为mask
        if composite.mode == "RGBA":
            alpha = composite.split()[3]
            # 将半透明区域转为完全透明或不透明
            threshold = 128
            mask = alpha.point(lambda p: 255 if p > threshold else 0)
            p_img.info["transparency"] = 0  # 使用调色板中的第0个颜色
        else:
            mask = None

        frames.append(p_img)

    if not frames:
        raise ValueError("没有有效的帧")

    # 保存GIF
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # 第一帧保存，其余帧append
    frames[0].save(
        str(output),
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        optimize=optimize,
        disposal=2,  # 每帧清除前一帧区域
    )

    file_size = output.stat().st_size / 1024
    print(f"  [GIF合成] ✅ GIF已生成: {output} ({file_size:.1f}KB, {n}帧)")
    return str(output)


def generate_gif_from_spritesheet(
    spritesheet_path: str,
    output_path: str,
    action_name: str,
    frame_count: int,
    fps: int = 3,
    frame_width: int = None,
    frame_height: int = None,
) -> str:
    """
    从精灵表中切割指定动作的帧并合成GIF
    Args:
        spritesheet_path: 精灵表路径
        output_path: 输出GIF路径
        action_name: 动作名称
        frame_count: 帧数
        fps: 帧率
    Returns:
        GIF路径
    """
    sheet = Image.open(spritesheet_path)
    sheet_w, sheet_h = sheet.size

    # 自动检测帧尺寸
    from config import SPRITESHEET_PADDING, SPRITESHEET_FRAME_GAP, SPRITESHEET_LABEL_HEIGHT
    padding = SPRITESHEET_PADDING
    gap = SPRITESHEET_FRAME_GAP
    label_h = SPRITESHEET_LABEL_HEIGHT

    # 计算每帧宽度
    available_w = sheet_w - 2 * padding - (frame_count - 1) * gap
    fw = frame_width or (available_w // frame_count)
    fh = frame_height or (sheet_h - 2 * padding - label_h)

    print(f"  [GIF合成] 从精灵表切割: {action_name} ({frame_count}帧, {fw}x{fh})")

    frame_paths = []
    temp_dir = Path(output_path).parent / "_temp_frames"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for i in range(frame_count):
        x = padding + i * (fw + gap)
        y = padding
        frame = sheet.crop((x, y, x + fw, y + fh))
        frame_path = temp_dir / f"{action_name}_frame_{i:03d}.png"
        frame.save(str(frame_path), "PNG")
        frame_paths.append(str(frame_path))

    return generate_gif(frame_paths, output_path, fps=fps,
                       frame_width=fw, frame_height=fh)


def batch_generate_gifs(
    frames_dir: str,
    output_dir: str,
    actions: list[dict],
) -> list[str]:
    """
    批量生成GIF
    Args:
        frames_dir: 帧图根目录（包含各动作子目录）
        output_dir: GIF输出目录
        actions: 动作列表 [{"name": "sit", "fps": 3}, ...]
    Returns:
        GIF路径列表
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    for action in actions:
        name = action["name"]
        fps = action.get("fps", 3)

        action_dir = Path(frames_dir) / name
        if not action_dir.exists():
            print(f"  ⚠️ 动作目录不存在: {action_dir}")
            continue

        # 收集帧
        extensions = {".png", ".jpg", ".jpeg"}
        frame_files = sorted([
            f for f in action_dir.iterdir()
            if f.suffix.lower() in extensions
        ])

        if not frame_files:
            print(f"  ⚠️ 无帧图: {action_dir}")
            continue

        gif_path = output_path / f"{name}.gif"
        try:
            result = generate_gif(
                [str(f) for f in frame_files],
                str(gif_path),
                fps=fps,
            )
            results.append(result)
        except Exception as e:
            print(f"  ❌ GIF生成失败 ({name}): {e}")

    print(f"  [批量GIF] ✅ 完成: {len(results)}/{len(actions)} 个GIF")
    return results


# ============================================================
# 命令行入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PetPal GIF合成工具")
    parser.add_argument("input", help="帧图目录或精灵表路径")
    parser.add_argument("--output", "-o", default=None, help="输出路径")
    parser.add_argument("--fps", type=int, default=3, help="帧率")
    parser.add_argument("--loop", type=int, default=0, help="循环次数(0=无限)")
    parser.add_argument("--width", type=int, default=None, help="帧宽度")
    parser.add_argument("--height", type=int, default=None, help="帧高度")
    parser.add_argument("--action", default=None, help="动作名(从精灵表切割时用)")
    parser.add_argument("--frames", type=int, default=None, help="帧数(从精灵表切割时用)")
    args = parser.parse_args()

    input_path = Path(args.input)

    if input_path.is_dir():
        # 从帧图目录生成
        extensions = {".png", ".jpg", ".jpeg"}
        frame_files = sorted([
            f for f in input_path.iterdir()
            if f.suffix.lower() in extensions
        ])
        frame_paths = [str(f) for f in frame_files]
        output = args.output or str(input_path.parent / f"{input_path.name}.gif")
    elif args.action and args.frames:
        # 从精灵表切割
        output = args.output or str(input_path.parent / f"{args.action}.gif")
        result = generate_gif_from_spritesheet(
            str(input_path), output, args.action, args.frames,
            fps=args.fps, frame_width=args.width, frame_height=args.height
        )
        print(f"\n✅ GIF已生成: {result}")
        sys.exit(0)
    else:
        print("❌ 请指定帧图目录或使用 --action 和 --frames 从精灵表生成")
        sys.exit(1)

    result = generate_gif(frame_paths, output, fps=args.fps, loop=args.loop,
                         frame_width=args.width, frame_height=args.height)
    print(f"\n✅ GIF已生成: {result}")
