local remote_addr = ngx.var.remote_addr
local uri = ngx.var.uri

if not remote_addr or not string.match(remote_addr, "172.25.0.1") then
  ngx.exit(ngx.HTTP_FORBIDDEN)
end
