"""Offline verify: standalone APISIX config parses, references resolve, and the rewrite regex does what the README says."""
import re
import yaml

# apisix.yaml ends with a '#END' marker that APISIX requires; it is a YAML comment.
cfg = yaml.safe_load(open("apisix.yaml"))
assert open("apisix.yaml").read().rstrip().endswith("#END")
route = cfg["routes"][0]
assert route["upstream_id"] in {u["id"] for u in cfg["upstreams"]}
assert {"proxy-rewrite", "limit-count"} <= route["plugins"].keys()
pattern, template = route["plugins"]["proxy-rewrite"]["regex_uri"]
assert re.sub(pattern, template.replace("$1", r"\1"), "/v2/orders/42") == "/42"
assert route["plugins"]["limit-count"]["count"] > 0
assert yaml.safe_load(open("config.yaml"))["deployment"]["role_data_plane"]["config_provider"] == "yaml"
assert yaml.safe_load(open("compose.yaml"))["services"].keys() >= {"apisix", "orders"}
print("ok")
