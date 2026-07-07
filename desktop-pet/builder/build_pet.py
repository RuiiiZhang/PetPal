#!/usr/bin/env python3
"""
PetPal 桌宠打包脚本
将模板项目 + 精灵表 + 配置打包为可编译的 Tauri 项目，并构建 exe
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="PetPal 桌宠打包工具")
    parser.add_argument("--order-id", required=True, help="订单ID")
    parser.add_argument("--sprite-sheet", required=True, help="精灵表图片路径")
    parser.add_argument("--config", required=True, help="配置JSON文件路径")
    parser.add_argument("--output-dir", default="output", help="输出目录")
    parser.add_argument("--skip-build", action="store_true", help="跳过tauri build，仅生成项目")
    return parser.parse_args()


TEMPLATE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_BASE = Path(__file__).resolve().parent.parent.parent / "output"


def prepare_project(order_id: str, sprite_sheet: str, config_json: str) -> Path:
    """准备可编译的Tauri项目"""

    output_dir = OUTPUT_BASE / order_id / "build"
    project_dir = output_dir / "desktop-pet"

    if project_dir.exists():
        shutil.rmtree(project_dir)

    # 复制模板项目（排除 builder 和 template 目录）
    shutil.copytree(
        TEMPLATE_DIR, project_dir,
        ignore=shutil.ignore_patterns("builder", "template", "node_modules", "target", "output")
    )

    # 读取用户配置
    with open(config_json, "r", encoding="utf-8") as f:
        user_config = json.load(f)

    # 处理配置模板变量替换（如果config.json中有{{}}占位符）
    config_path = project_dir / "template" / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # 替换模板变量
        for key, value in user_config.items():
            if isinstance(value, str):
                placeholder = "{{" + key.upper() + "}}"
                template_content = template_content.replace(placeholder, value)

        # 写入最终配置到项目根目录
        final_config = json.loads(template_content)
    else:
        final_config = user_config

    # 确保基本字段存在
    final_config.setdefault("pet_name", "小宠")
    final_config.setdefault("species", "cat")
    final_config.setdefault("size", 200)
    final_config.setdefault("sprite_sheet", "spritesheet.png")

    # 写入最终config.json到dist同级
    with open(project_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(final_config, f, ensure_ascii=False, indent=2)

    # 复制精灵表
    sprite_dest = project_dir / "spritesheet.png"
    shutil.copy2(sprite_sheet, sprite_dest)

    # 更新tauri.conf.json中的窗口大小
    tauri_conf_path = project_dir / "src-tauri" / "tauri.conf.json"
    with open(tauri_conf_path, "r", encoding="utf-8") as f:
        tauri_conf = json.load(f)

    size = final_config.get("size", 200)
    tauri_conf["tauri"]["windows"][0]["width"] = size
    tauri_conf["tauri"]["windows"][0]["height"] = size

    with open(tauri_conf_path, "w", encoding="utf-8") as f:
        json.dump(tauri_conf, f, ensure_ascii=False, indent=2)

    # 生成默认图标（如果没有）
    icons_dir = project_dir / "src-tauri" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    print(f"[PetPal Build] 项目准备完成: {project_dir}")
    return project_dir


def install_dependencies(project_dir: Path):
    """安装前端和Rust依赖"""
    print("[PetPal Build] 安装前端依赖...")
    subprocess.run(
        ["npm", "install"],
        cwd=project_dir,
        check=True,
        shell=(os.name == "nt")
    )

    print("[PetPal Build] 前端依赖安装完成")


def build_tauri(project_dir: Path, order_id: str) -> Path:
    """执行 Tauri 构建"""
    print("[PetPal Build] 开始构建 Tauri 应用...")

    subprocess.run(
        ["npm", "run", "tauri", "--", "build"],
        cwd=project_dir,
        check=True,
        shell=(os.name == "nt")
    )

    # 查找生成的exe
    exe_dir = project_dir / "src-tauri" / "target" / "release" / "bundle"
    if os.name == "nt":
        # Windows: 查找msi或exe
        for ext_dir in ["msi", "nsis"]:
            bundle_path = exe_dir / ext_dir
            if bundle_path.exists():
                for f in bundle_path.iterdir():
                    if f.suffix in (".exe", ".msi"):
                        return f

    # Linux/macOS fallback
    binary = project_dir / "src-tauri" / "target" / "release" / "petpal-desktop"
    if binary.exists():
        return binary

    raise FileNotFoundError("构建产物未找到")


def deliver(built_file: Path, order_id: str):
    """复制产物到交付目录"""
    delivery_dir = OUTPUT_BASE / order_id / "delivery"
    delivery_dir.mkdir(parents=True, exist_ok=True)

    dest = delivery_dir / f"PetPal-{order_id}{built_file.suffix}"
    shutil.copy2(built_file, dest)

    print(f"[PetPal Build] 交付产物: {dest}")
    return dest


def main():
    args = parse_args()
    order_id = args.order_id

    # 验证输入文件
    if not os.path.isfile(args.sprite_sheet):
        print(f"错误: 精灵表文件不存在: {args.sprite_sheet}")
        sys.exit(1)
    if not os.path.isfile(args.config):
        print(f"错误: 配置文件不存在: {args.config}")
        sys.exit(1)

    print(f"[PetPal Build] 订单: {order_id}")
    print(f"[PetPal Build] 精灵表: {args.sprite_sheet}")
    print(f"[PetPal Build] 配置: {args.config}")

    # Step 1: 准备项目
    project_dir = prepare_project(order_id, args.sprite_sheet, args.config)

    if args.skip_build:
        print(f"[PetPal Build] 跳过构建，项目目录: {project_dir}")
        return

    # Step 2: 安装依赖
    install_dependencies(project_dir)

    # Step 3: 构建
    built_file = build_tauri(project_dir, order_id)

    # Step 4: 交付
    deliver(built_file, order_id)

    print(f"[PetPal Build] ✅ 完成！订单 {order_id} 桌宠已生成。")


if __name__ == "__main__":
    main()
