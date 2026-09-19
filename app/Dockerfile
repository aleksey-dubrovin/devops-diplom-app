FROM nginx:alpine

# Копируем статическую страницу
COPY index.html /usr/share/nginx/html/index.html

# Порт по умолчанию
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1