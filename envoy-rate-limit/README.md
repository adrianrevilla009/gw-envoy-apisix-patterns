# envoy-rate-limit

Envoy v1.31.2 with a local rate limit and a global rate limit (`envoyproxy/ratelimit` backed by Redis 7.4.1) on one route, plus a note on xDS.

## Goal
Contrast the in-process local limit (10 requests per second per Envoy) with the shared global limit (5 requests per minute per `x-client-id`).

## Run it
```
python3 check.py
docker compose up -d
for i in $(seq 8); do curl -s -o /dev/null -w '%{http_code}\n' -H 'x-client-id: a' localhost:8080/; done
docker compose down
```
Expected from `check.py`: `ok`.
Expected from the stack: five 200s, then 429 for the remaining requests in that minute.

Not run end to end: only `check.py` was run. The Compose stack, Redis and the ratelimit service were not started, so the status codes above are what the config is written to produce.

## What it proves
- `envoy.yaml` sets a token bucket of 10 tokens refilled every 1 s in `local_ratelimit`, with no external dependency.
- The route descriptor key `client` (from the `x-client-id` header) matches `ratelimit/config/config.yaml`, and both use the domain `orders`; `check.py` asserts this.
- The `ratelimit` cluster is configured for HTTP/2, which gRPC needs, and the rate-limit filter sits before `router`.

## Trade-offs
- The local limit is cheap, but every Envoy replica counts separately, so the real limit is N times higher.
- The global limit is exact across replicas but adds a gRPC hop and a Redis dependency; `failure_mode_deny: false` means requests pass if the service is down.
- This lab uses static config, read once at startup and easy to diff. xDS (LDS, CDS, RDS, EDS from a control plane) changes routes and endpoints at runtime without restarts but needs a management server, which is too much for a handful of routes.

## When not to use it
- When a single gateway instance is enough, the local limit alone does the job.
- For quotas per plan or billing period; use a metering system instead.
