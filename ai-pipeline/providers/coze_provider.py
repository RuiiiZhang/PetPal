"""
PetPal AI管线 - Coze内置生图提供商
使用Coze平台内置的图像生成能力作为fallback方案
"""

import sys
import time
import requests
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from providers.base import BaseProvider
from config import COZE_API_KEY, COZE_API_BASE, COZE_BOT_ID, COZE_TIMEOUT


class CozeProvider(BaseProvider):
    """
    Coze 内置生图提供商
    作为fallback方案，当Flux和Midjourney不可用时使用
    通过Coze Bot API调用内置生图能力
    """

    def __init__(self, api_key: str = None, api_base: str = None, bot_id: str = None):
        super().__init__("coze")
        self.api_key = api_key or COZE_API_KEY
        self.api_base = api_base or COZE_API_BASE
        self.bot_id = bot_id or COZE_BOT_ID
        if not self.api_key:
            raise ValueError("Coze API Key 未配置，请设置 COZE_API_KEY 环境变量")
        if not self.bot_id:
            raise ValueError("Coze Bot ID 未配置，请设置 COZE_BOT_ID 环境变量")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _chat_and_get_image(self, prompt: str, timeout: int = None) -> str:
        """通过Coze对话获取生成的图片URL"""
        timeout = timeout or COZE_TIMEOUT
        url = f"{self.api_base}/v3/chat"

        # 创建对话
        payload = {
            "bot_id": self.bot_id,
            "user_id": "petpal_pipeline",
            "stream": False,
            "auto_save_history": False,
            "additional_messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "content_type": "text",
                }
            ],
        }

        resp = requests.post(url, headers=self._headers(), json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        chat_id = data.get("data", {}).get("id", "")
        if not chat_id:
            raise RuntimeError(f"Coze 创建对话失败: {data}")

        # 轮询获取结果
        start = time.time()
        poll_url = f"{self.api_base}/v3/chat/retrieve"

        while time.time() - start < timeout:
            poll_payload = {"chat_id": chat_id, "conversation_id": ""}
            resp = requests.post(
                poll_url, headers=self._headers(), json=poll_payload, timeout=15
            )
            resp.raise_for_status()
            result = resp.json()
            status = result.get("data", {}).get("status", "")

            if status == "completed":
                # 获取消息列表
                msg_url = f"{self.api_base}/v3/chat/message/list"
                msg_resp = requests.get(
                    msg_url, headers=self._headers(),
                    params={"chat_id": chat_id}, timeout=15
                )
                msg_resp.raise_for_status()
                messages = msg_resp.json().get("data", [])

                # 查找图片消息
                for msg in messages:
                    if msg.get("type") == "answer":
                        content = msg.get("content", "")
                        # 尝试提取图片URL
                        image_url = self._extract_image_url(content)
                        if image_url:
                            return image_url
                raise RuntimeError("Coze 返回中未找到图片")

            elif status in ("failed", "error"):
                raise RuntimeError(f"Coze 生成失败: {result}")

            time.sleep(3)

        raise TimeoutError(f"Coze 生成超时 ({timeout}s)")

    def _extract_image_url(self, content: str) -> str:
        """从消息内容中提取图片URL"""
        # Coze可能在内容中返回markdown格式的图片
        import re
        # 匹配 ![...](url) 格式
        match = re.search(r'!\[.*?\]\((https?://[^\)]+)\)', content)
        if match:
            return match.group(1)
        # 匹配纯URL
        match = re.search(r'(https?://\S+\.(?:png|jpg|jpeg|webp))', content)
        if match:
            return match.group(1)
        return ""

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
        """使用Coze生成角色图"""
        full_prompt = f"请生成以下图片：{prompt}"
        if negative_prompt:
            full_prompt += f"。请避免：{negative_prompt}"
        full_prompt += f"。图片尺寸 {width}x{height}，白色背景，居中构图。"

        print(f"  [Coze] 提交角色生成任务...")
        image_url = self._chat_and_get_image(full_prompt)

        print(f"  [Coze] 下载图片...")
        result_path = self._download_image(image_url, output_path)
        print(f"  [Coze] ✅ 角色图已保存: {result_path}")
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
        """使用Coze生成动画帧序列"""
        full_prompt = (
            f"请生成一张包含{frame_count}个连续帧的横向精灵表动画序列图。"
            f"{prompt}。"
            f"所有帧横向排列在同一张图片中，帧与帧之间用细线分隔。"
            f"图片尺寸 {width}x{height}，白色背景。"
        )
        if negative_prompt:
            full_prompt += f"请避免：{negative_prompt}。"

        print(f"  [Coze] 提交帧序列生成任务 ({frame_count}帧)...")
        image_url = self._chat_and_get_image(full_prompt)

        print(f"  [Coze] 下载帧序列图...")
        result_path = self._download_image(image_url, output_path)
        print(f"  [Coze] ✅ 帧序列已保存: {result_path}")
        return result_path

    def health_check(self) -> bool:
        """检查Coze API是否可用"""
        try:
            resp = requests.get(
                f"{self.api_base}/v1/bots",
                headers=self._headers(),
                params={"space_id": "0"},
                timeout=10
            )
            return resp.status_code == 200
        except Exception:
            return False


# ============================================================
# 命令行测试
# ============================================================
if __name__ == "__main__":
    print("🧪 CozeProvider 测试")
    try:
        provider = CozeProvider()
        print(f"  健康检查: {provider.health_check()}")
    except ValueError as e:
        print(f"  ⚠️ 配置缺失: {e}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
