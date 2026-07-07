# PetPal API Integration Guide

## 概述

本文档详细说明 PetPal 前端如何与后端 API 交互，以及第三方网站如何接入 PetPal 功能。

---

## 1. 环境配置

### 1.1 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `NEXT_PUBLIC_API_URL` | 后端 API 基础地址 | `http://localhost:8000` |
| `NEXT_PUBLIC_IMAGE_HOST` | 图片资源的域名（用于 Next.js Image 优化） | `**`（允许所有） |

### 1.2 配置方式

在项目根目录创建 `.env.local` 文件：

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_IMAGE_HOST=cdn.yourdomain.com
```

或通过启动命令注入：

```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com npm run dev
```

### 1.3 开发环境快速启动

```bash
cd frontend
npm install
npm run dev
# 默认访问 http://localhost:3000
```

后端需在同一网络下运行于 `http://localhost:8000`，或在 `.env.local` 中指定后端地址。

---

## 2. API 接口文档

所有 API 基础路径由 `NEXT_PUBLIC_API_URL` 决定。

### 2.1 POST /api/upload

上传宠物照片和基本信息。

**请求格式：** `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `photo` | File[] | ✅ | 宠物照片，支持多张，JPG/PNG |
| `pet_name` | string | ✅ | 宠物名字 |
| `style` | string | ✅ | 风格：`cute` / `realistic` / `cartoon` |

**请求示例：**

```bash
curl -X POST http://localhost:8000/api/upload \
  -F "photo=@cat1.jpg" \
  -F "photo=@cat2.jpg" \
  -F "pet_name=小橘" \
  -F "style=cute"
