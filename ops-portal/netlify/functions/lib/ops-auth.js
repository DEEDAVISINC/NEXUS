/**
 * NEXUS OPS auth — HMAC JWT with sliding idle + absolute max session.
 * Uses OPS_AUTH_SECRET only (never GATEWAY_AUTH_SECRET).
 *
 * Sliding JWT TTL = 15 minutes (refreshed on authenticated calls).
 * Absolute max = 12 hours from session start (sst claim).
 */
const crypto = require('crypto');

const WINDOW_MS = 60 * 60 * 1000; // OTP window 60 min
const OTP_ACCEPT_WINDOWS = 2;
const IDLE_TTL_SEC = 15 * 60;
const ABSOLUTE_TTL_SEC = 12 * 60 * 60;
const WARN_BEFORE_IDLE_SEC = 2 * 60;

function getSecret() {
  return (process.env.OPS_AUTH_SECRET || '').trim();
}

function b64url(buf) {
  return Buffer.from(buf)
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function b64urlJson(obj) {
  return b64url(JSON.stringify(obj));
}

function signJwt(payload, secret, ttlSec) {
  const header = b64urlJson({ alg: 'HS256', typ: 'JWT' });
  const now = Math.floor(Date.now() / 1000);
  const body = { ...payload, iat: now, exp: now + ttlSec };
  const bodyEnc = b64urlJson(body);
  const sig = crypto.createHmac('sha256', secret).update(`${header}.${bodyEnc}`).digest();
  return `${header}.${bodyEnc}.${b64url(sig)}`;
}

function verifyJwt(token, secret, expectedPurpose) {
  if (!token || !secret) return null;
  const parts = String(token).split('.');
  if (parts.length !== 3) return null;
  const [header, body, sig] = parts;
  const expected = b64url(
    crypto.createHmac('sha256', secret).update(`${header}.${body}`).digest()
  );
  if (sig !== expected) return null;
  let payload;
  try {
    payload = JSON.parse(Buffer.from(body.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString());
  } catch {
    return null;
  }
  const now = Math.floor(Date.now() / 1000);
  if (!payload.exp || payload.exp < now) return null;
  if (expectedPurpose && payload.purpose !== expectedPurpose) return null;
  return payload;
}

function normEmail(v) {
  const s = (v || '').trim().toLowerCase();
  return s && s.includes('@') ? s : '';
}

function timeWindow(ts = Date.now()) {
  return Math.floor(ts / WINDOW_MS);
}

function otpForEmail(email, secret, windowOffset = 0) {
  const w = timeWindow() + windowOffset;
  const hmac = crypto.createHmac('sha256', secret).update(`ops-otp:${email}:${w}`).digest('hex');
  return String(parseInt(hmac.slice(0, 8), 16) % 1000000).padStart(6, '0');
}

function verifyOtp(email, code, secret) {
  const c = String(code || '').replace(/\D/g, '');
  if (c.length !== 6) return false;
  for (let off = 0; off < OTP_ACCEPT_WINDOWS; off++) {
    if (otpForEmail(email, secret, -off) === c) return true;
  }
  return false;
}

function createLoginLinkToken(email, secret) {
  const otp = otpForEmail(email, secret, 0);
  return signJwt({ purpose: 'ops-login', email, otp }, secret, Math.floor(WINDOW_MS / 1000));
}

function verifyLoginLinkToken(token, secret) {
  const p = verifyJwt(token, secret, 'ops-login');
  if (!p || !p.email) return null;
  return normEmail(p.email);
}

function createSessionToken(email, secret, sessionStarted) {
  const now = Math.floor(Date.now() / 1000);
  const sst = sessionStarted || now;
  if (now - sst >= ABSOLUTE_TTL_SEC) return null;
  return signJwt(
    { purpose: 'ops-session', email: normEmail(email), sst },
    secret,
    IDLE_TTL_SEC
  );
}

function verifySessionToken(token, secret) {
  const p = verifyJwt(token, secret, 'ops-session');
  if (!p || !p.email) return null;
  const now = Math.floor(Date.now() / 1000);
  const sst = p.sst || p.iat;
  if (!sst || now - sst >= ABSOLUTE_TTL_SEC) return null;
  return { email: normEmail(p.email), sst, exp: p.exp };
}

function refreshSessionToken(token, secret) {
  const sess = verifySessionToken(token, secret);
  if (!sess) return null;
  const next = createSessionToken(sess.email, secret, sess.sst);
  if (!next) return null;
  return { email: sess.email, sst: sess.sst, session: next };
}

function sessionFromEvent(event) {
  const secret = getSecret();
  if (!secret) return null;
  const auth = event.headers?.authorization || event.headers?.Authorization || '';
  const bearer = auth.startsWith('Bearer ') ? auth.slice(7).trim() : '';
  return verifySessionToken(bearer, secret);
}

function portalCors(origin) {
  const allowed = [
    'https://ops.deedavis.biz',
    'https://ddi-ops-portal.netlify.app',
  ];
  const req = origin || '';
  let allow = 'https://ops.deedavis.biz';
  if (allowed.includes(req) || /--ddi-ops-portal\.netlify\.app$/.test(req)) {
    allow = req;
  }
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Headers': 'Content-Type, Accept, Authorization, X-Ops-Email',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
  };
}

module.exports = {
  getSecret,
  normEmail,
  otpForEmail,
  verifyOtp,
  createLoginLinkToken,
  verifyLoginLinkToken,
  createSessionToken,
  verifySessionToken,
  refreshSessionToken,
  sessionFromEvent,
  portalCors,
  WINDOW_MS,
  IDLE_TTL_SEC,
  ABSOLUTE_TTL_SEC,
  WARN_BEFORE_IDLE_SEC,
};
