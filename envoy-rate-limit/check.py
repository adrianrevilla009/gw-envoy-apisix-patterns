"""Offline verify: both limiters are wired, descriptor keys match, and the local bucket arithmetic holds."""
import yaml

env = yaml.safe_load(open("envoy.yaml"))
hcm = env["static_resources"]["listeners"][0]["filter_chains"][0]["filters"][0]["typed_config"]
filters = {f["name"]: f["typed_config"] for f in hcm["http_filters"]}
assert list(filters)[-1] == "envoy.filters.http.router"
local = filters["envoy.filters.http.local_ratelimit"]["token_bucket"]
assert local["tokens_per_fill"] <= local["max_tokens"]
glob = filters["envoy.filters.http.ratelimit"]
cfg = yaml.safe_load(open("ratelimit/config/config.yaml"))
assert glob["domain"] == cfg["domain"]
action = hcm["route_config"]["virtual_hosts"][0]["routes"][0]["route"]["rate_limits"][0]["actions"][0]
assert action["request_headers"]["descriptor_key"] == cfg["descriptors"][0]["key"]
cluster = glob["rate_limit_service"]["grpc_service"]["envoy_grpc"]["cluster_name"]
assert cluster in {c["name"] for c in env["static_resources"]["clusters"]}
assert yaml.safe_load(open("compose.yaml"))["services"].keys() >= {"envoy", "ratelimit", "redis", "orders"}
print("ok")
