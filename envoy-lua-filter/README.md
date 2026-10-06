# envoy-lua-filter

Envoy v1.31.2 with an inline Lua HTTP filter in `envoy.yaml`, in front of a `traefik/whoami` upstream.

## Goal
Show a Lua filter that adds a request header, short-circuits `/blocked` with a 403 and tags every response, without recompiling Envoy.

## Run it
```
python3 check.py
docker compose up -d
curl -i localhost:8080/blocked
curl -i localhost:8080/
docker compose down
```
Expected from `check.py`: `ok`.
Expected from the stack: `/blocked` returns 403 with body `blocked by lua`; `/` returns the upstream echo containing `X-Orders-Tenant: demo` and a response header `x-served-by: envoy-lua`.

Not run end to end: only `check.py` was run. The Compose stack was not started, and `check.py` does not execute the Lua, it only checks that the hooks exist. Optional validation: `docker run --rm -v $PWD/envoy.yaml:/e.yaml envoyproxy/envoy:v1.31.2 --mode validate -c /e.yaml`.

## What it proves
- The Lua filter is listed before `router` and defines exactly two functions, `envoy_on_request` and `envoy_on_response`.
- On request the script adds `x-orders-tenant: demo`, answers `/blocked` itself with 403, and logs the `x-request-id`.
- On response it adds `x-served-by: envoy-lua`.

## Trade-offs
- Quickest way to prototype a header or routing tweak; the script lives next to the route config.
- Lua is untyped and hard to unit test, and it runs on the worker thread, so blocking work hurts latency.
- The path check is an exact match on `/blocked`; query strings would not be matched by it.

## When not to use it
- For stateful or heavy work such as auth calls, rate limiting or large body transformation; use `ext_authz`, a rate-limit filter or a Wasm filter.
