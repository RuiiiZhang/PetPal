"""
PetPal AI管线 - 产物打包脚本
将所有产物打包成ZIP文件，用于交付
用法: python scripts/package_output.py <output_dir> [--output ZIP_PATH]
"""

import os
import sys
import json
import zipfile
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    SPRITESHEET_FILENAME, DELIVERY_ZIP_FILENAME,
    CONFIG_JSON_FILENAME, DIR_GIFS, DIR_ANIMATIONS,
    DIR_CHARACTER, DIR_CHARACTER_CONFIRMED
)


def generate_delivery_config(
    order_id: str,
    pet_name: str,
    species: str,
    breed: str,
    style: str,
    actions: list[dict],
    output_dir: str,
) -> str:
    """
    生成桌宠行为配置JSON
    这是客户端加载桌宠时需要的配置文件
    """
    config = {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "pet": {
            "order_id": order_id,
            "name": pet_name,
            "species": species,
            "breed": breed,
            "style": style,
        },
        "spritesheet": {
            "file": SPRITESHEET_FILENAME,
            "frame_width": 128,
            "frame_height": 128,
        },
        "animations": [],
        "behavior": {
            "default_action": actions[0]["name"] if actions else "sit",
            "idle_timeout": 30,       # 秒，无操作后进入待机动作
            "random_play": True,       # 是否随机播放动作
            "action_weights": {        # 动作播放权重
                a["name"]: 1.0 for a in actions
            },
        },
        "gifs": {},
    }

    # 填充动画配置
    for action in actions:
        config["animations"].append({
            "name": action["name"],
            "display": action["display"],
            "frames": action["frames"],
            "fps": action["fps"],
            "duration_ms": int(1000 / action["fps"]) * action["frames"],
            "loop": True,
        })

    # 填充GIF配置
    gifs_dir = Path(output_dir) / DIR_GIFS
    if gifs_dir.exists():
        for gif_file in sorted(gifs_dir.glob("*.gif")):
            action_name = gif_file.stem
            config["gifs"][action_name] = {
                "file": f"{DIR_GIFS}/{gif_file.name}",
                "fps": next(
                    (a["fps"] for a in actions if a["name"] == action_name),
                    3
                ),
            }

    # 保存配置
    config_path = Path(output_dir) / CONFIG_JSON_FILENAME
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))
    print(f"  [打包] 配置已生成: {config_path}")
    return str(config_path)


def package_delivery(
    output_dir: str,
    zip_path: str = None,
    include_frames: bool = False,
) -> str:
    """
    将输出目录打包为ZIP交付包
    Args:
        output_dir: 输出目录路径
        zip_path: ZIP输出路径（None则使用默认名称）
        include_frames: 是否包含原始帧图（默认不包含以减小体积）
    Returns:
        ZIP文件路径
    """
    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"输出目录不存在: {output_dir}")

    # 默认ZIP路径
    if zip_path is None:
        zip_path = str(output_path / DELIVERY_ZIP_FILENAME)

    print(f"  [打包] 开始打包: {output_dir}")

    # 收集需要打包的文件
    files_to_include = []

    # 1. 精灵表
    spritesheet = output_path / SPRITESHEET_FILENAME
    if spritesheet.exists():
        files_to_include.append((spritesheet, SPRITESHEET_FILENAME))

    # 2. 配置文件
    config_json = output_path / CONFIG_JSON_FILENAME
    if config_json.exists():
        files_to_include.append((config_json, CONFIG_JSON_FILENAME))

    # 3. GIF文件
    gifs_dir = output_path / DIR_GIFS
    if gifs_dir.exists():
        for gif_file in sorted(gifs_dir.glob("*.gif")):
            files_to_include.append((gif_file, f"{DIR_GIFS}/{gif_file.name}"))

    # 4. 角色确认图
    char_confirmed = output_path / DIR_CHARACTER_CONFIRMED
    if char_confirmed.exists():
        for img_file in sorted(char_confirmed.glob("*")):
            if img_file.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
                files_to_include.append(
                    (img_file, f"{DIR_CHARACTER_CONFIRMED}/{img_file.name}")
                )

    # 5. 可选：帧图
    if include_frames:
        anim_dir = output_path / DIR_ANIMATIONS
        if anim_dir.exists():
            for action_dir in sorted(anim_dir.iterdir()):
                if action_dir.is_dir():
                    for frame_file in sorted(action_dir.glob("*")):
                        if frame_file.suffix.lower() in {".png", ".jpg"}:
                            files_to_include.append(
                                (frame_file,
                                 f"{DIR_ANIMATIONS}/{action_dir.name}/{frame_file.name}")
                            )

    # 生成ZIP
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, arc_name in files_to_include:
            zf.write(str(file_path), arc_name)

    zip_size = Path(zip_path).stat().st_size / 1024
    print(f"  [打包] ✅ 交付包已生成: {zip_path}")
    print(f"  [打包]    包含 {len(files_to_include)} 个文件, 大小 {zip_size:.1f}KB")
    return zip_path


