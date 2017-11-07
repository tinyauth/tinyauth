FROM openresty/openresty:alpine AS builder
RUN apk --no-cache add curl perl
RUN /usr/local/openresty/bin/opm get pintsized/lua-resty-http


FROM openresty/openresty:alpine
COPY --from=builder /usr/local/openresty/site /usr/local/openresty/site
COPY nginx.conf /etc/nginx/nginx.conf
COPY httpbin_auth.lua /etc/nginx/httpbin_auth.lua

CMD ["nginx", "-c", "/etc/nginx/nginx.conf"]
