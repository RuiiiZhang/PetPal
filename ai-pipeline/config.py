"""
PetPal AI管线 - 配置文件
所有API密钥、模型参数、输出路径等配置集中管理
"""

import os
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
# 项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()

# 输出基础目录
OUTPUT_BASE_DIR = PROJECT_ROOT / "output"

# 静态资源目录
ASSETS_DIR = PROJECT_ROOT / "assets"
MOCK_IMAGES_DIR = ASSETS_DIR / "mock_images"

# ============================================================
# AI提供商配置
# ============================================================
# 默认使用的提供商: "flux" | "midjourney" | "coze" | "mock"
DEFAULT_PROVIDER = os.getenv("PETPAL_PROVIDER", "mock")

# Flux API 配置
FLUX_API_KEY = os.getenv("FLUX_API_KEY", "")
FLUX_API_BASE = os.getenv("FLUX_API_BASE", "https://api.bfl.ml/v1")
FLUX_MODEL_CHARACTER = "flux-pro-1.1"       # 角色生成模型
FLUX_MODEL_ANIMATION = "flux-pro-1.1"      # 动画帧生成模型
FLUX_TIMEOUT = 120                          # 超时秒数

# Midjourney API 配置 (通过第三方代理)
MIDJOURNEY_API_KEY = os.getenv("MIDJOURNEY_API_KEY", "")
MIDJOURNEY_API_BASE = os.getenv("MIDJOURNEY_API_BASE", "https://api.midjourneyapi.xyz/v2")
MIDJOURNEY_MODEL = "midjourney"
MIDJOURNEY_TIMEOUT = 300

# Coze 内置生图配置
COZE_API_KEY = os.getenv("COZE_API_KEY", "")
COZE_API_BASE = os.getenv("COZE_API_BASE", "https://api.coze.cn/v1")
COZE_BOT_ID = os.getenv("COZE_BOT_ID", "")
COZE_TIMEOUT = 120

# ============================================================
# 百度AI API 配置 (品种检测)
# ============================================================
BAIDU_API_KEY = os.getenv("BAIDU_API_KEY", "")
BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY", "")
BAIDU_DETECT_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v2/animal_detect"

# ============================================================
# 图像生成参数
# ============================================================
# 角色图尺寸
CHARACTER_WIDTH = 512
CHARACTER_HEIGHT = 512

# 动画帧尺寸
FRAME_WIDTH = 128
FRAME_HEIGHT = 128

# 精灵表配置
SPRITESHEET_FRAME_GAP = 10       # 帧间隔像素
SPRITESHEET_PADDING = 20         # 精灵表内边距
SPRITESHEET_LABEL_HEIGHT = 30    # 底部标签高度

# GIF 配置
GIF_LOOP = 0                     # 0=无限循环
GIF_OPTIMIZE = True

# ============================================================
# 去背景配置
# ============================================================
# 去背景方法: "rembg" | "threshold"
BG_REMOVAL_METHOD = os.getenv("BG_REMOVAL_METHOD", "rembg")
# 阈值去白底的容差 (0-255)
BG_THRESHOLD_TOLERANCE = 30

# ============================================================
# 风格预设
# ============================================================
STYLE_PRESETS = {
    "chibi": {
        "display_name": "Q版卡通",
        "body_ratio": "2-3头身",
        "eye_style": "大而圆的眼睛，高光点明显",
        "line_style": "柔和的轮廓线",
        "color_palette": "明亮、饱和度适中",
        "detail_level": "中等细节，简洁可爱",
    },
    "hand_drawn": {
        "display_name": "手绘风",
        "body_ratio": "3-4头身",
        "eye_style": "自然比例的眼睛，温和表情",
        "line_style": "铅笔/水彩质感线条",
        "color_palette": "温暖柔和的水彩色调",
        "detail_level": "手绘纹理，有纸张质感",
    },
    "realistic": {
        "display_name": "写实风",
        "body_ratio": "真实比例",
        "eye_style": "真实眼睛比例，光泽细腻",
        "line_style": "无明显线条，光影造型",
        "color_palette": "真实毛色，细腻渐变",
        "detail_level": "高精度细节，毛发纹理清晰",
    },
}

# ============================================================
# 输出子目录名称
# ============================================================
DIR_ORIGINAL = "original"
DIR_CHARACTER = "character"
DIR_CHARACTER_CONFIRMED = "character_confirmed"
DIR_ANIMATIONS = "animations"
DIR_GIFS = "gifs"

# 产物文件名
SPRITESHEET_FILENAME = "spritesheet.png"
DELIVERY_ZIP_FILENAME = "delivery.zip"
CONFIG_JSON_FILENAME = "config.json"
