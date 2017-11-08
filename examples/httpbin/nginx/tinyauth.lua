local cjson = require "cjson"
local http = require "resty.http"

local ngx = ngx

local _M = {
    _VERSION = '0.1',
}
local mt = { __index = _M }


local function get_header_list()
    local headers = {}
    local i = 1
    for k, v in pairs(ngx.req.get_headers(raw)) do
        headers[i] = {k, v}
        i = i + 1
    end
    return headers
end


local function get_resource_urn()
    return "urn:::" .. ngx.var.uri
end


local function req_matches_method(methods)
  for idx, method in pairs(methods) do
    if method == ngx.req.get_method() then
      return true
    end
  end
  return false
end


local function req_matches_uri(uri)
  return ngx.re.match(ngx.var.uri, uri, "jo")
end


function _M.new(self, endpoint, user, pass)
    return setmetatable({
        endpoint = endpoint,
        user = user,
        pass = pass,
        client = http.new(),
    }, mt)
end


function _M.authorize_for_url(self, default_action, matches)
  for k, v in pairs(matches) do
    if req_matches_uri(v[1]) and req_matches_method(v[2]) then
      return _M.authorize_for_action(self, v[3])
    end
  end

  return _M.authorize_for_action(self, default_action)
end


function _M.authorize_for_action(self, action)
    local client = self.client

    local body = cjson.encode({
        action = action,
        resource = get_resource_urn(),
        headers = get_header_list(),
        context = {
            SourceIP = ngx.var.remote_addr
        }
    })

    ngx.log(ngx.DEBUG, "REQUEST: " .. body)

    local res, err = client:request_uri(self.endpoint .. "authorize", {
        method = "POST",
        body = body,
        headers = {
            ["Content-Type"] = "application/json",
            Authorization = 'Basic '..ngx.encode_base64(self.user .. ':' .. self.pass)
        }
    })

    if not res then
        ngx.log(ngx.ERR, err)
        ngx.exit(ngx.HTTP_FORBIDDEN)
        return
    end

    ngx.log(ngx.DEBUG, "RESPONSE: " .. res.body)

    local auth = cjson.decode(res.body)

    if not auth['Authorized'] then
        ngx.exit(ngx.HTTP_FORBIDDEN)
        return
    end

    if auth['Identity'] then
        ngx.req.set_header('X-User', auth['Identity'])
    end
end


return _M
