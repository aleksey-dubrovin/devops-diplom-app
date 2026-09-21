FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY docs.html /usr/share/nginx/html/docs.html
COPY docs/ /usr/share/nginx/html/docs/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1