"""
桌宠打包服务
将精灵表 + 配置文件打包成 Tauri 桌面应用（exe/可执行文件）
注意：实际的 Tauri 编译需要 Rust 环境，这里提供配置模板生成 + 打包逻辑
"""

import os
import json
import shutil
from typing import Dict, Any
from app.core.config import settings


# Tauri 前端模板（极简 HTML + JS）
TAURI_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{pet_name} - PetPal Desktop Pet</title>
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{
            background: transparent;
            overflow: hidden;
            user-select: none;
            -webkit-app-region: drag;
        }}
        #pet-container {{
            width: 256px;
            height: 256px;
            position: relative;
        }}
        #pet-sprite {{
            width: 128px;
            height: 128px;
            image-rendering: pixelated;
            position: absolute;
            bottom: 0;
            left: 64px;
        }}
        #pet-name {{
            position: absolute;
            bottom: -24px;
            left: 0;
            right: 0;
            text-align: center;
            font-family: 'Microsoft YaHei', sans-serif;
            font-size: 12px;
            color: #666;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        #pet-container:hover #pet-name {{
            opacity: 1;
        }}
        /* 右键菜单 */
        #context-menu {{
            display: none;
            position: fixed;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            padding: 4px 0;
            font-family: 'Microsoft YaHei', sans-serif;
            font-size: 13px;
            z-index: 1000;
        }}
        #context-menu .menu-item {{
            padding: 6px 16px;
            cursor: pointer;
            -webkit-app-region: no-drag;
        }}
        #context-menu .menu-item:hover {{
            background: #f0f0f0;
        }}
    </style>
</head>
<body>
    <div id="pet-container">
        <img id="pet-sprite" src="sprite_sheet.png" alt="{pet_name}">
        <div id="pet-name">{pet_name}</div>
    </div>
    <div id="context-menu">
        <div class="menu-item" onclick="changeAction('idle')">待机</div>
        <div class="menu-item" onclick="changeAction('walk')">散步</div>
        <div class="menu-item" onclick="changeAction('sleep')">睡觉</div>
        <div class="menu-item" onclick="changeAction('happy')">开心</div>
        <div class="menu-item" onclick="openSettings()">设置</div>
        <div class="menu-item" onclick="exitApp()">退出</div>
    </div>
    <script>
        const config = {config_json};
        let currentAction = 'idle';
        let frameIndex = 0;
        const sprite = document.getElementById('pet-sprite');
        const frameWidth = config.frame_width || 128;
        const frameHeight = config.frame_height || 128;

        function updateSprite() {{
            const action = config.actions.find(a => a.name === currentAction) || config.actions[0];
            if (!action) return;
            const row = config.actions.indexOf(action);
            const col = frameIndex % action.frame_count;
            sprite.style.clipPath = `inset(${{row * frameHeight}}px ${{(config.columns - col - 1) * frameWidth}}px ${{(config.rows - row - 1) * frameHeight}}px ${{col * frameWidth}}px)`;
            frameIndex = (frameIndex + 1) % action.frame_count;
        }}

        function changeAction(action) {{
            currentAction = action;
            frameIndex = 0;
            document.getElementById('context-menu').style.display = 'none';
        }}

        // 自动切换动作
        function autoAction() {{
            const actions = config.actions.map(a => a.name);
            const randomAction = actions[Math.floor(Math.random() * actions.length)];
            currentAction = randomAction;
            frameIndex = 0;
        }}

        setInterval(updateSprite, 1000 / 8); // 8fps
        setInterval(autoAction, 10000); // 每10秒随机切换

        // 右键菜单
        document.addEventListener('contextmenu', (e) => {{
            e.preventDefault();
            const menu = document.getElementById('context-menu');
            menu.style.display = 'block';
            menu.style.left = e.clientX + 'px';
            menu.style.top = e.clientY + 'px';
        }});

        document.addEventListener('click', () => {{
            document.getElementById('context-menu').style.display = 'none';
        }});

        function openSettings() {{ alert('PetPal Desktop Pet v1.0\\n宠物: {pet_name}\\n品种: {species}'); }}
        function exitApp() {{ if(confirm('确定退出吗？')) window.close(); }}
    </script>
