# DDI Portal Domains — deedavis.biz

**Locked:** July 25, 2026  
**Owner:** Dee Davis Inc.

Two workforce portals + existing NEXUS/client portals. **Separate Netlify sites. Separate auth secrets. Same Flask backend (PythonAnywhere).**

---

## Domain map

| Subdomain | Product | Audience | Repo folder | Netlify site name (suggested) |
|---|---|---|---|---|
| **gateway.deedavis.biz** | GATEWAY | New hires / contractors (onboarding) | `gateway-portal/` | `ddi-gateway-portal` |
| **ops.deedavis.biz** | NEXUS OPS | Cleared employees (daily work desks) | `ops-portal/` | `ddi-ops-portal` |
| nexus.deedavis.biz | NEXUS Command Center | Dieasha / internal admin | `nexus-frontend/` | (existing) |
| portal.deedavis.biz | PRISM client intake | External clients | `prism-intake/` | (existing) |

```
gateway.deedavis.biz  →  hire / clear / e-sign / training
ops.deedavis.biz      →  work (PRISM desk first, Claims later)
nexus.deedavis.biz    →  your cockpit
```

---

## DNS (add at deedavis.biz DNS host)

After each Netlify site is created and shows its `*.netlify.app` hostname:

| Type | Host | Value | Portal |
|---|---|---|---|
| **CNAME** | `gateway` | `ddi-gateway-portal.netlify.app` | GATEWAY |
| **CNAME** | `ops` | `ddi-ops-portal.netlify.app` | NEXUS OPS |

Use the **exact** Netlify hostname Netlify shows if it differs from the suggestion.

Verify:
```bash
dig +short gateway.deedavis.biz CNAME
dig +short ops.deedavis.biz CNAME
curl -I https://gateway.deedavis.biz
curl -I https://ops.deedavis.biz
```

SSL: Let’s Encrypt auto-provisions on Netlify once DNS resolves.

---

## Create checklist

### A — gateway.deedavis.biz (onboarding)

- [x] Netlify site `ddi-gateway-portal` (base directory `gateway-portal`)
- [x] Custom domain `gateway.deedavis.biz` added
- [ ] Confirm CNAME `gateway` → `ddi-gateway-portal.netlify.app` at DNS host (if not already)
- [ ] Env vars set per `gateway-portal/PORTAL_DOMAIN_SETUP.md`
  - Especially: `GATEWAY_AUTH_SECRET`, `PORTAL_PUBLIC_URL=https://gateway.deedavis.biz`, `GATEWAY_FROM_EMAIL=hr@deedavis.biz`
- [ ] Deploy + smoke test magic-link login

### B — ops.deedavis.biz (work)

- [x] Netlify site `ddi-ops-portal` created + linked to `ops-portal/` (Project ID `bf8225a6-816b-44b0-a5c4-cd44cad3949c`)
- [x] Custom domain `ops.deedavis.biz` added on the Netlify site
- [ ] **DNS:** CNAME `ops` → `ddi-ops-portal.netlify.app` (required for SSL + custom URL)
- [x] Env vars: `OPS_AUTH_SECRET`, `OPS_API_BASE`, `PORTAL_PUBLIC_URL`, `OPS_FROM_EMAIL`, `NEXUS_EMAIL`, `NEXUS_EMAIL_PASSWORD`
- [x] Shell deployed (live on `https://ddi-ops-portal.netlify.app` until DNS propagates)
- [ ] Full OTP login + PRISM Desk = Phase A/B build

---

## Auth separation (non-negotiable)

| Portal | Secret env | Session policy |
|---|---|---|
| GATEWAY | `GATEWAY_AUTH_SECRET` | Longer session OK (onboarding) |
| OPS | `OPS_AUTH_SECRET` | **15-min idle · 12-hr absolute max** |

A GATEWAY JWT must **never** open OPS, and vice versa.

---

## Backend

Both portals call `https://deedavis.pythonanywhere.com` (same Flask app):

- GATEWAY → `/nexus/hr/onboarding/*`
- OPS → `/ops/*` (Phase A+) and PRISM façades as built

---

## Docs

- GATEWAY setup detail: `gateway-portal/PORTAL_DOMAIN_SETUP.md`
- OPS setup detail: `ops-portal/PORTAL_DOMAIN_SETUP.md`
- OPS product architecture: `NEXUS_OPS_MASTER.md`
