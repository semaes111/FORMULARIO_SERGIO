FROM nginx:alpine

# Remove default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy our files
COPY index.html /usr/share/nginx/html/index.html
COPY admin.html /usr/share/nginx/html/admin.html

# Custom nginx config for SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
