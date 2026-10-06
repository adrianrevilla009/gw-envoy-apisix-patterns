"""Offline verify: parse envoy.yaml/compose.yaml, check wiring, exercise the auth decision."""
import sys
import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, "auth")
from app import decide

env = yaml.safe_load(open("envoy.yaml"))
hcm = env["static_resources"]["listeners"][0]["filter_chains"][0]["filters"][0]["typed_config"]
names = [f["name"] for f in hcm["http_filters"]]
assert names == ["envoy.filters.http.ext_authz", "envoy.filters.http.router"], names  # router must be last
authz = hcm["http_filters"][0]["typed_config"]["http_service"]["server_uri"]["cluster"]
clusters = {c["name"] for c in env["static_resources"]["clusters"]}
assert {authz, "orders"} <= clusters
assert yaml.safe_load(open("compose.yaml"))["services"].keys() >= {"envoy", "auth", "orders"}
assert decide({"Authorization": "Bearer demo-token"}) == (200, {"x-user": "alice"})
assert decide({})[0] == 403
print("ok")
