// ============================================================
// PetPal Desktop Pet - 前端主逻辑
// ============================================================
import { appWindow } from "@tauri-apps/api/window";
import { invoke } from "@tauri-apps/api/tauri";
import { listen } from "@tauri-apps/api/event";

// ─── 类型定义 ───────────────────────────────────────────────

interface BehaviorConfig {
  start_frame: number;
  frame_count: number;
  fps: number;
  loop: boolean;
  next_behavior?: string;
  columns: number;
}

interface PetConfig {
  pet_name: string;
  species: string;
  size: number;
  sprite_sheet: string;
  behaviors: Record<string, BehaviorConfig>;
  random_behavior_weights: Record<string, number>;
  idle_timeout: number;
}

// ─── 全局状态 ───────────────────────────────────────────────

let config: PetConfig;
let spriteSheet: HTMLImageElement;
let canvas: HTMLCanvasElement;
let ctx: CanvasRenderingContext2D;
let frameWidth = 0;
let frameHeight = 0;
let currentBehavior = "idle";
let currentFrame = 0;
let lastFrameTime = 0;
let lastInteractionTime = Date.now();
let isDragging = false;
let dragOffset = { x: 0, y: 0 };
let nameHideTimer: ReturnType<typeof setTimeout> | null = null;

// ─── 初始化 ─────────────────────────────────────────────────

async function init() {
  canvas = document.getElementById("pet-canvas") as HTMLCanvasElement;
  ctx = canvas.getContext("2d")!;

  // 尝试加载配置 - 打包后在资源目录, 开发时在template目录
  try {
    const configText = await loadResource("config.json");
    config = JSON.parse(configText);
  } catch {
    console.warn("无法加载config.json，使用默认配置");
    config = {
      pet_name: "小宠",
      species: "cat",
      size: 200,
      sprite_sheet: "spritesheet.png",
      behaviors: {
        idle: { start_frame: 0, frame_count: 5, fps: 3, loop: true, columns: 10 },
      },
      random_behavior_weights: { idle: 100 },
      idle_timeout: 30,
    };
  }

  // 加载精灵表
  spriteSheet = new Image();
  spriteSheet.onload = () => {
    const behaviorKeys = Object.keys(config.behaviors);
    const firstBehavior = config.behaviors[behaviorKeys[0]];
    const columns = firstBehavior.columns || 10;
    frameWidth = spriteSheet.width / columns;
    frameHeight = spriteSheet.height / Math.ceil(getTotalFrames() / columns);

    canvas.width = config.size;
    canvas.height = config.size;

    // 启动动画循环
    requestAnimationFrame(animationLoop);
    // 启动随机行为定时器
    startRandomBehaviorTimer();
  };

  try {
    spriteSheet.src = await loadResourceUrl(config.sprite_sheet);
  } catch {
    console.warn("无法加载精灵表，使用占位绘制");
    spriteSheet.src = "";
    canvas.width = config.size;
    canvas.height = config.size;
    requestAnimationFrame(animationLoop);
  }

  setupInteraction();
  setupContextMenu();
  setupNameDisplay();
  setupTauriEvents();
}

// ─── 资源加载 ───────────────────────────────────────────────

async function loadResource(path: string): Promise<string> {
  // Tauri环境: 通过resource protocol加载
  try {
    const resp = await fetch(`asset://localhost/${path}`);
    if (resp.ok) return await resp.text();
  } catch { /* fallback */ }
  // 开发环境
  const resp = await fetch(path);
  return await resp.text();
}

async function loadResourceUrl(path: string): Promise<string> {
  try {
    // 检查Tauri环境
    const { convertFileSrc } = await import("@tauri-apps/api/tauri");
    // 在Tauri中，资源文件需要使用convertFileSrc
    return path;
  } catch {
    return path;
  }
}

function getTotalFrames(): number {
  let total = 0;
  for (const b of Object.values(config.behaviors)) {
    total = Math.max(total, b.start_frame + b.frame_count);
  }
  return total;
}