```

**响应示例：**

```json
{
  "order_id": "ord_abc123def456",
  "pet_breed": "British Shorthair",
  "message": "Upload successful"
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `order_id` | 订单唯一标识，后续所有操作都需要此 ID |
| `pet_breed` | AI 识别的宠物品种 |
| `message` | 操作结果消息 |

---

### 2.2 POST /api/generate-character

触发 AI 角色图生成。此接口为耗时操作（可能需要 10-60 秒）。

**请求格式：** `application/json`

```json
{
  "order_id": "ord_abc123def456"
}
```

**响应示例：**

```json
{
  "status": "success",
  "image_url": "/uploads/characters/ord_abc123def456.png",
  "message": "Character generated successfully"
}
```

**注意：** `image_url` 可能是相对路径（相对于 `NEXT_PUBLIC_API_URL`）或绝对 URL。前端通过 `resolveImageUrl()` 工具函数自动处理。

---

### 2.3 POST /api/confirm-character

确认或拒绝生成的角色图。

**请求格式：** `application/json`

```json
{
  "order_id": "ord_abc123def456",
  "approved": true
}
```

**响应示例：**

```json
{
  "status": "confirmed",
  "message": "Character approved"
}
```

- `approved: true` — 确认满意，可进入动画生成阶段
- `approved: false` — 不满意，可重新调用 `generate-character` 生成新图

---

### 2.4 POST /api/generate-animation

基于确认的角色图生成动画（GIF/序列帧）。

**请求格式：** `application/json`

```json
{
  "order_id": "ord_abc123def456"
}
```

**响应示例：**

```json
{
  "status": "success",
  "image_url": "/uploads/animations/ord_abc123def456.gif",
  "message": "Animation generated successfully"
}
```

---

### 2.5 POST /api/confirm-animation

确认或拒绝生成的动画。

**请求格式：** `application/json`

```json
{
  "order_id": "ord_abc123def456",
  "approved": true
}
```

**响应示例：**

```json
{
  "status": "confirmed",
  "message": "Animation approved"
}
```

---

### 2.6 POST /api/payment/create

创建支付订单。

**请求格式：** `application/json`

```json
{
  "order_id": "ord_abc123def456"
}
```

**响应示例：**

```json
{
  "payment_url": "https://pay.example.com/checkout?token=xxx",
  "order_id": "ord_abc123def456",
  "amount": 29.00,
  "message": "Payment created"
}
```

**字段说明：**

| 字段 | 说明 |
|------|------|
| `payment_url` | 支付网关跳转地址（微信/支付宝收银台） |
| `amount` | 应付金额（元） |

---

### 2.7 GET /api/order/{order_id}/status

查询订单状态（用于轮询支付结果）。

**响应示例：**

```json
{
  "status": "paid",
  "order_id": "ord_abc123def456"
}
```

**状态枚举：**

| 状态值 | 说明 |
|--------|------|
| `uploading` | 上传中 |
| `processing` | 处理中 |
| `character_ready` | 角色图已生成 |
| `animation_ready` | 动画已生成 |
| `paid` | 已支付 |
| `completed` | 已完成，可下载 |

---

### 2.8 GET /api/order/{order_id}/download

获取已支付订单的下载文件列表。

**响应示例：**

```json
{
  "files": [
    {
      "name": "PetPal_Desktop_v1.0.zip",
      "url": "/downloads/ord_abc123def456/desktop-pet.zip",
      "size": "45.2 MB",
      "type": "desktop_pet"
    },
    {
      "name": "PetPal_Stickers_v1.0.zip",
      "url": "/downloads/ord_abc123def456/stickers.zip",
      "size": "12.8 MB",
      "type": "sticker_pack"
    },
    {
      "name": "QuickStart_Guide.pdf",
      "url": "/downloads/guide.pdf",
      "size": "1.2 MB",
      "type": "guide"
    }
  ],
  "message": "Download links ready"
}
```

**文件类型枚举：**

| type | 说明 |
|------|------|
| `desktop_pet` | 桌宠程序主文件 |
| `sticker_pack` | 动态贴纸包 |
| `guide` | 使用指南 |

---

## 3. 网站接入方式

### 3.1 方式一：完整嵌入（iframe）

将 PetPal 整个制作流程嵌入你的网站。

```html
<iframe
  src="https://petpal.yourdomain.com"
  width="100%"
  height="800"
  frameborder="0"
  style="border: none; border-radius: 16px; overflow: hidden;"
  allow="camera; microphone"
></iframe>
```

**优点：** 零开发成本，完整体验
**注意：** 需要后端配置 CORS 和 `X-Frame-Options`

**后端配置（Nginx 示例）：**

```nginx
add_header X-Frame-Options "ALLOW-FROM https://yourdomain.com";
add_header Content-Security-Policy "frame-ancestors 'self' https://yourdomain.com";
```

---

### 3.2 方式二：部分嵌入（嵌入特定步骤）

只嵌入某个步骤页面，与你的页面布局融合。

```html
<!-- 嵌入上传步骤 -->
<iframe
  src="https://petpal.yourdomain.com/upload?embed=true&order_id=ord_xxx"
  width="600"
  height="500"
  frameborder="0"
></iframe>

<!-- 嵌入风格选择 -->
<iframe
  src="https://petpal.yourdomain.com/style?embed=true&order_id=ord_xxx"
  width="600"
  height="400"
  frameborder="0"
></iframe>
```

---

### 3.3 方式三：纯 API 调用

直接调用 PetPal API，在你自己的前端中实现 UI。

```javascript
// 1. 上传照片
const formData = new FormData();
formData.append('photo', file1);
formData.append('photo', file2);
formData.append('pet_name', 'Mochi');
formData.append('style', 'cute');

const uploadRes = await fetch('https://api.petpal.com/api/upload', {
  method: 'POST',
  body: formData,
});
const { order_id } = await uploadRes.json();

// 2. 生成角色
const genRes = await fetch('https://api.petpal.com/api/generate-character', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ order_id }),
});
const { image_url } = await genRes.json();

// 3. 确认角色
await fetch('https://api.petpal.com/api/confirm-character', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ order_id, approved: true }),
});

// 4. 生成动画
const animRes = await fetch('https://api.petpal.com/api/generate-animation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ order_id }),
});
const { image_url: animation_url } = await animRes.json();

// 5. 确认动画
await fetch('https://api.petpal.com/api/confirm-animation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ order_id, approved: true }),
});

// 6. 创建支付
const payRes = await fetch('https://api.petpal.com/api/payment/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ order_id }),
});
const { payment_url, amount } = await payRes.json();

// 7. 轮询支付状态
const statusRes = await fetch(`https://api.petpal.com/api/order/${order_id}/status`);
const { status } = await statusRes.json();

// 8. 获取下载链接
const dlRes = await fetch(`https://api.petpal.com/api/order/${order_id}/download`);
const { files } = await dlRes.json();
```

---

## 4. 支付回调（Webhook）

### 4.1 回调配置

后端需实现支付回调接口，接收支付网关的异步通知。

**回调流程：**

```
用户支付 → 支付网关 → Webhook → PetPal后端 → 更新订单状态
```

### 4.2 Webhook 接口规范

PetPal 后端应提供以下 Webhook 端点：

```
POST /api/webhook/payment
```

**请求头：**

```
X-Signature: sha256=xxxxx
Content-Type: application/json
```

**请求体：**

```json
{
  "event": "payment.success",
  "order_id": "ord_abc123def456",
  "amount": 29.00,
  "payment_method": "wechat",
  "timestamp": "2025-01-15T10:30:00Z",
  "signature": "hmac_sha256_signature"
}
```

### 4.3 前端轮询替代方案

若不想实现 Webhook，前端可通过轮询 `GET /api/order/{order_id}/status` 来获取支付状态：

```javascript
const pollPayment = async (orderId, maxAttempts = 30) => {
  for (let i = 0; i < maxAttempts; i++) {
    const res = await fetch(`/api/order/${orderId}/status`);
    const { status } = await res.json();
    
    if (status === 'paid' || status === 'completed') {
      return true; // Payment confirmed
    }
    
    await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2s
  }
  return false; // Timeout
};
```

---

## 5. 自定义主题色

### 5.1 修改 TailwindCSS 配置

编辑 `tailwind.config.ts` 中的 `theme.extend.colors`：

```typescript
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      accent: {
        DEFAULT: '#YOUR_COLOR', // 主点缀色
        50: '#LIGHT_VARIANT',
        // ... 其他色阶
      },
      surface: {
        DEFAULT: '#YOUR_BG', // 背景色
      },
      panel: {
        DEFAULT: '#YOUR_CARD_BG', // 卡片背景色
      },
    },
  },
},
```

### 5.2 通过 CSS 变量覆盖

在 `globals.css` 中添加 CSS 变量：

```css
:root {
  --accent-color: #d4a574;
  --surface-bg: #0f0f0f;
  --panel-bg: #161616;
  --text-primary: #f5f0eb;
  --text-secondary: #a09890;
}
```

### 5.3 当前配色方案

| 用途 | 颜色 | 说明 |
|------|------|------|
| 背景 | `#0f0f0f` | 纯黑背景 |
| 卡片 | `#161616` | 微亮的面板 |
| 点缀色 | `#d4a574` | 温暖琥珀金 |
| 主文字 | `#f5f0eb` | 暖白色 |
| 副文字 | `#a09890` | 柔和灰 |
| 边框 | `rgba(212,165,116,0.12)` | 微妙金色边框 |
| 标题字体 | Playfair Display | 衬线体 |
| 正文字体 | Inter | 无衬线体 |

