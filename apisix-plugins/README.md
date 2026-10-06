# apisix-plugins

Apache APISIX 3.10.0 in standalone mode, with one route in `apisix.yaml` that uses the `proxy-rewrite` and `limit-count` plugins.

## Goal
Show two plugins on a single route in file-driven mode: a path rewrite with an extra header, and a per-client request quota.

## Run it
```
python3 check.py
docker compose up -d
for i in $(seq 7); do curl -s -o /dev/null -w '%{http_code}\n' localhost:9080/v2/orders/42; done
docker compose down
```
Expected from `check.py`: `ok`.
Expected from the stack: five 200s, then 429 for the next two requests.

Not run end to end: only `check.py` was run. The APISIX container was not started, so the status codes above are what the config is written to produce.

## What it proves
- Route `orders-v2` matches `/v2/orders/*` and points at upstream `orders` (`orders:80`); `check.py` confirms the reference resolves.
- `proxy-rewrite` turns `/v2/orders/42` into `/42` (the regex is tested in `check.py`) and sets `X-Gateway: apisix`.
- `limit-count` allows 5 requests per 60 s keyed on `remote_addr`, rejecting with 429.

## Trade-offs
- Standalone YAML needs no etcd and is easy to review in git, but there is no Admin API.
- `policy: local` counts per APISIX node; a shared limit across replicas needs the Redis policy.
- `apisix.yaml` must end with the `#END` marker, which looks like a comment but is required.

## When not to use it
- When routes change often at runtime; use etcd mode with the Admin API.
- When a plain reverse proxy already covers the need.
