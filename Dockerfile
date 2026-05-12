FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /app/index.html
COPY admin.html /app/admin.html

# Static assets — favicon, apple-touch-icon (varias resoluciones) y robots.txt
COPY favicon.ico                              /app/favicon.ico
COPY favicon-32x32.png                        /app/favicon-32x32.png
COPY apple-touch-icon.png                     /app/apple-touch-icon.png
COPY apple-touch-icon-precomposed.png         /app/apple-touch-icon-precomposed.png
COPY apple-touch-icon-120x120.png             /app/apple-touch-icon-120x120.png
COPY apple-touch-icon-120x120-precomposed.png /app/apple-touch-icon-120x120-precomposed.png
COPY robots.txt                               /app/robots.txt

EXPOSE 80
