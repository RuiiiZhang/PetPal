"""
PetPal AI管线 - 动作库定义
定义每种宠物的所有动作，包括帧数、帧率、描述等信息
"""

# ============================================================
# 动作库：定义每个物种的标准动作集
# ============================================================
ACTIONS = {
    "cat": [
        {
            "name": "sit",
            "display": "端坐摇尾巴",
            "frames": 5,
            "fps": 3,
            "description": "猫咪端坐在地面上，尾巴缓慢左右摇摆",
            "prompt_hint": "sitting cat with tail gently swaying side to side, calm and dignified pose",
        },
        {
            "name": "walk",
            "display": "慢走散步",
            "frames": 6,
            "fps": 4,
            "description": "猫咪优雅地慢步行走，四肢交替迈步",
            "prompt_hint": "cat walking gracefully with alternating leg movement, elegant stride",
        },
        {
            "name": "stretch",
            "display": "伸懒腰",
            "frames": 4,
            "fps": 3,
            "description": "猫咪前爪向前伸展，背部弓起打哈欠",
            "prompt_hint": "cat stretching front paws forward, back arched, yawning slightly",
        },
        {
            "name": "sleep",
            "display": "趴下打瞌睡",
            "frames": 4,
            "fps": 2,
            "description": "猫咪趴下闭上眼睛，身体微微起伏呼吸",
            "prompt_hint": "sleeping cat lying down, eyes closed, body gently rising and falling with breathing",
        },
        {
            "name": "belly",
            "display": "翻肚皮",
            "frames": 5,
            "fps": 3,
            "description": "猫咪翻身露出肚皮，四肢微微摆动",
            "prompt_hint": "cat rolling over showing belly, paws slightly wiggling in the air",
        },
        {
            "name": "head_tilt",
            "display": "歪头好奇",
            "frames": 3,
            "fps": 2,
            "description": "猫咪歪头看向一侧，耳朵转动",
            "prompt_hint": "cat tilting head curiously to one side, ears perked and rotating",
        },
        {
            "name": "groom",
            "display": "舔爪子洗脸",
            "frames": 5,
            "fps": 3,
            "description": "猫咪抬起前爪舔舐，然后擦拭脸部",
            "prompt_hint": "cat grooming itself, lifting front paw to lick and then wiping face",
        },
        {
            "name": "yawn",
            "display": "打哈欠",
            "frames": 4,
            "fps": 2,
            "description": "猫咪张大嘴巴打哈欠，眼睛半眯",
            "prompt_hint": "cat yawning with mouth wide open, eyes half-closed, sleepy expression",
        },
    ],
    "dog": [
        {
            "name": "sit",
            "display": "端坐摇尾巴",
            "frames": 5,
            "fps": 3,
            "description": "狗狗端坐在地面，尾巴快速摇摆",
            "prompt_hint": "dog sitting upright with tail wagging enthusiastically side to side",
        },
        {
            "name": "walk",
            "display": "欢快散步",
            "frames": 6,
            "fps": 4,
            "description": "狗狗轻快地行走，耳朵随风飘动",
            "prompt_hint": "dog walking happily with bouncy gait, ears flopping with each step",
        },
        {
            "name": "shake",
            "display": "握手",
            "frames": 4,
            "fps": 3,
            "description": "狗狗抬起一只前爪，做出握手的姿势",
            "prompt_hint": "dog raising one front paw in a shaking hands gesture, eager expression",
        },
        {
            "name": "sleep",
            "display": "趴下睡觉",
            "frames": 4,
            "fps": 2,
            "description": "狗狗趴在地上睡觉，偶尔抽动爪子",
            "prompt_hint": "dog sleeping on ground, paws occasionally twitching, peaceful breathing",
        },
        {
            "name": "fetch",
            "display": "接飞盘",
            "frames": 5,
            "fps": 4,
            "description": "狗狗跳跃起来张嘴接住飞盘的动作",
            "prompt_hint": "dog jumping up to catch a frisbee, mouth open wide, excited expression",
        },
        {
            "name": "head_tilt",
            "display": "歪头卖萌",
            "frames": 3,
            "fps": 2,
            "description": "狗狗歪头看向一侧，表情呆萌",
            "prompt_hint": "dog tilting head adorably to one side, cute confused expression",
        },
        {
            "name": "spin",
            "display": "转圈圈",
            "frames": 6,
            "fps": 5,
            "description": "狗狗原地转圈，尾巴甩成螺旋",
            "prompt_hint": "dog spinning in circles happily, tail spinning like a propeller",
        },
        {
            "name": "beg",
            "display": "作揖讨食",
            "frames": 4,
            "fps": 3,
            "description": "狗狗后腿站立，前爪合在一起做作揖动作",
            "prompt_hint": "dog standing on hind legs, front paws together begging for food, hopeful eyes",
        },
    ],
}

# ============================================================
# 通用辅助函数
# ============================================================

def get_actions(species: str) -> list[dict]:
    """获取指定物种的动作列表"""
    species = species.lower().strip()
    if species in ACTIONS:
        return ACTIONS[species]
    # 模糊匹配
    for key in ACTIONS:
        if key in species or species in key:
            return ACTIONS[key]
    # 默认返回猫的动作
    return ACTIONS.get("cat", [])


def get_action(species: str, action_name: str) -> dict | None:
    """获取指定物种的单个动作定义"""
    for action in get_actions(species):
        if action["name"] == action_name:
            return action
    return None


def get_total_frames(species: str) -> int:
    """获取指定物种所有动作的总帧数"""
    return sum(a["frames"] for a in get_actions(species))


def get_all_action_names(species: str) -> list[str]:
    """获取指定物种所有动作的名称列表"""
    return [a["name"] for a in get_actions(species)]


def calculate_gif_duration(action: dict) -> int:
    """计算GIF每帧的毫秒间隔"""
    return int(1000 / action["fps"])


# ============================================================
# 命令行测试
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("PetPal 动作库")
    print("=" * 60)
    for species in ["cat", "dog"]:
        actions = get_actions(species)
        print(f"\n🐾 {species.upper()} ({len(actions)} 个动作):")
        for i, action in enumerate(actions, 1):
            duration = calculate_gif_duration(action)
            print(f"  {i}. {action['name']:12s} | {action['display']:10s} | "
                  f"帧数:{action['frames']} | FPS:{action['fps']} | "
                  f"间隔:{duration}ms")
        total = get_total_frames(species)
        print(f"  → 总帧数: {total}")
