local cjson = require "cjson"
local http = require "resty.http"

local headers = {}
local i = 1
for k, v in pairs(ngx.req.get_headers(raw)) do
  headers[i] = {k, v}
  i = i + 1
end

local body = {
    action = "HttpReverseProxy",
    resource = "urn:::" .. ngx.var.uri,
    headers = headers,
    context = {
        SourceIP = ngx.var.remote_addr
    }
}

ngx.log(ngx.ERR, cjson.encode(body))

local httpc = http.new()
local res, err = httpc:request_uri("http://microauth:5000/api/v1/authorize", {
    method = "POST",
    body = cjson.encode(body),
    headers = {
        ["Content-Type"] = "application/json",
        Authorization = "Basic Z2F0ZWtlZXBlcjprZXltYXN0ZXI="
    }
})

if not res then
  ngx.log(ngx.ERR, err) 
  ngx.exit(ngx.HTTP_FORBIDDEN)
end

local auth = cjson.decode(res.body)
ngx.log(ngx.ERR, res.body) 
if not auth['Authorized'] then
  ngx.exit(ngx.HTTP_FORBIDDEN)
end

ngx.req.set_header('X-User', 'gatekeeper')
