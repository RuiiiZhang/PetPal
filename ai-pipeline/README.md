# PetPal AI 管线

> 自动宠物桌宠平台的AI图像生成管线，从宠物照片到完整的动画桌宠产物。

## 🏗️ 架构概览

```
用户上传照片 → 品种检测 → AI生成角色图 → 生成动画帧序列 → 去背景 → 切割帧 → 组装精灵表 → 合成GIF → 打包交付
```

## 📁 项目结构

```
ai-pipeline/
├── pipeline.py              # 主入口 - PetPipeline 类
├── config.py                # 配置（API密钥、模型参数、路径）
├── prompts.py               # AI生图Prompt模板库
├── action_library.py        # 动作库定义（猫8个/狗8个动作）
├── requirements.txt         # Python依赖
├── README.md                # 本文件
│
├── providers/               # AI提供商
│   ├── base.py              # 抽象基类
│   ├── flux_provider.py     # Flux Pro API
│   ├── midjourney_provider.py  # Midjourney API
│   ├── coze_provider.py     # Coze内置生图（fallback）
│   └── mock_provider.py     # Mock测试提供商
│
├── scripts/                 # 独立脚本
│   ├── detect_breed.py      # 品种检测（百度AI/Mock）
│   ├── remove_background.py # 去背景（rembg/阈值法）
│   ├── crop_frames.py       # 帧图切割
│   ├── build_spritesheet.py # 精灵表构建
│   ├── generate_gif.py      # GIF合成
│   └── package_output.py    # 产物打包
│
└── output/                  # 输出目录
    └── {order_id}/
        ├── original/        # 原图
        ├── character/       # 角色生成图
        ├── character_confirmed/  # 确认后的角色图
        ├── animations/      # 帧序列
        │   ├── sit/
        │   ├── walk/
        │   └── ...
        ├── spritesheet.png  # 精灵表
        ├── gifs/            # GIF动画
        ├── config.json      # 桌宠行为配置
        └── delivery.zip     # 交付包
```

## 🚀 快速开始

### 安装依赖

```bash
cd ai-pipeline
pip install -r requirements.txt
```

### 运行完整管线

```bash
# Mock模式（无需API密钥，测试用）
python pipeline.py --order-id TEST001 --pet-name Mimi --species cat \
  --breed "British Shorthair" --features "蓝白,圆脸,大眼睛" --style chibi \
  --provider mock

# Flux模式
export FLUX_API_KEY=your_key
python pipeline.py --order-id ORD001 --pet-name Buddy --species dog \
  --breed "Golden Retriever" --features "金色,大耳朵" --style chibi \
  --provider flux
```

### Python代码调用

```python
from pipeline import PetPipeline, run_pipeline

# 方式1：一键运行
result = run_pipeline(
    order_id="ORD001",
    pet_name="Mimi",
    species="cat",
    breed="British Shorthair",
    features="蓝白, 圆脸",
    style="chibi",
    photo_paths=["/path/to/photo.jpg"],
)

# 方式2：分步执行
pipeline = PetPipeline(
    order_id="ORD001", pet_name="Mimi",
    species="cat", breed="British Shorthair",
    features="蓝白", style="chibi",
    photo_paths=["photo.jpg"],
)
char_path = pipeline.generate_character()       # 生成角色
frames = pipeline.generate_animation("sit")     # 生成动作帧
sprite = pipeline.build_sprite_sheet()          # 构建精灵表
gifs = pipeline.generate_gifs()                 # 合成GIF
```

## 🔧 独立脚本使用

```bash
# 品种检测
python scripts/detect_breed.py photo.jpg --mock

# 去背景
python scripts/remove_background.py photo.jpg -o photo_nobg.png
python scripts/remove_background.py photos_dir/ --batch -o output_dir/

# 帧切割
python scripts/crop_frames.py strip.png --frames 5 -o frames_dir/

# 精灵表构建
python scripts/build_spritesheet.py frames_dir/ --action sit -o sprite.png

# GIF合成
python scripts/generate_gif.py frames_dir/ --fps 3 -o sit.gif

# 产物打包
python scripts/package_output.py output/ORD001/
```

## 🎨 AI提供商

| 提供商 | 模型 | 特点 | 配置 |
|--------|------|------|------|
| **Flux** | Flux Pro 1.1 | 高质量、快速 | `FLUX_API_KEY` |
| **Midjourney** | Midjourney v6 | 艺术感强 | `MIDJOURNEY_API_KEY` |
| **Coze** | 内置生图 | 便捷fallback | `COZE_API_KEY`, `COZE_BOT_ID` |
| **Mock** | PIL绘制 | 测试用，无需API | 无 |

通过环境变量切换：`export PETPAL_PROVIDER=mock`

## 🐾 动作库

### 猫咪动作 (8个)
| 动作 | 显示名 | 帧数 | FPS | 描述 |
|------|--------|------|-----|------|
| sit | 端坐摇尾巴 | 5 | 3 | 端坐，尾巴缓慢摇摆 |
| walk | 慢走散步 | 6 | 4 | 优雅行走 |
| stretch | 伸懒腰 | 4 | 3 | 前爪伸展 |
| sleep | 趴下打瞌睡 | 4 | 2 | 闭眼呼吸 |
| belly | 翻肚皮 | 5 | 3 | 翻身露肚皮 |
| head_tilt | 歪头好奇 | 3 | 2 | 歪头观察 |
| groom | 舔爪子洗脸 | 5 | 3 | 舔爪擦脸 |
| yawn | 打哈欠 | 4 | 2 | 张嘴打哈欠 |

### 狗狗动作 (8个)
| 动作 | 显示名 | 帧数 | FPS | 描述 |
|------|--------|------|-----|------|
| sit | 端坐摇尾巴 | 5 | 3 | 快速摇尾 |
| walk | 欢快散步 | 6 | 4 | 轻快行走 |
| shake | 握手 | 4 | 3 | 抬爪握手 |
| sleep | 趴下睡觉 | 4 | 2 | 趴地安睡 |
| fetch | 接飞盘 | 5 | 4 | 跳跃接盘 |
| head_tilt | 歪头卖萌 | 3 | 2 | 呆萌歪头 |
| spin | 转圈圈 | 6 | 5 | 原地旋转 |
| beg | 作揖讨食 | 4 | 3 | 后腿站立作揖 |

## 📝 Prompt模板

prompt模板按物种×风格组织，支持三种画风：
- **chibi** (Q版卡通): 2-3头身，大眼睛，可爱风
- **hand_drawn** (手绘风): 水彩质感，温暖柔和
- **realistic** (写实风): 照片级真实感

详见 `prompts.py`，包含角色生成和动画帧序列的完整模板。

## ⚙️ 配置

所有配置集中在 `config.py`，支持环境变量覆盖：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `PETPAL_PROVIDER` | AI提供商 | `mock` |
| `FLUX_API_KEY` | Flux API密钥 | - |
| `MIDJOURNEY_API_KEY` | Midjourney API密钥 | - |
| `COZE_API_KEY` | Coze API密钥 | - |
| `COZE_BOT_ID` | Coze Bot ID | - |
| `BG_REMOVAL_METHOD` | 去背景方法 | `rembg` |
| `BAIDU_API_KEY` | 百度AI密钥（品种检测） | - |
