"""Offline verify: parse envoy.yaml, check filter order and the Lua hooks (Lua itself is not executed)."""
import yaml

env = yaml.safe_load(open("envoy.yaml"))
hcm = env["static_resources"]["listeners"][0]["filter_chains"][0]["filters"][0]["typed_config"]
filters = hcm["http_filters"]
assert [f["name"] for f in filters] == ["envoy.filters.http.lua", "envoy.filters.http.router"]
lua = filters[0]["typed_config"]["default_source_code"]["inline_string"]
for hook in ("function envoy_on_request(handle)", "function envoy_on_response(handle)"):
    assert hook in lua, hook
assert lua.count("function ") == 2
route = hcm["route_config"]["virtual_hosts"][0]["routes"][0]["route"]["cluster"]
assert route in {c["name"] for c in env["static_resources"]["clusters"]}
print("ok")
