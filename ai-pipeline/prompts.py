"""
PetPal AI管线 - Prompt模板库
所有AI生图的prompt模板，按物种和风格分类
prompt设计原则：详细、专业、包含画风/比例/颜色/构图约束
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import STYLE_PRESETS


# ============================================================
# 通用质量修饰词
# ============================================================
QUALITY_TAGS = (
    "masterpiece, best quality, high resolution, detailed, "
    "professional illustration, clean background, centered composition, "
    "full body visible, transparent background or white background"
)

NEGATIVE_PROMPT = (
    "low quality, blurry, deformed, ugly, bad anatomy, "
    "extra limbs, missing limbs, mutated, disfigured, "
    "watermark, text, signature, frame, border, "
    "human, person, people, multiple animals"
)

NEGATIVE_PROMPT_ANIMATION = (
    NEGATIVE_PROMPT + ", inconsistent style between frames, "
    "flickering, jittery, morphing body shape dramatically"
)


# ============================================================
# 角色生成 Prompt 模板
# ============================================================
# 参数：{pet_name}, {breed}, {features}, {style_specific}

CHARACTER_PROMPTS = {
    "cat": {
        "chibi": (
            "A cute chibi-style illustration of a {breed} cat named {pet_name}. "
            "Art style: Japanese kawaii chibi, 2-3 head-to-body ratio. "
            "Large expressive round eyes with prominent highlight dots, small triangular nose, "
            "tiny mouth with subtle smile. "
            "{features}. "
            "Soft rounded body proportions, short stubby limbs, oversized head. "
            "Smooth clean outlines with slight cel-shading. "
            "Bright and cheerful color palette with saturated but not overwhelming tones. "
            "The cat is sitting in a relaxed pose, facing slightly to the right (3/4 view). "
            "Clean white background, character centered in frame. "
            "Style reference: Neko Atsume, Pusheen aesthetic. "
            "{quality_tags}"
        ),
        "hand_drawn": (
            "A warm hand-drawn watercolor illustration of a {breed} cat named {pet_name}. "
            "Art style: Soft watercolor painting with visible brush strokes and paper texture. "
            "Natural 3-4 head-to-body proportions, gentle and organic line quality. "
            "Warm, muted color palette inspired by children's book illustration. "
            "{features}. "
            "Soft pencil sketch underlayer visible through watercolor washes. "
            "The cat is in a natural relaxed sitting pose with slight head tilt. "
            "Subtle paper grain texture throughout the illustration. "
            "Clean white background, character centered. "
            "Style reference: Beatrix Potter, classic children's book art. "
            "{quality_tags}"
        ),
        "realistic": (
            "A photorealistic digital illustration of a {breed} cat named {pet_name}. "
            "Art style: Hyper-realistic pet portrait, photorealistic rendering. "
            "True-to-life proportions with anatomically correct features. "
            "Incredibly detailed fur texture with individual hair strands visible. "
            "Realistic eye reflections, wet nose highlight, whisker detail. "
            "{features}. "
            "Natural lighting with soft rim light highlighting fur edges. "
            "The cat is sitting in an elegant pose, looking at viewer with alert expression. "
            "Studio-quality lighting on clean white background. "
            "Style reference: professional pet photography, high-end digital painting. "
            "{quality_tags}"
        ),
    },
    "dog": {
        "chibi": (
            "A cute chibi-style illustration of a {breed} dog named {pet_name}. "
            "Art style: Japanese kawaii chibi, 2-3 head-to-body ratio. "
            "Large sparkling round eyes with star-shaped highlights, button nose, "
            "happy open mouth with tongue out. "
            "{features}. "
            "Plump rounded body, short sturdy limbs, oversized floppy or perky ears. "
            "Smooth clean outlines with playful cel-shading. "
            "Warm and vibrant color palette, friendly and approachable feel. "
            "The dog is sitting with tail wagging, facing slightly to the left (3/4 view). "
            "Clean white background, character centered in frame. "
            "Style reference: Doggie Dash, Nintendogs aesthetic. "
            "{quality_tags}"
        ),
        "hand_drawn": (
            "A warm hand-drawn watercolor illustration of a {breed} dog named {pet_name}. "
            "Art style: Soft watercolor painting with expressive brushwork. "
            "Natural 3-4 head-to-body proportions, friendly and approachable design. "
            "Warm golden-hour color palette with soft shadows. "
            "{features}. "
            "Visible pencil sketch lines adding character and charm. "
            "The dog is in a happy sitting pose with tail curved upward. "
            "Watercolor bleeds and splatters adding artistic texture. "
            "Clean white background, character centered. "
            "Style reference: classic Disney watercolor concepts, Garfield comic art. "
            "{quality_tags}"
        ),
        "realistic": (
            "A photorealistic digital illustration of a {breed} dog named {pet_name}. "
            "Art style: Hyper-realistic pet portrait with studio-quality rendering. "
            "True-to-life proportions, every whisker and fur strand meticulously rendered. "
            "Realistic wet nose texture, sparkling eye reflections, tongue moisture detail. "
            "{features}. "
            "Professional studio lighting with key light and fill light setup. "
            "The dog is sitting attentively, ears perked, looking at viewer with loyal expression. "
            "Clean white background, sharp focus on the subject. "
            "Style reference: AKC official portraits, professional pet photography. "
            "{quality_tags}"
        ),
    },
}


# ============================================================
# 动画帧序列生成 Prompt 模板
# ============================================================
# 帧序列图: 生成一张包含所有帧的横向sprite sheet线稿
# 参数：{breed}, {style}, {features}, {action_description}, {frame_count}, {frame_layout}

ANIMATION_PROMPTS = {
    "cat": {
        "chibi": (
            "A horizontal sprite sheet animation strip of a chibi {breed} cat, "
            "showing {frame_count} sequential frames of the action: {action_description}. "
            "Layout: {frame_layout}. Each frame shows the next moment in the animation sequence. "
            "Art style: Consistent Japanese kawaii chibi style across ALL frames, 2-3 head ratio. "
            "Same character design in every frame - identical colors, proportions, features. "
            "{features}. "
            "Each frame is separated by thin vertical guide lines. "
            "Clean white background, no shadows between frames. "
            "The animation should show smooth, natural movement progression. "
            "All frames must maintain consistent character size and position. "
            "Animation reference: classic 2D sprite animation, pixel-perfect consistency. "
            "{quality_tags}"
        ),
        "hand_drawn": (
            "A horizontal sprite sheet animation strip of a hand-drawn {breed} cat, "
            "showing {frame_count} sequential frames of the action: {action_description}. "
            "Layout: {frame_layout}. Each frame shows the next moment of animation. "
            "Art style: Consistent watercolor illustration style across ALL frames. "
            "Same character design, colors and proportions in every frame. "
            "{features}. "
            "Soft watercolor washes consistent between frames, gentle animation movement. "
            "Clean white background with subtle paper texture. "
            "Frames separated by light pencil guide lines. "
            "Smooth natural movement progression across the sequence. "
            "Style reference: traditional hand-drawn animation cels. "
            "{quality_tags}"
        ),
        "realistic": (
            "A horizontal sprite sheet animation strip of a realistic {breed} cat, "
            "showing {frame_count} sequential frames of the action: {action_description}. "
            "Layout: {frame_layout}. Each frame captures a precise moment in the animation. "
            "Art style: Photorealistic rendering, consistent across ALL frames. "
            "Identical character appearance, fur pattern, and proportions in every frame. "
            "{features}. "
            "Professional lighting consistent across all frames. "
            "Clean white background, each frame precisely the same dimensions. "
            "Smooth realistic movement captured in each frame. "
            "Reference: high-quality game sprite animation. "
            "{quality_tags}"
        ),
    },
    "dog": {
        "chibi": (
            "A horizontal sprite sheet animation strip of a chibi {breed} dog, "
            "showing {frame_count} sequential frames of the action: {action_description}. "
            "Layout: {frame_layout}. Each frame shows the next moment in the animation sequence. "
            "Art style: Consistent Japanese kawaii chibi style across ALL frames, 2-3 head ratio. "
            "Same character design in every frame - identical colors, proportions, features. "
            "{features}. "
            "Each frame is separated by thin vertical guide lines. "
            "Clean white background, no shadows between frames. "
            "Smooth natural movement progression, consistent character size and position. "
            "Animation reference: classic 2D sprite animation for desktop pet. "
            "{quality_tags}"
        ),
        "hand_drawn": (
            "A horizontal sprite sheet animation strip of a hand-drawn {breed} dog, "
            "showing {frame_count} sequential frames of the action: {action_description}. "
            "Layout: {frame_layout}. Each frame shows the next moment of animation. "
            "Art style: Consistent warm watercolor illustration across ALL frames. "
            "Same character design, colors and proportions maintained in every frame. "
            "{features}. "
            "Consistent watercolor washes, gentle hand-drawn animation movement. "
            "Clean white background with subtle paper texture. "
            "Frames separated by light pencil guide lines. "
            "Style reference: traditional 2D animation sprite sheet. "
            "{quality_tags}"
        ),
        "realistic": (
            "A horizontal sprite sheet animation strip of a realistic {breed} dog, "
            "showing {frame_count} sequential frames of the action: {action_description}. "
            "Layout: {frame_layout}. Each frame captures a precise animation moment. "
            "Art style: Photorealistic rendering consistent across ALL frames. "
            "Identical character appearance, fur pattern, proportions in every frame. "
            "{features}. "
            "Professional studio lighting maintained across all frames. "
            "Clean white background, precisely identical frame dimensions. "
            "Realistic smooth movement progression. "
            "Reference: AAA game quality sprite animation. "
            "{quality_tags}"
        ),
    },
}


# ============================================================
# 帧序列布局描述辅助函数
# ============================================================

def get_frame_layout(frame_count: int) -> str:
    """根据帧数生成布局描述"""
    return (
        f"{frame_count} equal-sized frames arranged in a single horizontal row, "
        f"reading left to right. Frame 1 is the starting pose, "
        f"frame {frame_count} is the final pose. "
        f"Each frame is the same size as the others."
    )


# ============================================================
# Prompt 构建函数
# ============================================================

def build_character_prompt(
    species: str,
    breed: str,
    pet_name: str,
    features: str,
    style: str = "chibi",
) -> tuple[str, str]:
    """
    构建角色生成prompt
    返回: (prompt, negative_prompt)
    """
    species = species.lower().strip()
    style = style.lower().strip()

    # 获取风格预设
    style_info = STYLE_PRESETS.get(style, STYLE_PRESETS["chibi"])

    # 获取模板
    species_prompts = CHARACTER_PROMPTS.get(species, CHARACTER_PROMPTS["cat"])
    template = species_prompts.get(style, species_prompts.get("chibi", ""))

    # 构建特征描述
    feature_desc = _build_feature_description(species, features)

    # 填充模板
    prompt = template.format(
        pet_name=pet_name,
        breed=breed,
        features=feature_desc,
        style_specific=style_info.get("display_name", ""),
        quality_tags=QUALITY_TAGS,
    )

    return prompt, NEGATIVE_PROMPT


def build_animation_prompt(
    species: str,
    breed: str,
    features: str,
    style: str,
    action: dict,
) -> tuple[str, str]:
    """
    构建动画帧序列生成prompt
    返回: (prompt, negative_prompt)
    """
    species = species.lower().strip()
    style = style.lower().strip()

    # 获取模板
    species_prompts = ANIMATION_PROMPTS.get(species, ANIMATION_PROMPTS["cat"])
    template = species_prompts.get(style, species_prompts.get("chibi", ""))

    # 构建特征描述
    feature_desc = _build_feature_description(species, features)

    # 填充模板
    prompt = template.format(
        breed=breed,
        features=feature_desc,
        action_description=action.get("prompt_hint", action.get("description", "")),
        frame_count=action["frames"],
        frame_layout=get_frame_layout(action["frames"]),
        quality_tags=QUALITY_TAGS,
    )

    return prompt, NEGATIVE_PROMPT_ANIMATION


def _build_feature_description(species: str, features: str) -> str:
    """将特征字符串转换为prompt中的自然语言描述"""
    if not features or features.strip() == "":
        return "Typical breed appearance with standard coloring"

    # 特征关键词映射
    feature_map = {
        # 猫
        "橘色": "orange tabby coloring with classic mackerel stripes",
        "白色": "pure white fluffy fur",
        "黑色": "sleek black fur with green eyes",
        "灰色": "grey/silver fur with striking patterns",
        "三花": "calico pattern with patches of orange, black, and white",
        "蓝猫": "solid blue-grey (Russian Blue) coloring with copper eyes",
        "暹罗": "cream body with dark color points on face, ears, paws, and tail, blue eyes",
        "加菲": "Persian/Exotic Shorthair with flat face and long luxurious fur",
        "英短": "British Shorthair with dense plush coat and round face",
        "蓝白": "blue and white bicolor pattern",
        "虎斑": "tabby striped pattern with bold markings",
        # 狗
        "金色": "golden retriever coloring, warm golden coat",
        "黄色": "yellow coat with soft cream undertones",
        "棕色": "rich brown/chocolate coloring",
        "黑白": "black and white bicolor pattern",
        "柯基": "corgi proportions with short legs and long body",
        "柴犬": "Shiba Inu appearance with fox-like features",
        "哈士奇": "Husky markings with blue or heterochromia eyes",
        "泰迪": "Teddy bear cut with curly fluffy coat",
        "贵宾": "Poodle with curly hypoallergenic coat",
        "比熊": "Bichon Frise with puffy white cotton-ball coat",
    }

    desc_parts = []
    for key, english_desc in feature_map.items():
        if key in features:
            desc_parts.append(english_desc)

    # 添加未被映射的原始特征
    remaining = features
    for key in feature_map:
        remaining = remaining.replace(key, "").replace("，", ",").replace("、", ",")
    remaining = remaining.strip(" ,，、")
    if remaining:
        desc_parts.append(f"additional features: {remaining}")

    if not desc_parts:
        desc_parts = [features]

    return ". ".join(desc_parts)


# ============================================================
# 命令行测试
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("PetPal Prompt 模板库测试")
    print("=" * 70)

    # 测试角色生成prompt
    print("\n📸 角色生成 Prompt (猫/Q版):")
    prompt, neg = build_character_prompt(
        species="cat", breed="British Shorthair",
        pet_name="Mimi", features="蓝白, 圆脸, 大眼睛", style="chibi"
    )
    print(f"  Prompt: {prompt[:200]}...")
    print(f"  Negative: {neg[:100]}...")

    print("\n📸 角色生成 Prompt (狗/写实):")
    prompt, neg = build_character_prompt(
        species="dog", breed="Golden Retriever",
        pet_name="Buddy", features="金色, 大耳朵, 微笑表情", style="realistic"
    )
    print(f"  Prompt: {prompt[:200]}...")

    # 测试动画prompt
    from action_library import get_action
    print("\n🎬 动画帧序列 Prompt (猫/端坐):")
    action = get_action("cat", "sit")
    prompt, neg = build_animation_prompt(
        species="cat", breed="British Shorthair",
        features="蓝白", style="chibi", action=action
    )
    print(f"  Prompt: {prompt[:200]}...")
    print(f"  Negative: {neg[:100]}...")

    print("\n✅ 所有prompt模板测试通过")
