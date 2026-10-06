# apisix-auth-plugins

Apache APISIX 3.10.0 in standalone mode, with a `key-auth` route and one consumer, `alice`, defined in `apisix.yaml`.

## Goal
Show APISIX authenticating callers by API key, where the key identifies a consumer and the consumer carries its own `limit-count` quota.

## Run it
```
python3 check.py
docker compose up -d
curl -i localhost:9080/orders/x
for i in 1 2 3 4; do curl -s -o /dev/null -w '%{http_code}\n' -H 'apikey: demo-key-alice' localhost:9080/orders/x; done
docker compose down
```
Expected from `check.py`: `ok`.
Expected from the stack: 401 without a key; with `demo-key-alice` three 200s, then 429 (3 requests per 60 s).

Not run end to end: only `check.py` was run. The APISIX container was not started, so the status codes above are what the config is written to produce.

## What it proves
- Route `orders` matches `/orders/*`, requires the `apikey` header via `key-auth`, and rewrites the path to `/*` with `proxy-rewrite`.
- Consumer `alice` owns the key `demo-key-alice` and a `limit-count` of 3 per 60 s, so the quota follows the caller rather than the route; `check.py` checks keys are unique and every consumer has a quota.
- The upstream reference `orders` resolves to `orders:80`.

## Trade-offs
- API keys are easy to issue and revoke and attach per-consumer plugins naturally.
- They are bearer secrets with no expiry or scopes; the key here is a public demo value, and real keys should not sit in a YAML file.
- `limit-count` has no `policy` set on the consumer, so it uses the plugin default and is not shared across nodes.

## When not to use it
- When you need user identity, scopes or short-lived credentials; use `jwt-auth` or `openid-connect`.