---

## 6. 错误处理

所有 API 错误返回统一格式：

```json
{
  "detail": "Error message here"
}
```

HTTP 状态码约定：

| 状态码 | 含义 |
|--------|------|
| `200` | 成功 |
| `400` | 请求参数错误 |
| `404` | 订单不存在 |
| `422` | 数据验证失败 |
| `500` | 服务器内部错误 |

前端在 `src/lib/api.ts` 的响应拦截器中统一处理错误。

---

## 7. CORS 配置

后端需配置 CORS 以允许前端跨域访问：

```python
# FastAPI 示例
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://petpal.yourdomain.com",
        "https://partner-site.com",  # 合作方
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 8. 部署建议

### 8.1 前端部署

```bash
# 构建
npm run build

# 启动（推荐 Node.js 环境）
npm start

# 或使用 Docker
docker build -t petpal-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://api.petpal.com petpal-frontend
```

### 8.2 环境变量注入

生产环境中，`NEXT_PUBLIC_*` 变量在构建时写入，需重新构建以更改配置。如需运行时动态配置，建议使用 Next.js 的 `public/runtime-config.json` 方案。

---

## 9. 联系与支持

- API 技术支持：tech@petpal.com
- 商务合作：bd@petpal.com
- 文档更新：请查看项目 README 获取最新版本
