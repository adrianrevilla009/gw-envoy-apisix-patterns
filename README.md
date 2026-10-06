# gw-envoy-apisix-patterns

Five small gateway configurations, three for Envoy and two for Apache APISIX, that put authentication, scripting and rate limiting in front of a tiny Orders upstream.

## What is inside

| Folder | What it shows | Run |
| --- | --- | --- |
| [`envoy-ext-authz`](./envoy-ext-authz) | Envoy `ext_authz` calling a small Python auth service that allows or denies and injects `x-user` | `python3 check.py` |
| [`envoy-lua-filter`](./envoy-lua-filter) | Inline Lua filter that adds a request header, blocks `/blocked` and tags responses | `python3 check.py` |
| [`envoy-rate-limit`](./envoy-rate-limit) | Local token-bucket limit next to a global limit through the `ratelimit` service and Redis, plus a note on xDS vs static config | `python3 check.py` |
| [`apisix-plugins`](./apisix-plugins) | APISIX standalone route with `proxy-rewrite` and `limit-count` | `python3 check.py` |
| [`apisix-auth-plugins`](./apisix-auth-plugins) | APISIX `key-auth` with a consumer that carries its own `limit-count` quota | `python3 check.py` |

## Prerequisites

- Python 3 with PyYAML, for the offline `check.py` in every folder.
- Docker with the Compose plugin, to start the full stacks (Envoy v1.31.2, APISIX 3.10.0, `traefik/whoami` as the Orders upstream).
- `curl` for the requests shown in each folder.

## How to read it

Start with `envoy-ext-authz`, then `envoy-lua-filter` and `envoy-rate-limit`; the APISIX folders repeat the same ideas as YAML plugins. The `check.py` scripts only parse and cross-check the config; the Compose stacks were not started when these READMEs were written.
