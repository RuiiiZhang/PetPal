# PetPal 桌宠桌面程序模板

基于 Tauri 框架的桌宠桌面程序模板。后端打包时动态注入精灵表和配置，生成绿色免安装的 exe 文件。

## 项目结构

```
desktop-pet/
├── src-tauri/           # Rust 后端
│   ├── Cargo.toml       # Rust 依赖
│   ├── tauri.conf.json  # Tauri 配置
│   ├── src/main.rs      # 主入口
│   └── build.rs         # 构建脚本
├── src/                 # 前端
│   ├── index.html       # HTML 入口
│   ├── main.ts          # 主逻辑（动画、交互）
│   └── styles.css       # 样式
├── template/
│   └── config.json      # 配置模板（打包时替换占位符）
├── builder/
│   └── build_pet.py     # 打包脚本
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 功能特性

- 🪟 透明无边框窗口，始终置顶
- 🖱️ 鼠标悬浮歪头、点击翻肚皮
- ✋ 拖拽移动桌宠位置
- 🎬 帧动画播放器，支持多行为切换
- ⏱️ 空闲30秒自动切换行为（walk/sit/sleep）
- 📛 鼠标悬浮显示宠物名字
- 📐 右键菜单：调整大小、修改名字、隐藏、退出
- 🖥️ 系统托盘支持

## 开发模式

```bash
# 安装依赖
npm install

# 开发模式（需要 Rust + Tauri CLI）
npm run tauri dev

# 构建
npm run tauri build
```

## 打包脚本

```bash
python builder/build_pet.py \
  --order-id ORDER_001 \
  --sprite-sheet /path/to/spritesheet.png \
  --config /path/to/config.json
```

产物输出到 `output/{order_id}/delivery/`

## 配置模板

`template/config.json` 中支持 `{{PET_NAME}}`、`{{SPECIES}}` 占位符，打包脚本会自动替换为实际值。