// ─── 帧动画系统 ─────────────────────────────────────────────

function animationLoop(timestamp: number) {
  const behavior = config.behaviors[currentBehavior];
  if (!behavior) {
    currentBehavior = "idle";
    requestAnimationFrame(animationLoop);
    return;
  }

  const frameInterval = 1000 / behavior.fps;

  if (timestamp - lastFrameTime >= frameInterval) {
    lastFrameTime = timestamp;
    currentFrame++;

    if (currentFrame >= behavior.frame_count) {
      if (behavior.loop) {
        currentFrame = 0;
      } else {
        // 非循环动画结束后切换到指定行为
        currentBehavior = behavior.next_behavior || "idle";
        currentFrame = 0;
      }
    }

    drawFrame();
  }

  requestAnimationFrame(animationLoop);
}

function drawFrame() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!spriteSheet || !spriteSheet.complete || spriteSheet.naturalWidth === 0) {
    // 占位绘制
    drawPlaceholder();
    return;
  }

  const behavior = config.behaviors[currentBehavior];
  if (!behavior) return;

  const actualFrame = behavior.start_frame + currentFrame;
  const columns = behavior.columns || 10;
  const sx = (actualFrame % columns) * frameWidth;
  const sy = Math.floor(actualFrame / columns) * frameHeight;

  ctx.drawImage(
    spriteSheet,
    sx, sy, frameWidth, frameHeight,
    0, 0, canvas.width, canvas.height
  );
}

function drawPlaceholder() {
  // 简单的占位圆形
  ctx.fillStyle = "#6c5ce7";
  ctx.beginPath();
  ctx.arc(canvas.width / 2, canvas.height / 2, 40, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "#fff";
  ctx.font = "14px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(config?.pet_name || "Pet", canvas.width / 2, canvas.height / 2 + 5);
}

// ─── 鼠标交互 ───────────────────────────────────────────────

function setupInteraction() {
  const app = document.getElementById("app")!;

  // 悬浮 → 歪头
  canvas.addEventListener("mouseenter", () => {
    lastInteractionTime = Date.now();
    if (currentBehavior === "idle" || currentBehavior === "walk") {
      playOneShot("tilt_head");
      document.getElementById("app")?.classList.add("tilting");
      setTimeout(() => {
        document.getElementById("app")?.classList.remove("tilting");
      }, 400);
    }
    showPetName();
  });

  // 点击 → 翻肚皮
  canvas.addEventListener("click", (e) => {
    if (isDragging) return;
    lastInteractionTime = Date.now();
    playOneShot("belly_up");
    document.getElementById("app")?.classList.add("belly-up");
    setTimeout(() => {
      document.getElementById("app")?.classList.remove("belly-up");
    }, 800);
  });

  // 拖拽 → 移动窗口
  canvas.addEventListener("mousedown", (e) => {
    if (e.button === 0) {
      isDragging = false;
      dragOffset.x = e.screenX - window.screenX;
      dragOffset.y = e.screenY - window.screenY;
    }
  });

  window.addEventListener("mousemove", async (e) => {
    if (e.buttons === 1) {
      const dx = e.screenX - dragOffset.x - window.screenX;
      const dy = e.screenY - dragOffset.y - window.screenY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        isDragging = true;
        try {
          const pos = await appWindow.outerPosition();
          await appWindow.setPosition(
            new (await import("@tauri-apps/api/window")).LogicalPosition(
              pos.x + dx,
              pos.y + dy
            )
          );
        } catch {
          // 非Tauri环境忽略
        }
        dragOffset.x = e.screenX - window.screenX;
        dragOffset.y = e.screenY - window.screenY;
      }
    }
  });

  window.addEventListener("mouseup", () => {
    setTimeout(() => { isDragging = false; }, 50);
  });
}

