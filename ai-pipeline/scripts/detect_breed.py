"""
PetPal AI管线 - 品种检测脚本
支持百度AI API和mock模式
用法: python scripts/detect_breed.py <image_path> [--mock]
"""

import sys
import json
import base64
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BAIDU_API_KEY, BAIDU_SECRET_KEY, BAIDU_DETECT_URL


# ============================================================
# 品种名称映射（中英文对照）
# ============================================================
BREED_MAP = {
    # 猫
    "波斯猫": "Persian",
    "英国短毛猫": "British Shorthair",
    "美国短毛猫": "American Shorthair",
    "暹罗猫": "Siamese",
    "布偶猫": "Ragdoll",
    "俄罗斯蓝猫": "Russian Blue",
    "加菲猫": "Exotic Shorthair",
    "苏格兰折耳猫": "Scottish Fold",
    "孟买猫": "Bombay",
    "橘猫": "Orange Tabby",
    "狸花猫": "Dragon Li",
    "三花猫": "Calico",
    # 狗
    "金毛寻回犬": "Golden Retriever",
    "拉布拉多": "Labrador Retriever",
    "柯基": "Corgi",
    "柴犬": "Shiba Inu",
    "哈士奇": "Siberian Husky",
    "贵宾犬": "Poodle",
    "比熊犬": "Bichon Frise",
    "泰迪犬": "Toy Poodle",
    "边境牧羊犬": "Border Collie",
    "萨摩耶": "Samoyed",
    "法国斗牛犬": "French Bulldog",
    "德国牧羊犬": "German Shepherd",
}


def get_access_token(api_key: str, secret_key: str) -> str:
    """获取百度AI access_token"""
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key,
    }
    import requests
    resp = requests.post(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"获取token失败: {data}")
    return data["access_token"]


def detect_breed_baidu(image_path: str, api_key: str = None, secret_key: str = None) -> dict:
    """
    使用百度AI API检测宠物品种
    返回: {"species": "cat"|"dog", "breed_cn": "英短", "breed_en": "British Shorthair", "confidence": 0.95}
    """
    import requests

    api_key = api_key or BAIDU_API_KEY
    secret_key = secret_key or BAIDU_SECRET_KEY

    if not api_key or not secret_key:
        raise ValueError("百度AI API密钥未配置")

    # 获取access_token
    token = get_access_token(api_key, secret_key)

    # 读取图片并base64编码
    img_path = Path(image_path)
    img_data = img_path.read_bytes()
    img_b64 = base64.b64encode(img_data).decode("utf-8")

    # 调用动物识别API
    url = f"{BAIDU_DETECT_URL}?access_token={token}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = requests.post(url, headers=headers, data={"image": img_b64}, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "result" not in data or len(data["result"]) == 0:
        raise RuntimeError(f"百度AI未检测到动物: {data}")

    # 取置信度最高的结果
    top_result = data["result"][0]
    name = top_result.get("name", "未知")
    confidence = float(top_result.get("confidence", 0))

    # 判断物种
    species = "unknown"
    breed_en = name
    for cn_name, en_name in BREED_MAP.items():
        if cn_name in name or name in cn_name:
            breed_en = en_name
            break

    # 简单物种判断
    cat_keywords = ["猫", "cat", "kitten"]
    dog_keywords = ["狗", "犬", "dog", "puppy"]
    if any(k in name for k in cat_keywords):
        species = "cat"
    elif any(k in name for k in dog_keywords):
        species = "dog"

    return {
        "species": species,
        "breed_cn": name,
        "breed_en": breed_en,
        "confidence": confidence,
        "raw_result": data["result"][:3],  # 前3个结果
    }


def detect_breed_mock(image_path: str) -> dict:
    """
    Mock模式的品种检测
    根据文件名或随机返回一个结果
    """
    import random
    filename = Path(image_path).stem.lower()

    # 尝试从文件名推断
    cat_names = ["cat", "猫", "kitty", "mimi", "luna"]
    dog_names = ["dog", "狗", "puppy", "buddy", "max"]

    species = "cat"  # 默认
    if any(n in filename for n in dog_names):
        species = "dog"

    # 根据物种返回预设结果
    if species == "cat":
        breeds = [
            ("英国短毛猫", "British Shorthair"),
            ("橘猫", "Orange Tabby"),
            ("暹罗猫", "Siamese"),
            ("布偶猫", "Ragdoll"),
        ]
    else:
        breeds = [
            ("金毛寻回犬", "Golden Retriever"),
            ("柯基", "Corgi"),
            ("柴犬", "Shiba Inu"),
            ("哈士奇", "Siberian Husky"),
        ]

    breed_cn, breed_en = random.choice(breeds)
    confidence = random.uniform(0.85, 0.99)

    return {
        "species": species,
        "breed_cn": breed_cn,
        "breed_en": breed_en,
        "confidence": round(confidence, 3),
        "raw_result": [],
    }


def detect_breed(image_path: str, use_mock: bool = False, **kwargs) -> dict:
    """
    品种检测统一入口
    Args:
        image_path: 图片路径
        use_mock: 是否使用mock模式
    Returns:
        检测结果字典
    """
    if use_mock:
        print(f"  [品种检测] Mock模式...")
        result = detect_breed_mock(image_path)
    else:
        try:
            print(f"  [品种检测] 调用百度AI API...")
            result = detect_breed_baidu(image_path, **kwargs)
        except Exception as e:
            print(f"  [品种检测] 百度API失败 ({e})，回退到Mock模式")
            result = detect_breed_mock(image_path)

    print(f"  [品种检测] 结果: {result['breed_cn']} ({result['breed_en']}) "
          f"置信度:{result['confidence']:.1%} 物种:{result['species']}")
    return result


# ============================================================
# 命令行入口
# ============================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PetPal 品种检测")
    parser.add_argument("image", help="待检测的图片路径")
    parser.add_argument("--mock", action="store_true", help="使用Mock模式")
    parser.add_argument("--output", "-o", help="输出结果JSON路径")
    args = parser.parse_args()

    if not Path(args.image).exists():
        print(f"❌ 图片不存在: {args.image}")
        sys.exit(1)

    result = detect_breed(args.image, use_mock=args.mock)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        print(f"✅ 结果已保存: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
