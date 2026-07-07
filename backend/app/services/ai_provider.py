"""
AI 模型提供商抽象层
统一封装不同 AI 生图/视频服务的调用接口
支持: Flux / Midjourney / Coze / Mock
"""

import os
import json
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from app.core.config import settings


class AIProvider:
    """
    AI 模型提供商抽象层
    根据配置选择实际的 AI 服务后端
    """

    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self._client = httpx.AsyncClient(timeout=120.0)

    async def close(self):
        """关闭 HTTP 客户端"""
        await self._client.aclose()

    # ==================== 文本生图 ====================

    async def text_to_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
        negative_prompt: str = "",
        **kwargs
    ) -> str:
        """
        根据文本描述生成图片。

        Args:
            prompt: 图片描述文本
            output_path: 输出图片保存路径
            width: 图片宽度
            height: 图片高度
            negative_prompt: 负面提示词
            **kwargs: 各提供商特有参数

        Returns:
            str: 生成的图片本地路径
        """
        if self.provider == "mock":
            return await self._mock_text_to_image(prompt, output_path, width, height)
        elif self.provider == "flux":
            return await self._flux_text_to_image(prompt, output_path, width, height, negative_prompt)
        elif self.provider == "midjourney":
            return await self._mj_text_to_image(prompt, output_path, width, height)
        elif self.provider == "coze":
            return await self._coze_text_to_image(prompt, output_path, width, height)
        else:
            raise ValueError(f"不支持的 AI 提供商: {self.provider}")

    # ==================== 图片生图片 ====================

    async def image_to_image(
        self,
        image_path: str,
        prompt: str,
        output_path: str,
        strength: float = 0.7,
        **kwargs
    ) -> str:
        """
        基于参考图片 + 文本描述生成新图片（图生图）。

        Args:
            image_path: 参考图片路径
            prompt: 图片描述文本
            output_path: 输出图片保存路径
            strength: 变化强度 0-1
            **kwargs: 各提供商特有参数

        Returns:
            str: 生成的图片本地路径
        """
        if self.provider == "mock":
            return await self._mock_text_to_image(prompt, output_path)
        elif self.provider == "flux":
            return await self._flux_image_to_image(image_path, prompt, output_path, strength)
        elif self.provider == "coze":
            return await self._coze_image_to_image(image_path, prompt, output_path)
        else:
            # 其他提供商降级为文生图
            return await self.text_to_image(prompt, output_path)

    # ==================== 视频/动画生成 ====================

    async def generate_animation_frames(
        self,
        image_path: str,
        actions: list,
        output_dir: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        基于角色图生成动画帧序列。

        Args:
            image_path: 角色图片路径
            actions: 动作列表 [{"name": "idle", "frames": 8}, ...]
            output_dir: 帧图片输出目录

        Returns:
            dict: {"frames_dir": str, "actions": list}
        """
        if self.provider == "mock":
            return await self._mock_animation_frames(image_path, actions, output_dir)
        elif settings.AI_VIDEO_API_URL:
            return await self._api_animation_frames(image_path, actions, output_dir)
        else:
            return await self._mock_animation_frames(image_path, actions, output_dir)

    # ==================== Mock 实现 ====================

    async def _mock_text_to_image(
        self, prompt: str, output_path: str, width: int = 512, height: int = 512
    ) -> str:
        """Mock 文生图：生成纯色占位图"""
        from PIL import Image, ImageDraw, ImageFont
        import random

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 生成带文字提示的彩色占位图
        img = Image.new("RGBA", (width, height), (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
            255
        ))
        draw = ImageDraw.Draw(img)

        # 绘制中心文字
        text_lines = [
            "[MOCK] PetPal AI",
            f"Style: {prompt[:40]}...",
            f"Size: {width}x{height}"
        ]
        y = height // 2 - 30
        for line in text_lines:
            draw.text((width // 2 - 100, y), line, fill=(255, 255, 255, 200))
            y += 25

        # 绘制宠物图标占位
        draw.ellipse(
            [width // 4, height // 4, 3 * width // 4, 3 * height // 4],
            outline=(255, 255, 255, 150), width=3
        )

        img.save(output_path, "PNG")
        return output_path

    async def _mock_animation_frames(
        self, image_path: str, actions: list, output_dir: str
    ) -> Dict[str, Any]:
        """Mock 动画帧：生成简单的位移帧"""
        from PIL import Image
        import random

        os.makedirs(output_dir, exist_ok=True)
        result_actions = []

        for action in actions:
            action_name = action.get("name", "idle")
            frame_count = action.get("frames", 8)
            action_dir = os.path.join(output_dir, action_name)
            os.makedirs(action_dir, exist_ok=True)

            # 加载参考图或创建占位图
            try:
                base_img = Image.open(image_path).convert("RGBA")
                base_img = base_img.resize((128, 128))
            except Exception:
                base_img = Image.new("RGBA", (128, 128), (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255),
                    255
                ))

            for i in range(frame_count):
                frame = base_img.copy()
                # 简单位移模拟动画
                offset_x = int(5 * (i / frame_count * 2 * 3.14159))
                from PIL import ImageChops
                shifted = ImageChops.offset(frame, offset_x % 10, 0)
                frame_path = os.path.join(action_dir, f"frame_{i:04d}.png")
                shifted.save(frame_path, "PNG")

            result_actions.append({
                "name": action_name,
                "frame_count": frame_count,
                "frame_dir": action_dir,
                "fps": 8
            })

        return {
            "frames_dir": output_dir,
            "actions": result_actions
        }

    # ==================== Flux 实现 ====================

    async def _flux_text_to_image(
        self, prompt: str, output_path: str, width: int, height: int, negative_prompt: str
    ) -> str:
        """Flux API 文生图"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "negative_prompt": negative_prompt,
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
        }
        headers = {
            "Authorization": f"Bearer {settings.FLUX_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = await self._client.post(
            settings.FLUX_API_URL,
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
        result = resp.json()

        # 下载生成的图片
        image_url = result.get("image_url") or result.get("images", [{}])[0].get("url")
        if image_url:
            img_resp = await self._client.get(image_url)
            img_resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(img_resp.content)

        return output_path

    async def _flux_image_to_image(
        self, image_path: str, prompt: str, output_path: str, strength: float
    ) -> str:
        """Flux API 图生图"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        import base64

        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "prompt": prompt,
            "image": image_b64,
            "strength": strength,
            "num_inference_steps": 30,
        }
        headers = {
            "Authorization": f"Bearer {settings.FLUX_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = await self._client.post(
            settings.FLUX_API_URL + "/img2img",
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
        result = resp.json()

        image_url = result.get("image_url") or result.get("images", [{}])[0].get("url")
        if image_url:
            img_resp = await self._client.get(image_url)
            with open(output_path, "wb") as f:
                f.write(img_resp.content)

        return output_path

    # ==================== Midjourney 实现 ====================

    async def _mj_text_to_image(
        self, prompt: str, output_path: str, width: int, height: int
    ) -> str:
        """Midjourney 代理 API 文生图"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        payload = {
            "prompt": f"{prompt} --ar {width}:{height} --niji 6",
        }
        headers = {
            "Authorization": f"Bearer {settings.MJ_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = await self._client.post(
            settings.MJ_API_URL,
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
        result = resp.json()

        # MJ 通常是异步任务，需要轮询
        task_id = result.get("task_id") or result.get("id")
        if task_id:
            image_url = await self._poll_mj_result(task_id, headers)
            if image_url:
                img_resp = await self._client.get(image_url)
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)

        return output_path

    async def _poll_mj_result(self, task_id: str, headers: dict) -> Optional[str]:
        """轮询 Midjourney 任务结果"""
        import asyncio
        for _ in range(60):  # 最多等待 5 分钟
            await asyncio.sleep(5)
            resp = await self._client.get(
                f"{settings.MJ_API_URL}/task/{task_id}",
                headers=headers
            )
            result = resp.json()
            if result.get("status") == "completed":
                return result.get("image_url")
            elif result.get("status") == "failed":
                raise RuntimeError(f"MJ 任务失败: {result.get('error')}")
        return None

    # ==================== Coze 实现 ====================

    async def _coze_text_to_image(
        self, prompt: str, output_path: str, width: int, height: int
    ) -> str:
        """Coze 工作流 API 文生图"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        payload = {
            "workflow_id": "image_generation",
            "parameters": {
                "prompt": prompt,
                "width": width,
                "height": height,
            }
        }
        headers = {
            "Authorization": f"Bearer {settings.COZE_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = await self._client.post(
            settings.COZE_API_URL,
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
        result = resp.json()

        image_url = result.get("data", {}).get("image_url")
        if image_url:
            img_resp = await self._client.get(image_url)
            with open(output_path, "wb") as f:
                f.write(img_resp.content)

        return output_path

    async def _coze_image_to_image(
        self, image_path: str, prompt: str, output_path: str
    ) -> str:
        """Coze 工作流 API 图生图"""
        import base64

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "workflow_id": "image_to_image",
            "parameters": {
                "prompt": prompt,
                "image_base64": image_b64,
            }
        }
        headers = {
            "Authorization": f"Bearer {settings.COZE_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = await self._client.post(
            settings.COZE_API_URL,
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
        result = resp.json()

        image_url = result.get("data", {}).get("image_url")
        if image_url:
            img_resp = await self._client.get(image_url)
            with open(output_path, "wb") as f:
                f.write(img_resp.content)

        return output_path

    # ==================== 通用视频 API 实现 ====================

    async def _api_animation_frames(
        self, image_path: str, actions: list, output_dir: str
    ) -> Dict[str, Any]:
        """通过外部视频 API 生成动画帧"""
        import base64

        os.makedirs(output_dir, exist_ok=True)

        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode()

        payload = {
            "image": image_b64,
            "actions": actions,
        }
        headers = {
            "Authorization": f"Bearer {settings.AI_VIDEO_API_KEY}",
            "Content-Type": "application/json",
        }

        resp = await self._client.post(
            settings.AI_VIDEO_API_URL,
            json=payload,
            headers=headers
        )
        resp.raise_for_status()
        result = resp.json()

        # 保存返回的帧数据
        result_actions = []
        for action_data in result.get("actions", []):
            action_name = action_data["name"]
            action_dir = os.path.join(output_dir, action_name)
            os.makedirs(action_dir, exist_ok=True)

            for i, frame_b64 in enumerate(action_data.get("frames", [])):
                frame_path = os.path.join(action_dir, f"frame_{i:04d}.png")
                import base64
                with open(frame_path, "wb") as f:
                    f.write(base64.b64decode(frame_b64))

            result_actions.append({
                "name": action_name,
                "frame_count": len(action_data.get("frames", [])),
                "frame_dir": action_dir,
                "fps": action_data.get("fps", 8)
            })

        return {
            "frames_dir": output_dir,
            "actions": result_actions
        }


# 全局单例
ai_provider = AIProvider()
