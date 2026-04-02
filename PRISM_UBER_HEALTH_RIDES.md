# PRISM — Uber Health Rides API

**Status:** Integrated in NEXUS (`prism_uber_health.py`)  
**Owner:** Dee Davis Inc.  
**Purpose:** NEMT and coordinated ride flows — OAuth, trip estimates, sandbox simulation, future wiring to PRISM orders.

## Source artifacts

| Item | Location |
|------|----------|
| OpenAPI 3.1 spec | `ESSENTIALS/uber_health_rides_openapi.json` |
| Python module + routes | `prism_uber_health.py` |

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `UBER_HEALTH_CLIENT_ID` | Yes | Uber developer app client ID |
| `UBER_HEALTH_CLIENT_SECRET` | Yes | Uber developer app client secret |
| `UBER_HEALTH_ORG_ID` | Yes* | U4B organization UUID → `x-uber-organizationuuid` on API calls (*required when Uber expects org header) |
| `UBER_HEALTH_TOKEN_URL` | No | Default `https://login.uber.com/oauth/v2/token` |

**Legacy aliases** (still read if present): `UBER_CLIENT_ID`, `UBER_CLIENT_SECRET`, `UBER_ORG_UUID`, `UBER_TOKEN_URL`.

## Lyft (future PRISM transport)

| Variable | Description |
|----------|-------------|
| `LYFT_ORG_ID` | Organization / business identifier (e.g. business profile slug) |
| `LYFT_CLIENT_ID` | Lyft API client id when issued |
| `LYFT_CLIENT_SECRET` | Lyft API client secret when issued |

Helpers: `prism_transport_env.py` → `get_lyft_env()`, `lyft_configured_for_api()`. No HTTP routes until Lyft is integrated.

## OAuth (client credentials)

- **Grant:** `client_credentials`  
- **Scope:** `health`  
- Response includes `access_token`, `token_type` Bearer, `expires_in` (often ~30 days).  
- The client caches the token and refreshes before expiry.

## NEXUS HTTP routes (after `api_server` loads the blueprint)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/prism/uber-health/status` | Credentials configured, token cache state (no secrets) |
| POST | `/prism/uber-health/sandbox/run` | Create sandbox run; empty body uses default SF coordinates from the spec |
| POST | `/prism/uber-health/trips/estimates` | Proxy to production **Create Health Trip Estimates**; JSON must use `pickup` / `dropoff` per OpenAPI |

## Request shape notes

- **Sandbox run** (`SandboxRunRequest`): `driver_locations`, `pickup_location`, `dropoff_location`, `parent_product_type_id`, optional `preferences.auto_accept_trip`.  
- **Trip estimates** (`OnDemandEstimateRequest`): `pickup` and `dropoff` coordinates — not `pickup_location` / `dropoff_location`.

## Sandbox defaults (San Francisco)

Recommended test coordinates from Uber’s documentation are encoded in `prism_uber_health.py` as `SANDBOX_SF_PICKUP`, `SANDBOX_SF_DROPOFF`, and `default_sandbox_run_body()`.

## Security

- Do not commit client secrets or live bearer tokens.  
- Treat access tokens like passwords; rotate client secret if a token is exposed.

## Next steps (PRISM product work)

- Map PRISM `nemt` / `transport` orders to guest + trip create/update/cancel.  
- Ingest **webhooks** (`health.status_changed`, `health.receipt_ready`, etc.) via a dedicated NEXUS URL + verification.  
- Store `run_id` / `request_id` on sandbox test orders for QA.