def validate_output(output_dir: str) -> dict:
    """
    验证输出目录的完整性
    Returns:
        {"valid": bool, "missing": [...], "warnings": [...]}
    """
    output_path = Path(output_dir)
    missing = []
    warnings = []

    # 检查必需文件
    required = [
        SPRITESHEET_FILENAME,
        CONFIG_JSON_FILENAME,
    ]
    for f in required:
        if not (output_path / f).exists():
            missing.append(f)

    # 检查GIF目录
    gifs_dir = output_path / DIR_GIFS
    if gifs_dir.exists():
        gif_count = len(list(gifs_dir.glob("*.gif")))
        if gif_count == 0:
            warnings.append("gifs/目录为空")
    else:
        missing.append(DIR_GIFS)

    # 检查角色图
    char_dir = output_path / DIR_CHARACTER_CONFIRMED
    if char_dir.exists():
        char_files = [f for f in char_dir.iterdir()
                     if f.suffix.lower() in {".png", ".jpg"}]
        if not char_files:
            warnings.append("character_confirmed/目录为空")
    else:
        warnings.append("character_confirmed/目录不存在")

    valid = len(missing) == 0
    return {
        "valid": valid,
        "missing": missing,
        "warnings": warnings,
        "gif_count": len(list(gifs_dir.glob("*.gif"))) if gifs_dir.exists() else 0,
    }


# ============================================================
# 命令行入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PetPal 产物打包工具")
    parser.add_argument("output_dir", help="输出目录路径")
    parser.add_argument("--output", "-o", default=None,
                       help="ZIP输出路径")
    parser.add_argument("--include-frames", action="store_true",
                       help="包含原始帧图")
    parser.add_argument("--validate-only", action="store_true",
                       help="仅验证完整性")
    parser.add_argument("--gen-config", action="store_true",
                       help="生成配置文件")
    parser.add_argument("--pet-name", default="Pet")
    parser.add_argument("--species", default="cat")
    parser.add_argument("--breed", default="Unknown")
    parser.add_argument("--style", default="chibi")
    parser.add_argument("--order-id", default="test")
    args = parser.parse_args()

    if not Path(args.output_dir).exists():
        print(f"❌ 目录不存在: {args.output_dir}")
        sys.exit(1)

    # 验证
    validation = validate_output(args.output_dir)
    print(f"\n📋 完整性检查: {'✅ 通过' if validation['valid'] else '❌ 不通过'}")
    if validation["missing"]:
        for m in validation["missing"]:
            print(f"  ❌ 缺失: {m}")
    if validation["warnings"]:
        for w in validation["warnings"]:
            print(f"  ⚠️ 警告: {w}")

    if args.validate_only:
        sys.exit(0 if validation["valid"] else 1)

    # 打包
    zip_path = package_delivery(
        args.output_dir,
        args.output,
        include_frames=args.include_frames
    )
    print(f"\n📦 交付包: {zip_path}")
