"""
PetPal AI管线 - Flux API提供商
调用 Flux Pro / Flux Dev 模型生成角色图和动画帧序列
API文档: https://api.bfl.ml/
"""

import sys
import time
import json
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from providers.base import BaseProvider
from config import (
    FLUX_API_KEY, FLUX_API_BASE, FLUX_MODEL_CHARACTER,
    FLUX_MODEL_ANIMATION, FLUX_TIMEOUT
)


class FluxProvider(BaseProvider):
    """
    Flux API 提供商
    使用 BFL (Black Forest Labs) 的 Flux 模型生成图片
    支持 Flux Pro 1.1 和 Flux Dev
    """

    def __init__(self, api_key: str = None, api_base: str = None):
        super().__init__("flux")
        self.api_key = api_key or FLUX_API_KEY
        self.api_base = api_base or FLUX_API_BASE
        if not self.api_key:
            raise ValueError("Flux API Key 未配置，请设置 FLUX_API_KEY 环境变量")

    def _headers(self):
        return {
            "X-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _submit_request(self, model: str, prompt: str, width: int, height: int,
                        negative_prompt: str = "") -> str:
        """提交生图请求，返回任务ID"""
        url = f"{self.api_base}/{model}"
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": 25,
            "guidance": 3.5,
            "safety_tolerance": 2,
        }
        if negative_prompt:
            payload["prompt"] = f"{prompt}. Avoid: {negative_prompt}"

        resp = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("id", "")

    def _poll_result(self, task_id: str, timeout: int = None) -> str:
        """轮询任务结果，返回图片URL"""
        timeout = timeout or FLUX_TIMEOUT
        url = f"{self.api_base}/get_result"
        start = time.time()

        while time.time() - start < timeout:
            resp = requests.get(url, headers=self._headers(),
                              params={"id": task_id}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "")

            if status == "Ready":
                result = data.get("result", {})
                return result.get("sample", "")
            elif status in ("Failed", "Error"):
                raise RuntimeError(f"Flux 生成失败: {data}")

            time.sleep(2)

        raise TimeoutError(f"Flux 生成超时 ({timeout}s)")

    def _download_image(self, url: str, output_path: str) -> str:
        """下载图片到本地"""
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(resp.content)
        return str(output)

    def generate_character(
        self,
        photo_path: str,
        prompt: str,
        negative_prompt: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """使用 Flux 生成角色图"""
        print(f"  [Flux] 提交角色生成任务...")
        task_id = self._submit_request(
            FLUX_MODEL_CHARACTER, prompt, width, height, negative_prompt
        )
        print(f"  [Flux] 任务ID: {task_id}")

        print(f"  [Flux] 等待生成完成...")
        image_url = self._poll_result(task_id)

        print(f"  [Flux] 下载图片...")
        result_path = self._download_image(image_url, output_path)
        print(f"  [Flux] ✅ 角色图已保存: {result_path}")
        return result_path

    def generate_animation_frames(
        self,
        prompt: str,
        negative_prompt: str,
        output_path: str,
        frame_count: int,
        width: int = 1024,
        height: int = 256,
    ) -> str:
        """使用 Flux 生成动画帧序列"""
        print(f"  [Flux] 提交帧序列生成任务 ({frame_count}帧)...")
        task_id = self._submit_request(
            FLUX_MODEL_ANIMATION, prompt, width, height, negative_prompt
        )
        print(f"  [Flux] 任务ID: {task_id}")

        print(f"  [Flux] 等待生成完成...")
        image_url = self._poll_result(task_id)

        print(f"  [Flux] 下载帧序列图...")
        result_path = self._download_image(image_url, output_path)
        print(f"  [Flux] ✅ 帧序列已保存: {result_path}")
        return result_path

    def health_check(self) -> bool:
        """检查Flux API是否可用"""
        try:
            resp = requests.get(
                f"{self.api_base}/health",
                headers=self._headers(),
                timeout=10
            )
            return resp.status_code == 200
        except Exception:
            return False


# ============================================================
# 命令行测试
# ============================================================
if __name__ == "__main__":
    print("🧪 FluxProvider 测试")
    try:
        provider = FluxProvider()
        print(f"  健康检查: {provider.health_check()}")
    except ValueError as e:
        print(f"  ⚠️ 配置缺失: {e}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
