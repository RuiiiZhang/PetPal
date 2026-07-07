"""
PetPal AI管线 - 去背景脚本
使用rembg库去除图片背景，支持批量处理
如果rembg不可用，回退到简单的颜色阈值去白底
用法: python scripts/remove_background.py <input> [--output OUTPUT] [--batch]
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BG_REMOVAL_METHOD, BG_THRESHOLD_TOLERANCE


def remove_background_rembg(image_path: str, output_path: str) -> str:
    """
    使用rembg去除背景
    rembg基于U2-Net模型，效果最好但首次运行需要下载模型
    """
    try:
        from rembg import remove
        from PIL import Image
        import io

        print(f"  [去背景] 使用rembg处理: {Path(image_path).name}")
        inp = Image.open(image_path)

        # 确保是RGBA
        if inp.mode != "RGBA":
            inp = inp.convert("RGBA")

        # rembg处理
        out = remove(inp)

        # 保存
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        out.save(str(output), "PNG")
        print(f"  [去背景] ✅ 完成 (rembg): {output}")
        return str(output)

    except ImportError:
        raise RuntimeError("rembg 未安装，请运行: pip install rembg")


def remove_background_threshold(image_path: str, output_path: str,
                                tolerance: int = None) -> str:
    """
    简单阈值去白底方案（rembg不可用时的fallback）
    将接近白色的像素设为透明
    """
    from PIL import Image
    import numpy as np

    tolerance = tolerance or BG_THRESHOLD_TOLERANCE
    print(f"  [去背景] 使用阈值法处理: {Path(image_path).name} (容差:{tolerance})")

    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)

    # 检测白色/接近白色的像素
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

    # 白色阈值判断
    white_mask = (
        (r > 255 - tolerance) &
        (g > 255 - tolerance) &
        (b > 255 - tolerance)
    )

    # 将白色像素设为透明
    data[white_mask, 3] = 0

    # 边缘柔化（对白色区域边缘进行半透明处理）
    from PIL import ImageFilter
    alpha_channel = Image.fromarray(data[:, :, 3])
    alpha_blurred = alpha_channel.filter(ImageFilter.GaussianBlur(radius=1))
    data[:, :, 3] = np.array(alpha_blurred)

    # 保存
    result = Image.fromarray(data)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(str(output), "PNG")
    print(f"  [去背景] ✅ 完成 (阈值法): {output}")
    return str(output)


def remove_background(image_path: str, output_path: str,
                      method: str = None, **kwargs) -> str:
    """
    去背景统一入口
    Args:
        image_path: 输入图片路径
        output_path: 输出图片路径
        method: "rembg" | "threshold" | None(自动选择)
    Returns:
        输出图片路径
    """
    method = method or BG_REMOVAL_METHOD

    if method == "rembg":
        try:
            return remove_background_rembg(image_path, output_path)
        except (ImportError, RuntimeError) as e:
            print(f"  [去背景] rembg不可用 ({e})，回退到阈值法")
            return remove_background_threshold(image_path, output_path, **kwargs)
    else:
        return remove_background_threshold(image_path, output_path, **kwargs)


def batch_remove_background(input_dir: str, output_dir: str,
                            method: str = None, **kwargs) -> list[str]:
    """
    批量去背景处理
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        method: 去背景方法
    Returns:
        输出文件路径列表
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 支持的图片格式
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    results = []

    image_files = sorted([
        f for f in input_path.iterdir()
        if f.suffix.lower() in extensions
    ])

    print(f"  [批量去背景] 找到 {len(image_files)} 张图片")

    for i, img_file in enumerate(image_files, 1):
        out_file = output_path / f"{img_file.stem}_nobg.png"
        print(f"  [{i}/{len(image_files)}] ", end="")
        try:
            result = remove_background(str(img_file), str(out_file), method, **kwargs)
            results.append(result)
        except Exception as e:
            print(f"  [批量去背景] ❌ 失败 {img_file.name}: {e}")

    print(f"  [批量去背景] ✅ 完成: {len(results)}/{len(image_files)} 张")
    return results


# ============================================================
# 命令行入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PetPal 去背景工具")
    parser.add_argument("input", help="输入图片路径或目录（--batch时为目录）")
    parser.add_argument("--output", "-o", help="输出路径")
    parser.add_argument("--method", choices=["rembg", "threshold"],
                       default=None, help="去背景方法")
    parser.add_argument("--batch", action="store_true", help="批量处理模式")
    parser.add_argument("--tolerance", type=int, default=30,
                       help="阈值法容差 (0-255)")
    args = parser.parse_args()

    if args.batch:
        if not args.output:
            args.output = str(Path(args.input) / ".." / "no_bg")
        batch_remove_background(args.input, args.output, args.method,
                               tolerance=args.tolerance)
    else:
        if not Path(args.input).exists():
            print(f"❌ 文件不存在: {args.input}")
            sys.exit(1)
        if not args.output:
            p = Path(args.input)
            args.output = str(p.parent / f"{p.stem}_nobg.png")
        remove_background(args.input, args.output, args.method,
                         tolerance=args.tolerance)
