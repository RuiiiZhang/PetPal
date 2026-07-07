FROM nginx:1.25-alpine

RUN rm /etc/nginx/conf.d/default.conf
RUN mkdir -p /etc/nginx/conf.d /var/lib/letsencrypt

# 安装 certbot（用于 HTTPS 证书）
RUN apk add --no-cache certbot certbot-nginx

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
