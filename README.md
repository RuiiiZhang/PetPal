# PetPal - 自动宠物桌宠搭建平台

一个让线下宠物店 5 分钟生成专属 App + AI 桌宠的 SaaS 平台。

## 📁 项目结构

```
PetPal/
├── frontend/           # 前端（Next.js 14）
├── backend/            # 后端（FastAPI）
├── ai-pipeline/        # AI 管线（图像/文案/桌宠生成）
├── desktop-pet/        # 桌宠客户端（Tauri）
└── deploy/             # 部署配置
```

## 🚀 快速开始

### 前端
```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# API 文档 http://localhost:8000/docs
```

## 🌐 部署到 Cloudflare Pages

1. Fork 本项目到你的 GitHub
2. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
3. 进入 **Workers & Pages** → **Create** → **Pages**
4. 选择 **Connect to Git** → 选择你的仓库
5. 配置：
   - **Framework preset**: Next.js
   - **Build command**: `npm run build`
   - **Build output**: `.next`
   - **Root directory**: `frontend`
6. 点击 **Save and Deploy**

部署完成后你会得到一个 `https://your-project.pages.dev` 的网址。

## 🔧 后端部署（Render）

1. 登录 [Render](https://render.com)
2. 创建 **Web Service** → 连接你的 GitHub
3. 配置：
   - **Root directory**: `backend`
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 添加环境变量（按需）
5. 部署

## 📝 环境变量

前端 `.env.local`:
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

后端 `.env`:
```
API_KEY=your_api_key
```

## 🛠️ 技术栈

- **前端**: Next.js 14, TypeScript, TailwindCSS
- **后端**: FastAPI, Python 3.10+
- **AI**: 图像生成、文案生成、桌宠构建
- **客户端**: Tauri (Rust + Vue)

## 📄 License

MIT