</body>
</html>"""


class DesktopPetBuilder:
    """桌宠打包服务"""

    def build(
        self,
        order_id: str,
        pet_name: str,
        species: str,
        breed: str,
        sprite_sheet_path: str,
        sprite_metadata: Dict[str, Any]
    ) -> str:
        """
        构建桌宠程序包。

        生成一个可直接在浏览器中运行的桌宠 HTML 应用，
        以及 Tauri 项目配置（供有 Rust 环境的用户编译为 exe）。

        Args:
            order_id: 订单ID
            pet_name: 宠物名称
            species: 物种
            breed: 品种
            sprite_sheet_path: 精灵表图片路径
            sprite_metadata: 精灵表元数据

        Returns:
            str: 桌宠程序目录路径

        Raises:
            RuntimeError: 构建失败时抛出
        """
        try:
            output_dir = os.path.join(settings.OUTPUT_DIR, order_id)
            pet_dir = os.path.join(output_dir, "desktop_pet")
            os.makedirs(pet_dir, exist_ok=True)

            # 1. 复制精灵表
            dest_sprite = os.path.join(pet_dir, "sprite_sheet.png")
            shutil.copy2(sprite_sheet_path, dest_sprite)

            # 2. 生成配置文件
            config = {
                "pet_name": pet_name,
                "species": species,
                "breed": breed,
                "frame_width": sprite_metadata.get("frame_width", 128),
                "frame_height": sprite_metadata.get("frame_height", 128),
                "columns": sprite_metadata.get("columns", 4),
                "rows": sprite_metadata.get("rows", 1),
                "actions": sprite_metadata.get("actions", []),
                "version": "1.0.0",
                "engine": "petpal-v1"
            }

            config_path = os.path.join(pet_dir, "config.json")
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            # 3. 生成 HTML 桌面宠物
            config_json = json.dumps(config, ensure_ascii=False)
            html_content = TAURI_HTML_TEMPLATE.format(
                pet_name=pet_name,
                species=f"{species} ({breed})",
                config_json=config_json
            )
            html_path = os.path.join(pet_dir, "index.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # 4. 生成 Tauri 配置（供高级用户编译）
            self._generate_tauri_config(pet_dir, pet_name, config)

            # 5. 生成启动说明
            readme = f"""# {pet_name} - PetPal 桌面宠物

## 快速启动
1. 双击 `index.html` 即可在浏览器中运行
2. 推荐 Chrome / Edge 浏览器

## 操作说明
- 拖拽：直接拖动宠物窗口
- 右键：打开菜单（切换动作/退出）
- 宠物会自动在桌面上随机走动

## 编译为 EXE（可选）
如果你有 Rust 环境，可以使用 `tauri.conf.json` 编译：
```bash
npm install -g @tauri-apps/cli
tauri build
```

## 由 PetPal 自动生成
"""
            readme_path = os.path.join(pet_dir, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme)

            return pet_dir

        except Exception as e:
            raise RuntimeError(f"桌宠打包失败: {str(e)}")

    def _generate_tauri_config(
        self, pet_dir: str, pet_name: str, config: Dict
    ):
        """
        生成 Tauri 项目配置文件。

        Args:
            pet_dir: 桌宠目录
            pet_name: 宠物名称
            config: 应用配置
        """
        tauri_conf = {
            "build": {
                "distDir": ".",
                "devPath": ".",
            },
            "package": {
                "productName": f"{pet_name}-PetPal",
                "version": "1.0.0"
            },
            "tauri": {
                "windows": [
                    {
                        "title": f"{pet_name} - PetPal",
                        "width": 256,
                        "height": 256,
                        "transparent": True,
                        "decorations": False,
                        "alwaysOnTop": True,
                        "resizable": False,
                    }
                ],
                "allowlist": {
                    "all": False
                }
            }
        }

        tauri_path = os.path.join(pet_dir, "tauri.conf.json")
        with open(tauri_path, "w", encoding="utf-8") as f:
            json.dump(tauri_conf, f, indent=2, ensure_ascii=False)


# 全局单例
desktop_pet_builder = DesktopPetBuilder()
