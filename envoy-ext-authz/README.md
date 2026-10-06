# envoy-ext-authz

Envoy v1.31.2 with the `ext_authz` HTTP filter calling a tiny Python auth service (`auth/app.py`), in front of a `traefik/whoami` upstream.

## Goal
Show Envoy delegating every request to an external service that allows or denies it and injects an `x-user` header for the upstream.

## Run it
```
python3 check.py
docker compose up -d
curl -i localhost:8080/
curl -i -H 'Authorization: Bearer demo-token' localhost:8080/
docker compose down
```
Expected from `check.py`: `ok`.
Expected from the stack: 403 without a token; 200 with `Bearer demo-token`, and the echoed request shows `X-User: alice`.

Not run end to end: only `check.py` was run. The Compose stack and the curl calls were not executed, so the outputs above are what the config is written to produce. Optional config validation: `docker run --rm -v $PWD/envoy.yaml:/e.yaml envoyproxy/envoy:v1.31.2 --mode validate -c /e.yaml`.

## What it proves
- `envoy.yaml` puts `ext_authz` before `router`, and `check.py` asserts that order and that the `auth` and `orders` clusters exist.
- `failure_mode_allow: false` makes Envoy fail closed, with a 0.5 s timeout on the auth call.
- `decide()` in `auth/app.py` returns 200 plus `x-user: alice` for `Bearer demo-token` and 403 for anything else; `check.py` asserts both.

## Trade-offs
- HTTP mode is the simplest to write; gRPC mode is faster and can modify more of the request.
- Every request pays an extra network hop to the auth service, bounded only by the timeout.
- The token table in `auth/app.py` is hard-coded demo data.

## When not to use it
- When auth is only JWT validation: the built-in `jwt_authn` filter needs no extra service.
- When the latency budget cannot afford a per-request call.
