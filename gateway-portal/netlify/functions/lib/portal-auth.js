/**
 * GATEWAY portal auth — HMAC JWT sessions + time-window OTP (no database).
 * Same email gets the same 6-digit code for 15 minutes; magic link works in that window.
 * (Adapted from prism-intake/netlify/functions/lib/portal-auth.js — same pattern,
 * separate CORS allow-list for gateway.deedavis.biz.)
 */
const crypto = require('crypto');

const WINDOW_MS = 15 * 60 * 1000;
const SESSION_DAYS = 30;

function getSecret() {
  const s = process.env.GATEWAY_AUTH_SECRET || process.env.PORTAL_AUTH_SECRET || process.env.NEXUS_EMAIL_PASSWORD || '';
  return s.trim();
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
  const body = {
    ...payload,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + ttlSec,
  };
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
  if (!payload.exp || payload.exp < Math.floor(Date.now() / 1000)) return null;
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
  const hmac = crypto.createHmac('sha256', secret).update(`gateway-otp:${email}:${w}`).digest('hex');
  return String(parseInt(hmac.slice(0, 8), 16) % 1000000).padStart(6, '0');
}

function verifyOtp(email, code, secret) {
  const c = String(code || '').replace(/\D/g, '');
  if (c.length !== 6) return false;
  return (
    otpForEmail(email, secret, 0) === c ||
    otpForEmail(email, secret, -1) === c
  );
}

function createLoginLinkToken(email, secret) {
  return signJwt(
    { purpose: 'login', email, win: timeWindow() },
    secret,
    Math.floor(WINDOW_MS / 1000)
  );
}

function verifyLoginLinkToken(token, secret) {
  const p = verifyJwt(token, secret, 'login');
  if (!p || !p.email) return null;
  const win = p.win;
  const now = timeWindow();
  if (win !== now && win !== now - 1) return null;
  return normEmail(p.email);
}

function createSessionToken(email, secret) {
  return signJwt({ purpose: 'session', email: normEmail(email) }, secret, SESSION_DAYS * 86400);
}

function verifySessionToken(token, secret) {
  const p = verifyJwt(token, secret, 'session');
  if (!p || !p.email) return null;
  return normEmail(p.email);
}

function sessionFromEvent(event) {
  const secret = getSecret();
  if (!secret) return null;
  const auth = event.headers?.authorization || event.headers?.Authorization || '';
  const bearer = auth.startsWith('Bearer ') ? auth.slice(7).trim() : '';
  const headerEmail = (event.headers?.['x-gateway-email'] || event.headers?.['X-Gateway-Email'] || '').trim().toLowerCase();
  const email = verifySessionToken(bearer, secret);
  if (!email) return null;
  if (headerEmail && headerEmail !== email) return null;
  return email;
}

function portalCors(origin) {
  const allowed = [
    'https://gateway.deedavis.biz',
    'https://ddi-gateway-portal.netlify.app',
  ];
  const req = origin || '';
  let allow = 'https://gateway.deedavis.biz';
  if (allowed.includes(req) || req.endsWith('--ddi-gateway-portal.netlify.app')) {
    allow = req;
  }
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Headers': 'Content-Type, Accept, Authorization, X-Gateway-Email',
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
  sessionFromEvent,
  portalCors,
  WINDOW_MS,
  SESSION_DAYS,
};
