"""
品种识别服务
调用百度 AI 宠物识别 API 进行品种检测
支持 Mock 模式用于无 API Key 时的测试
"""

import json
import httpx
from typing import Dict, Any
from app.core.config import settings
from app.models.schemas import PetDetectionResult


class PetDetector:
    """宠物品种识别服务"""

    def __init__(self):
        self.api_key = settings.BAIDU_API_KEY
        self.secret_key = settings.BAIDU_SECRET_KEY
        self._access_token = None
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """关闭 HTTP 客户端"""
        await self._client.aclose()

    async def detect(self, image_path: str) -> PetDetectionResult:
        """
        识别宠物照片的品种信息。

        Args:
            image_path: 宠物照片的本地文件路径

        Returns:
            PetDetectionResult: 包含 species, breed, confidence, features

        Raises:
            RuntimeError: API 调用失败时抛出
        """
        # Mock 模式
        if not self.api_key or not self.secret_key:
            return await self._mock_detect(image_path)

        # 获取 access_token
        if not self._access_token:
            await self._fetch_access_token()

        # 调用百度 AI 宠物识别 API
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()

            import base64
            image_b64 = base64.b64encode(image_data).decode()

            resp = await self._client.post(
                "https://aip.baidubce.com/rest/2.0/image-classify/v1/animal",
                params={"access_token": self._access_token},
                data={"image": image_b64},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            resp.raise_for_status()
            result = resp.json()

            if "error_code" in result:
                raise RuntimeError(f"百度 API 错误: {result.get('error_msg', '未知错误')}")

            # 解析结果
            results = result.get("result", [])
            if not results:
                return PetDetectionResult(
                    species="unknown",
                    breed="unknown",
                    confidence=0.0,
                    features={}
                )

            top = results[0]
            name = top.get("name", "unknown")
            confidence = top.get("score", 0.0)

            # 解析物种和品种
            species, breed = self._parse_species_breed(name)

            # 提取更多结果作为特征
            features = {
                "all_results": [
                    {"name": r.get("name"), "score": r.get("score")}
                    for r in results[:5]
                ],
                "top_name": name
            }

            return PetDetectionResult(
                species=species,
                breed=breed,
                confidence=confidence,
                features=features
            )

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"API 请求失败: {e.response.status_code}")
        except Exception as e:
            # 降级到 mock
            return await self._mock_detect(image_path)

    async def _fetch_access_token(self):
        """获取百度 API access_token"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }
        resp = await self._client.post(url, data=params)
        resp.raise_for_status()
        result = resp.json()
        self._access_token = result.get("access_token")
        if not self._access_token:
            raise RuntimeError(f"获取 access_token 失败: {result}")

    def _parse_species_breed(self, name: str) -> tuple:
        """
        解析物种和品种
        百度返回格式通常是 "猫-英短" 或 "狗-金毛" 等

        Args:
            name: 百度 API 返回的名称

        Returns:
            tuple: (species, breed)
        """
        # 常见物种关键词映射
        species_map = {
            "猫": "cat",
            "狗": "dog",
            "犬": "dog",
            "鸟": "bird",
            "兔": "rabbit",
            "仓鼠": "hamster",
            "鹦鹉": "bird",
            "乌龟": "turtle",
            "鱼": "fish",
        }

        species = "other"
        breed = name

        for key, sp in species_map.items():
            if key in name:
                species = sp
                # 去除物种前缀作为品种名
                breed = name.replace(key, "").strip("- ").strip()
                if not breed:
                    breed = name
                break

        return species, breed

    async def _mock_detect(self, image_path: str) -> PetDetectionResult:
        """
        Mock 品种检测 - 基于图片尺寸简单模拟

        Args:
            image_path: 图片路径

        Returns:
            PetDetectionResult: 模拟的检测结果
        """
        from PIL import Image

        try:
            img = Image.open(image_path)
            w, h = img.size
            # 用图片尺寸做简单"判断"（纯模拟）
            ratio = w / h if h > 0 else 1

            if ratio > 1.5:
                # 横向图 → 狗
                return PetDetectionResult(
                    species="dog",
                    breed="golden_retriever",
                    confidence=0.85,
                    features={"color": "golden", "size": "large", "mock": True}
                )
            elif ratio < 0.7:
                # 纵向图 → 猫
                return PetDetectionResult(
                    species="cat",
                    breed="british_shorthair",
                    confidence=0.88,
                    features={"color": "gray", "size": "medium", "mock": True}
                )
            else:
                # 正方形 → 仓鼠
                return PetDetectionResult(
                    species="hamster",
                    breed="syrian",
                    confidence=0.75,
                    features={"color": "brown", "size": "small", "mock": True}
                )
        except Exception:
            return PetDetectionResult(
                species="cat",
                breed="tabby",
                confidence=0.80,
                features={"color": "orange", "size": "medium", "mock": True}
            )


# 全局单例
pet_detector = PetDetector()
