FROM alpine:3.6
RUN apk --no-cache add nginx openssl
RUN mkdir -p /etc/nginx/external
ADD nginx.conf /etc/nginx/nginx.conf
ADD entrypoint.sh /docker-entrypoint
ENTRYPOINT ["/docker-entrypoint"]
CMD ["nginx"]
