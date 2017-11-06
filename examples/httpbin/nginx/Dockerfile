FROM openresty/openresty:alpine

COPY nginx.conf /etc/nginx/nginx.conf
COPY httpbin_auth.lua /etc/nginx/httpbin_auth.lua

CMD ["nginx", "-c", "/etc/nginx/nginx.conf"]
