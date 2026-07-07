"""
PetPal AI管线 - Midjourney API提供商
通过第三方代理API调用Midjourney生成图片
"""

import sys
import time
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from providers.base import BaseProvider
from config import MIDJOURNEY_API_KEY, MIDJOURNEY_API_BASE, MIDJOURNEY_TIMEOUT


class MidjourneyProvider(BaseProvider):
    """
    Midjourney API 提供商
    通过第三方代理服务调用Midjourney（如 midjourneyapi.xyz）
    """

    def __init__(self, api_key: str = None, api_base: str = None):
        super().__init__("midjourney")
        self.api_key = api_key or MIDJOURNEY_API_KEY
        self.api_base = api_base or MIDJOURNEY_API_BASE
        if not self.api_key:
            raise ValueError(
                "Midjourney API Key 未配置，请设置 MIDJOURNEY_API_KEY 环境变量"
            )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _submit_imagine(self, prompt: str, aspect_ratio: str = "1:1") -> str:
        """提交Imagine请求，返回任务ID"""
        url = f"{self.api_base}/imagine"
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "process_mode": "fast",
        }
        resp = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("id", "")

    def _poll_result(self, task_id: str, timeout: int = None) -> str:
        """轮询任务结果，返回图片URL"""
        timeout = timeout or MIDJOURNEY_TIMEOUT
        url = f"{self.api_base}/fetch"
        start = time.time()

        while time.time() - start < timeout:
            resp = requests.get(
                url, headers=self._headers(),
                params={"task_id": task_id}, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "")

            if status == "finished":
                return data.get("image_url", "")
            elif status in ("failed", "error"):
                raise RuntimeError(f"Midjourney 生成失败: {data}")

            time.sleep(5)

        raise TimeoutError(f"Midjourney 生成超时 ({timeout}s)")

    def _download_image(self, url: str, output_path: str) -> str:
        """下载图片到本地"""
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(resp.content)
        return str(output)

    def _build_prompt(self, prompt: str, negative_prompt: str = "") -> str:
        """构建Midjourney格式的prompt"""
        full_prompt = prompt
        if negative_prompt:
            full_prompt += f" --no {negative_prompt}"
        # 添加质量参数
        full_prompt += " --q 2 --s 750"
        return full_prompt

    def generate_character(
        self,
        photo_path: str,
        prompt: str,
        negative_prompt: str,
        output_path: str,
        width: int = 512,
        height: int = 512,
    ) -> str:
        """使用Midjourney生成角色图"""
        full_prompt = self._build_prompt(prompt, negative_prompt)
        print(f"  [Midjourney] 提交角色生成任务...")
        task_id = self._submit_imagine(full_prompt, "1:1")
        print(f"  [Midjourney] 任务ID: {task_id}")

        print(f"  [Midjourney] 等待生成完成（可能需要1-3分钟）...")
        image_url = self._poll_result(task_id)

        print(f"  [Midjourney] 下载图片...")
        result_path = self._download_image(image_url, output_path)
        print(f"  [Midjourney] ✅ 角色图已保存: {result_path}")
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
        """使用Midjourney生成动画帧序列"""
        # 帧序列使用宽幅比例
        aspect = "16:9" if frame_count <= 6 else "21:9"
        full_prompt = self._build_prompt(prompt, negative_prompt)
        full_prompt += f" --ar {aspect}"

        print(f"  [Midjourney] 提交帧序列生成任务 ({frame_count}帧, {aspect})...")
        task_id = self._submit_imagine(full_prompt, aspect)
        print(f"  [Midjourney] 任务ID: {task_id}")

        print(f"  [Midjourney] 等待生成完成...")
        image_url = self._poll_result(task_id)

        print(f"  [Midjourney] 下载帧序列图...")
        result_path = self._download_image(image_url, output_path)
        print(f"  [Midjourney] ✅ 帧序列已保存: {result_path}")
        return result_path

    def health_check(self) -> bool:
        """检查Midjourney API是否可用"""
        try:
            resp = requests.get(
                f"{self.api_base}/status",
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
    print("🧪 MidjourneyProvider 测试")
    try:
        provider = MidjourneyProvider()
        print(f"  健康检查: {provider.health_check()}")
    except ValueError as e:
        print(f"  ⚠️ 配置缺失: {e}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
