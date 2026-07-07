# PetPal Backend

自动宠物桌宠搭建平台后端服务。

用户上传宠物照片 → AI 生成角色和动画 → 打包桌宠程序 + 动态贴纸包 → 用户下载。

## 技术栈

- **框架**: FastAPI (Python 3.10+)
- **数据库**: SQLite + SQLAlchemy
- **AI 服务**: 支持 Flux / Midjourney / Coze / Mock
- **支付**: 虎皮椒（支持 Mock 模式）
- **图像处理**: Pillow

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并按需修改：

```bash
cp .env.example .env
```

**最低启动配置**（Mock 模式，无需任何 API Key）：

```env
AI_PROVIDER=mock
PAYMENT_MODE=mock
```

### 3. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health
- 根路径: http://localhost:8000/

## 项目结构

```
backend/
├── app/
│   ├── main.py                  # FastAPI 主入口
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   └── database.py          # 数据库初始化
│   ├── models/
│   │   ├── schemas.py           # Pydantic 模型
│   │   └── db_models.py         # SQLAlchemy ORM 模型
│   ├── api/
│   │   └── routes.py            # API 路由
│   └── services/
│       ├── ai_provider.py       # AI 提供商抽象层
│       ├── pet_detector.py      # 品种识别服务
│       ├── character_generator.py   # 角色生成服务
│       ├── animation_generator.py   # 动画生成服务
│       ├── sprite_builder.py    # 精灵表构建服务
│       ├── desktop_pet_builder.py   # 桌宠打包服务
│       ├── sticker_generator.py # 贴纸包生成服务
│       ├── package_builder.py   # 最终打包服务
│       └── payment_service.py   # 支付服务
├── uploads/                     # 用户上传文件
├── output/                      # 生成产物
├── data/                        # 数据库文件
├── requirements.txt
├── .env.example
└── README.md
```

## API 接口文档

### 健康检查
```
GET /api/health
```

### 上传宠物照片
```
POST /api/upload
Content-Type: multipart/form-data

字段:
  photo:     图片文件 (jpg/png/webp)
  pet_name:  宠物名字 (str)
  style:     风格: cute / handdrawn / realistic

返回:
  {"code": 0, "data": {"order_id": "xxx", "species": "cat", "breed": "tabby", "features": {...}}}
```

### 生成角色预览
```
POST /api/generate-character
Content-Type: application/json

{"order_id": "xxx"}

返回:
  {"code": 0, "data": {"preview_url": "/output/xxx/character_preview.png"}}
```

### 确认角色
```
POST /api/confirm-character
Content-Type: application/json

{"order_id": "xxx", "approved": true/false}

返回:
  {"code": 0, "data": {"status": "character_confirmed"}}
  {"code": 0, "data": {"status": "regenerating", "preview_url": "..."}}
```

### 生成动画
```
POST /api/generate-animation
Content-Type: application/json

{"order_id": "xxx"}

返回:
  {"code": 0, "data": {"preview_url": "/output/xxx/animation_preview.gif", "actions": [...]}}
```

### 确认动画
```
POST /api/confirm-animation
Content-Type: application/json

{"order_id": "xxx", "approved": true/false}

返回:
  {"code": 0, "data": {"status": "animation_confirmed"}}
```

### 创建支付
```
POST /api/payment/create
Content-Type: application/json

{"order_id": "xxx", "plan": "basic/standard/premium"}

返回:
  {"code": 0, "data": {"payment_url": "...", "payment_id": "..."}}
```

### 支付回调
```
POST /api/payment/callback
Content-Type: application/x-www-form-urlencoded

字段: trade_no, order_id, money, status, hash
```

### 查询订单状态
```
GET /api/order/{order_id}/status

返回:
  {"code": 0, "data": {"order_id": "...", "status": "...", "payment_status": "...", "download_url": "..."}}
```

### 下载产物
```
GET /api/order/{order_id}/download

返回: ZIP 文件下载流
```

### Mock 支付（仅测试）
```
GET /api/payment/mock_pay?order_id=xxx&amount=29.9
```

## 订单状态流转

```
created → detected → character_generated → character_confirmed
    → animation_generated → animation_confirmed → paid
    → building → completed
```

## 套餐价格

| 套餐 | 价格 | 内容 |
|------|------|------|
| 基础版 basic | ¥19.9 | 桌宠程序 |
| 标准版 standard | ¥29.9 | 桌宠程序 + 贴纸包 |
| 高级版 premium | ¥49.9 | 桌宠程序 + 贴纸包 + 源文件 |

## 配置说明

所有配置通过环境变量或 `.env` 文件管理，详见 `.env.example`。

### AI 提供商切换

设置 `AI_PROVIDER` 环境变量：
- `mock` - Mock 模式（默认），生成占位图，无需 API Key
- `flux` - Flux AI 生图
- `midjourney` - Midjourney 代理
- `coze` - Coze 工作流

### 支付模式

设置 `PAYMENT_MODE` 环境变量：
- `mock` - Mock 模式（默认），直接模拟支付成功
- `production` - 真实虎皮椒支付

## 数据库

使用 SQLite，数据库文件位于 `./data/petpal.db`。首次启动自动创建。

如需重置数据库：
```bash
rm data/petpal.db
# 重启服务即可自动重建
```
