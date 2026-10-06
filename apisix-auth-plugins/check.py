"""Offline verify: key-auth route has a consumer with a key, consumer keys are unique, references resolve."""
import yaml

raw = open("apisix.yaml").read()
assert raw.rstrip().endswith("#END")
cfg = yaml.safe_load(raw)
route = cfg["routes"][0]
assert "key-auth" in route["plugins"]
assert route["upstream_id"] in {u["id"] for u in cfg["upstreams"]}
keys = [c["plugins"]["key-auth"]["key"] for c in cfg["consumers"]]
assert keys and len(keys) == len(set(keys))
assert all(c["plugins"].get("limit-count") for c in cfg["consumers"])  # per-consumer quota
assert yaml.safe_load(open("compose.yaml"))["services"].keys() >= {"apisix", "orders"}
print("ok")
