FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html admin.html favicon.ico favicon-32x32.png apple-touch-icon.png robots.txt /app/

EXPOSE 80
