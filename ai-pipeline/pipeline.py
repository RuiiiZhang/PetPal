"""
PetPal AI管线 - 主入口
完整的宠物桌宠AI生成管线流程：
  接收照片 → 品种检测 → 生成Q版/写实角色图 → 生成动画帧序列 → 去背景 → 组装精灵表 → 合成GIF
"""

import os
import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Optional

# 添加项目根目录到path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    OUTPUT_BASE_DIR, DEFAULT_PROVIDER, CHARACTER_WIDTH, CHARACTER_HEIGHT,
    DIR_ORIGINAL, DIR_CHARACTER, DIR_CHARACTER_CONFIRMED, DIR_ANIMATIONS,
    DIR_GIFS, SPRITESHEET_FILENAME, DELIVERY_ZIP_FILENAME, CONFIG_JSON_FILENAME,
)
from action_library import get_actions, get_action, calculate_gif_duration
from prompts import build_character_prompt, build_animation_prompt

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("PetPipeline")


class PetPipeline:
    """
    宠物桌宠AI生成管线
    完整流程：照片输入 → 角色生成 → 动画帧 → 去背景 → 精灵表 → GIF
    """

    def __init__(
        self,
        order_id: str,
        pet_name: str,
        species: str,
        breed: str,
        features: str,
        style: str,
        photo_paths: list[str],
    ):
        """
        初始化管线
        Args:
            order_id: 订单ID
            pet_name: 宠物名字
            species: 物种 (cat/dog)
            breed: 品种
            features: 特征描述 (如 "橘色, 圆脸, 大眼睛")
            style: 画风 (chibi/hand_drawn/realistic)
            photo_paths: 用户提供的宠物照片路径列表
        """
        self.order_id = order_id
        self.pet_name = pet_name
        self.species = species.lower().strip()
        self.breed = breed
        self.features = features
        self.style = style.lower().strip()
        self.photo_paths = photo_paths

        # 输出目录
        self.output_dir = OUTPUT_BASE_DIR / order_id
        self._setup_directories()

        # AI提供商
        self.provider = self._init_provider()

        # 状态
        self.character_path: Optional[str] = None
        self.confirmed_character_path: Optional[str] = None
        self.spritesheet_path: Optional[str] = None
        self.gif_paths: list[str] = []

        logger.info(f"🐾 PetPipeline 初始化: order={order_id}, pet={pet_name}, "
                    f"species={species}, breed={breed}, style={style}")

    def _setup_directories(self):
        """创建输出目录结构"""
        dirs = [
            self.output_dir / DIR_ORIGINAL,
            self.output_dir / DIR_CHARACTER,
            self.output_dir / DIR_CHARACTER_CONFIRMED,
            self.output_dir / DIR_ANIMATIONS,
            self.output_dir / DIR_GIFS,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # 为每个动作创建子目录
        actions = get_actions(self.species)
        for action in actions:
            (self.output_dir / DIR_ANIMATIONS / action["name"]).mkdir(
                parents=True, exist_ok=True
            )

        # 复制原图到original目录
        for i, photo_path in enumerate(self.photo_paths):
            src = Path(photo_path)
            if src.exists():
                dst = self.output_dir / DIR_ORIGINAL / f"photo_{i:02d}{src.suffix}"
                shutil.copy2(str(src), str(dst))

    def _init_provider(self):
        """初始化AI提供商"""
        provider_name = DEFAULT_PROVIDER.lower()

        if provider_name == "flux":
            from providers.flux_provider import FluxProvider
            return FluxProvider()
        elif provider_name == "midjourney":
            from providers.midjourney_provider import MidjourneyProvider
            return MidjourneyProvider()
        elif provider_name == "coze":
            from providers.coze_provider import CozeProvider
            return CozeProvider()
        else:
            from providers.mock_provider import MockProvider
            return MockProvider()

    def _fallback_provider(self, error: Exception):
        """提供商降级"""
        logger.warning(f"⚠️ {self.provider.name} 失败 ({error})，降级到mock")
        from providers.mock_provider import MockProvider
        self.provider = MockProvider()
        return self.provider

    # ================================================================
    # 核心管线方法
    # ================================================================

    def run_full_pipeline(self) -> dict:
        """
        运行完整管线
        Returns:
            产物路径字典
        """
        logger.info("=" * 60)
        logger.info(f"🚀 开始完整管线: {self.pet_name} ({self.order_id})")
        logger.info("=" * 60)

        result = {
            "order_id": self.order_id,
            "pet_name": self.pet_name,
            "species": self.species,
            "breed": self.breed,
            "style": self.style,
            "output_dir": str(self.output_dir),
            "steps": {},
        }

        try:
            # Step 1: 生成角色图
            logger.info("\n📸 Step 1: 生成角色预览图")
            char_path = self.generate_character()
            result["steps"]["character"] = char_path
            self.character_path = char_path

            # Step 2: 确认角色（这里直接使用生成的，实际场景中会有用户确认环节）
            confirmed_path = self._confirm_character(char_path)
            self.confirmed_character_path = confirmed_path
            result["steps"]["character_confirmed"] = confirmed_path

            # Step 3: 生成所有动作的动画帧
            logger.info("\n🎬 Step 2: 生成动画帧序列")
            actions = get_actions(self.species)
            animation_paths = {}
            for action in actions:
                logger.info(f"  🎞️  动作: {action['display']} ({action['name']})")
                frames_path = self.generate_animation(action["name"])
                animation_paths[action["name"]] = frames_path
            result["steps"]["animations"] = animation_paths

            # Step 4: 构建精灵表
            logger.info("\n🗂️ Step 3: 构建精灵表")
            sprite_path = self.build_sprite_sheet()
            self.spritesheet_path = sprite_path
            result["steps"]["spritesheet"] = sprite_path

            # Step 5: 生成GIF
            logger.info("\n🎞️ Step 4: 合成GIF动画")
            gif_list = self.generate_gifs()
            self.gif_paths = gif_list
            result["steps"]["gifs"] = gif_list

            # Step 6: 生成配置文件
            logger.info("\n⚙️ Step 5: 生成配置文件")
            config_path = self._generate_config()
            result["steps"]["config"] = config_path

            # Step 7: 打包交付
            logger.info("\n📦 Step 6: 打包交付")
            from scripts.package_output import package_delivery
            zip_path = package_delivery(str(self.output_dir))
            result["steps"]["delivery_zip"] = zip_path
            result["delivery_zip"] = zip_path

            logger.info("\n" + "=" * 60)
            logger.info(f"✅ 管线完成! 产物目录: {self.output_dir}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"❌ 管线执行失败: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def generate_character(self) -> str:
        """
        生成角色预览图
        Returns:
            角色图路径
        """
        output_path = str(
            self.output_dir / DIR_CHARACTER / f"{self.pet_name}_character.png"
        )

        # 构建prompt
        prompt, negative_prompt = build_character_prompt(
            species=self.species,
            breed=self.breed,
            pet_name=self.pet_name,
            features=self.features,
            style=self.style,
        )

        logger.info(f"  使用提供商: {self.provider.name}")
        logger.info(f"  Prompt: {prompt[:100]}...")

        try:
            result = self.provider.generate_character(
                photo_path=self.photo_paths[0] if self.photo_paths else "",
                prompt=prompt,
                negative_prompt=negative_prompt,
                output_path=output_path,
                width=CHARACTER_WIDTH,
                height=CHARACTER_HEIGHT,
            )
        except Exception as e:
            logger.warning(f"  提供商失败，尝试降级...")
            self._fallback_provider(e)
            result = self.provider.generate_character(
                photo_path=self.photo_paths[0] if self.photo_paths else "",
                prompt=prompt,
                negative_prompt=negative_prompt,
                output_path=output_path,
                width=CHARACTER_WIDTH,
                height=CHARACTER_HEIGHT,
            )

        # 去背景处理
        self._remove_background(result)

        logger.info(f"  ✅ 角色图: {result}")
        return result

    def generate_animation(self, action_name: str) -> str:
        """
        生成指定动作的帧序列
        Args:
            action_name: 动作名称
        Returns:
            帧序列图路径
        """
        action = get_action(self.species, action_name)
        if not action:
            raise ValueError(f"未知动作: {action_name} (物种: {self.species})")

        output_path = str(
            self.output_dir / DIR_ANIMATIONS / action_name / "strip.png"
        )

        # 构建动画prompt
        prompt, negative_prompt = build_animation_prompt(
            species=self.species,
            breed=self.breed,
            features=self.features,
            style=self.style,
            action=action,
        )

        # 计算帧序列图尺寸
        frame_count = action["frames"]
        from config import FRAME_WIDTH, FRAME_HEIGHT
        strip_width = frame_count * FRAME_WIDTH * 2  # AI生成时放大
        strip_height = FRAME_HEIGHT * 2

        logger.info(f"  生成 {frame_count} 帧 ({action['display']})")

        try:
            result = self.provider.generate_animation_frames(
                prompt=prompt,
                negative_prompt=negative_prompt,
                output_path=output_path,
                frame_count=frame_count,
                width=strip_width,
                height=strip_height,
            )
        except Exception as e:
            logger.warning(f"  提供商失败，尝试降级...")
            self._fallback_provider(e)
            result = self.provider.generate_animation_frames(
                prompt=prompt,
                negative_prompt=negative_prompt,
                output_path=output_path,
                frame_count=frame_count,
                width=strip_width,
                height=strip_height,
            )

        # 切割帧
        self._crop_frames_to_individual(result, action_name, frame_count)

        logger.info(f"  ✅ 帧序列: {result}")
        return result

    def build_sprite_sheet(self) -> str:
        """
        构建完整精灵表（包含所有动作）
        Returns:
            精灵表路径
        """
        from scripts.build_spritesheet import build_multi_action_spritesheet

        actions = get_actions(self.species)
        action_frames = {}

        for action in actions:
            action_dir = self.output_dir / DIR_ANIMATIONS / action["name"]
            # 收集单帧文件
            frame_files = sorted([
                f for f in action_dir.glob("frame_*.png")
            ])
            if frame_files:
                action_frames[action["name"]] = [str(f) for f in frame_files]
            else:
                # 如果没有单帧，使用strip.png
                strip = action_dir / "strip.png"
                if strip.exists():
                    action_frames[action["name"]] = [str(strip)]

        output_path = str(self.output_dir / SPRITESHEET_FILENAME)
        result = build_multi_action_spritesheet(action_frames, output_path)

        logger.info(f"  ✅ 精灵表: {result}")
        return result

    def generate_gifs(self) -> list[str]:
        """
        为所有动作生成GIF
        Returns:
            GIF文件路径列表
        """
        from scripts.generate_gif import generate_gif

        actions = get_actions(self.species)
        gifs = []

        for action in actions:
            action_dir = self.output_dir / DIR_ANIMATIONS / action["name"]
            frame_files = sorted(action_dir.glob("frame_*.png"))

            if not frame_files:
                logger.warning(f"  ⚠️ {action['name']}: 无帧图，跳过")
                continue

            gif_path = self.output_dir / DIR_GIFS / f"{action['name']}.gif"
            fps = action["fps"]

            try:
                result = generate_gif(
                    [str(f) for f in frame_files],
                    str(gif_path),
                    fps=fps,
                )
                gifs.append(result)
                logger.info(f"  ✅ {action['display']}: {gif_path.name}")
            except Exception as e:
                logger.error(f"  ❌ {action['name']} GIF生成失败: {e}")

        logger.info(f"  ✅ 共生成 {len(gifs)} 个GIF")
        return gifs

    # ================================================================
    # 内部辅助方法
    # ================================================================

    def _confirm_character(self, character_path: str) -> str:
        """确认角色图（复制到confirmed目录）"""
        src = Path(character_path)
        dst = self.output_dir / DIR_CHARACTER_CONFIRMED / src.name
        shutil.copy2(str(src), str(dst))
        logger.info(f"  ✅ 角色已确认: {dst}")
        return str(dst)

    def _remove_background(self, image_path: str):
        """对生成的图片去背景"""
        from scripts.remove_background import remove_background
        try:
            img_path = Path(image_path)
            nobg_path = img_path.parent / f"{img_path.stem}_nobg.png"
            remove_background(image_path, str(nobg_path))
            # 用去背景图替换原图
            if nobg_path.exists():
                shutil.move(str(nobg_path), image_path)
        except Exception as e:
            logger.warning(f"  去背景失败 (非致命): {e}")

    def _crop_frames_to_individual(self, strip_path: str, action_name: str,
                                    frame_count: int):
        """将帧序列条切割为单帧文件"""
        from scripts.crop_frames import crop_frames_from_strip
        output_dir = str(self.output_dir / DIR_ANIMATIONS / action_name)
        try:
            crop_frames_from_strip(
                strip_path, frame_count, output_dir, prefix="frame"
            )
        except Exception as e:
            logger.warning(f"  帧切割失败: {e}")

    def _generate_config(self) -> str:
        """生成桌宠行为配置文件"""
        from scripts.package_output import generate_delivery_config
        actions = get_actions(self.species)
        return generate_delivery_config(
            order_id=self.order_id,
            pet_name=self.pet_name,
            species=self.species,
            breed=self.breed,
            style=self.style,
            actions=actions,
            output_dir=str(self.output_dir),
        )


# ================================================================
# 便捷函数
# ================================================================

def run_pipeline(
    order_id: str,
    pet_name: str,
    species: str,
    breed: str,
    features: str,
    style: str = "chibi",
    photo_paths: list[str] = None,
) -> dict:
    """
    一键运行管线
    """
    pipeline = PetPipeline(
        order_id=order_id,
        pet_name=pet_name,
        species=species,
        breed=breed,
        features=features,
        style=style,
        photo_paths=photo_paths or [],
    )
    return pipeline.run_full_pipeline()


# ================================================================
# 命令行入口
# ================================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PetPal AI管线 - 主入口")
    parser.add_argument("--order-id", required=True, help="订单ID")
    parser.add_argument("--pet-name", required=True, help="宠物名字")
    parser.add_argument("--species", default="cat", choices=["cat", "dog"],
                       help="物种")
    parser.add_argument("--breed", default="British Shorthair", help="品种")
    parser.add_argument("--features", default="", help="特征描述")
    parser.add_argument("--style", default="chibi",
                       choices=["chibi", "hand_drawn", "realistic"],
                       help="画风")
    parser.add_argument("--photos", nargs="*", default=[], help="宠物照片路径")
    parser.add_argument("--provider", default=None,
                       choices=["flux", "midjourney", "coze", "mock"],
                       help="AI提供商")
    args = parser.parse_args()

    # 覆盖provider配置
    if args.provider:
        os.environ["PETPAL_PROVIDER"] = args.provider

    # 运行管线
    result = run_pipeline(
        order_id=args.order_id,
        pet_name=args.pet_name,
        species=args.species,
        breed=args.breed,
        features=args.features,
        style=args.style,
        photo_paths=args.photos,
    )

    # 输出结果
    print("\n" + "=" * 60)
    print("📊 管线执行结果")
    print("=" * 60)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