function playOneShot(behaviorName: string) {
  if (config.behaviors[behaviorName]) {
    currentBehavior = behaviorName;
    currentFrame = 0;
    lastFrameTime = 0;
  }
}

// ─── 随机行为 ───────────────────────────────────────────────

function startRandomBehaviorTimer() {
  setInterval(() => {
    const elapsed = (Date.now() - lastInteractionTime) / 1000;
    if (elapsed >= config.idle_timeout && currentBehavior === "idle") {
      switchRandomBehavior();
    }
  }, 5000);
}

function switchRandomBehavior() {
  const weights = config.random_behavior_weights;
  const entries = Object.entries(weights);
  const totalWeight = entries.reduce((sum, [, w]) => sum + w, 0);
  let random = Math.random() * totalWeight;

  for (const [behavior, weight] of entries) {
    random -= weight;
    if (random <= 0) {
      currentBehavior = behavior;
      currentFrame = 0;
      lastFrameTime = 0;
      return;
    }
  }
}

// ─── 宠物名字显示 ───────────────────────────────────────────

function setupNameDisplay() {
  const nameEl = document.getElementById("pet-name")!;
  nameEl.textContent = config.pet_name;

  canvas.addEventListener("mouseenter", showPetName);
  canvas.addEventListener("mouseleave", hidePetName);
}

function showPetName() {
  const nameEl = document.getElementById("pet-name")!;
  nameEl.classList.remove("hidden");
  nameEl.classList.add("visible");

  if (nameHideTimer) clearTimeout(nameHideTimer);
  nameHideTimer = setTimeout(() => {
    hidePetName();
  }, 3000);
}

function hidePetName() {
  const nameEl = document.getElementById("pet-name")!;
  nameEl.classList.remove("visible");
  nameEl.classList.add("hidden");
}

// ─── 右键菜单 ───────────────────────────────────────────────

function setupContextMenu() {
  const menu = document.getElementById("context-menu")!;
  const resizeDialog = document.getElementById("resize-dialog")!;
  const sizeSlider = document.getElementById("size-slider") as HTMLInputElement;

  // 右键弹出菜单
  canvas.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    menu.style.left = e.clientX + "px";
    menu.style.top = e.clientY + "px";
    menu.classList.remove("hidden");
  });

  // 点击其他区域关闭菜单
  document.addEventListener("click", () => {
    menu.classList.add("hidden");
  });

  // 菜单项点击
  menu.addEventListener("click", (e) => {
    const item = (e.target as HTMLElement).closest(".menu-item") as HTMLElement;
    if (!item) return;
    const action = item.dataset.action;
    menu.classList.add("hidden");

    switch (action) {
      case "resize":
        resizeDialog.classList.remove("hidden");
        sizeSlider.value = String(config.size);
        break;
      case "name":
        const newName = prompt("输入宠物名字:", config.pet_name);
        if (newName && newName.trim()) {
          config.pet_name = newName.trim();
          document.getElementById("pet-name")!.textContent = config.pet_name;
        }
        break;
      case "hide":
        appWindow.hide();
        break;
      case "quit":
        appWindow.close();
        break;
    }
  });

  // 大小调整确认
  document.getElementById("size-confirm")!.addEventListener("click", async () => {
    const newSize = parseInt(sizeSlider.value);
    config.size = newSize;
    canvas.width = newSize;
    canvas.height = newSize;
    resizeDialog.classList.add("hidden");

    try {
      await invoke("set_pet_size", { size: newSize });
    } catch { /* 非Tauri环境 */ }
  });

  document.getElementById("size-cancel")!.addEventListener("click", () => {
    resizeDialog.classList.add("hidden");
  });
}

// ─── Tauri事件监听 ──────────────────────────────────────────

async function setupTauriEvents() {
  try {
    await listen("resize-dialog", () => {
      document.getElementById("resize-dialog")!.classList.remove("hidden");
    });
  } catch { /* 非Tauri环境 */ }
}

// ─── 启动 ───────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", init);
