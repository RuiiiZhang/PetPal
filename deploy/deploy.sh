#!/bin/bash
# ============================================================
# PetPal 一键部署脚本
# 适用于阿里云 ECS / 任何 Ubuntu/CentOS 服务器
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# ─── 颜色输出 ────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── 检查依赖 ────────────────────────────────────────────────
check_prerequisites() {
    info "检查依赖..."

    if ! command -v docker &> /dev/null; then
        error "Docker 未安装，正在安装..."
        install_docker
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose 未安装，正在安装..."
        install_compose
    fi

    info "✅ 依赖检查通过"
}

install_docker() {
    info "安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    info "✅ Docker 安装完成"
}

install_compose() {
    info "安装 Docker Compose..."
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
    curl -SL "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" \
        -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    info "✅ Docker Compose 安装完成"
}

# ─── 初始化环境 ──────────────────────────────────────────────
init_env() {
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        warn ".env 文件不存在，从模板创建..."
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"

        # 生成随机数据库密码
        DB_PASS=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 20)
        sed -i "s/change_this_to_a_strong_password/$DB_PASS/" "$SCRIPT_DIR/.env"

        info "已创建 .env 文件，请根据需要修改配置"
        warn "请编辑 $SCRIPT_DIR/.env 设置 SITE_URL 和其他配置"
    fi
}

# ─── 构建并启动 ──────────────────────────────────────────────
deploy() {
    info "开始部署 PetPal..."

    cd "$SCRIPT_DIR"

    # 构建镜像
    info "构建 Docker 镜像..."
    docker compose build --parallel

    # 启动服务
    info "启动服务..."
    docker compose up -d

    # 等待服务就绪
    info "等待服务就绪..."
    sleep 10

    # 健康检查
    if curl -sf http://localhost/api/health > /dev/null 2>&1; then
        info "✅ 后端服务正常"
    else
        warn "后端服务可能需要更多时间启动，请稍后检查"
    fi

    if curl -sf http://localhost > /dev/null 2>&1; then
        info "✅ 前端服务正常"
    else
        warn "前端服务可能需要更多时间启动，请稍后检查"
    fi

    info "🎉 部署完成！"
    echo ""
    info "访问地址: http://$(hostname -I | awk '{print $1}')"
    info "查看日志: docker compose logs -f"
    info "停止服务: docker compose down"
}

# ─── HTTPS 证书 ──────────────────────────────────────────────
setup_https() {
    info "配置 HTTPS 证书..."

    source "$SCRIPT_DIR/.env"

    if [ -z "$CERTBOT_DOMAIN" ] || [ "$CERTBOT_DOMAIN" = "your-domain.com" ]; then
        error "请先在 .env 中设置 CERTBOT_DOMAIN"
        exit 1
    fi

    # 申请证书
    docker run -it --rm \
        -v "$SCRIPT_DIR/certbot_etc:/etc/letsencrypt" \
        -v "$SCRIPT_DIR/certbot_var:/var/lib/letsencrypt" \
        certbot/certbot certonly --standalone \
        -d "$CERTBOT_DOMAIN" \
        --email "$CERTBOT_EMAIL" \
        --agree-tos \
        --non-interactive

    info "✅ 证书已申请，请更新 nginx.conf 启用 HTTPS 配置"
}

# ─── 自动续期证书 ────────────────────────────────────────────
setup_auto_renew() {
    info "设置证书自动续期..."

    CRON_CMD="0 3 * * * cd $SCRIPT_DIR && docker compose run --rm certbot certbot renew --quiet && docker compose exec nginx nginx -s reload"

    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

    info "✅ 已添加证书自动续期 cron 任务（每天凌晨3点）"
}

# ─── 主入口 ──────────────────────────────────────────────────
main() {
    echo ""
    echo "========================================"
    echo "  🐾 PetPal 部署工具"
    echo "========================================"
    echo ""

    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            init_env
            deploy
            ;;
        https)
            setup_https
            ;;
        renew)
            setup_auto_renew
            ;;
        stop)
            info "停止所有服务..."
            cd "$SCRIPT_DIR" && docker compose down
            info "✅ 已停止"
            ;;
        restart)
            cd "$SCRIPT_DIR" && docker compose restart
            info "✅ 已重启"
            ;;
        logs)
            cd "$SCRIPT_DIR" && docker compose logs -f "${@:2}"
            ;;
        *)
            echo "用法: $0 {deploy|https|renew|stop|restart|logs}"
            echo ""
            echo "  deploy  - 一键部署所有服务"
            echo "  https   - 申请 HTTPS 证书"
            echo "  renew   - 设置证书自动续期"
            echo "  stop    - 停止所有服务"
            echo "  restart - 重启所有服务"
            echo "  logs    - 查看日志"
            ;;
    esac
}

main "$@"
