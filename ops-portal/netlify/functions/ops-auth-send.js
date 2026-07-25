const nodemailer = require('nodemailer');
const {
  getSecret,
  normEmail,
  otpForEmail,
  createLoginLinkToken,
  portalCors,
  WINDOW_MS,
} = require('./lib/ops-auth');

const AUTH_EMAIL = process.env.NEXUS_EMAIL || 'bids.deedavisinc@gmail.com';
const AUTH_PASSWORD = process.env.NEXUS_EMAIL_PASSWORD;
const FROM_EMAIL = process.env.OPS_FROM_EMAIL || 'hr@deedavis.biz';
const PORTAL_ORIGIN = process.env.PORTAL_PUBLIC_URL || 'https://ops.deedavis.biz';
const OPS_API = (process.env.OPS_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');

function buildSignInEmail(email, otp, link) {
  const mins = Math.round(WINDOW_MS / 60000);
  return {
    subject: `Your NEXUS OPS sign-in code: ${otp}`,
    text: `NEXUS OPS — Workforce Portal — sign in

Hi,

Fastest option — tap the link:
${link}

Or enter this 6-digit code (valid about ${mins} minutes):
${otp}

If you request another email within that hour, it will be the SAME code.

Session policy: 15-minute idle logout · 12-hour maximum. This is not GATEWAY.

Questions? Call (248) 270-8490 NEXUS desk or email hr@deedavis.biz.

— Dee Davis Inc. NEXUS OPS
`,
    html: `
<div style="font-family:Inter,Helvetica,Arial,sans-serif;max-width:480px;color:#0B1E3D">
  <p style="font-size:14px;font-weight:700;letter-spacing:.08em;text-transform:uppercase">NEXUS OPS — Workforce Portal</p>
  <p style="font-size:15px;line-height:1.6"><b>Fastest:</b> tap the button below.</p>
  <p style="margin:20px 0">
    <a href="${link}" style="display:inline-block;background:#152238;color:#E8A87C;padding:14px 24px;text-decoration:none;font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase">Sign in to NEXUS OPS</a>
  </p>
  <p style="font-size:15px;line-height:1.6">Or enter this code (valid about ${mins} minutes):</p>
  <p style="font-size:32px;font-weight:800;letter-spacing:.25em;margin:16px 0">${otp}</p>
  <p style="font-size:12px;color:#6B7280;line-height:1.6">15-minute idle logout · 12-hour max session. Not the GATEWAY onboarding portal.</p>
  <p style="font-size:11px;color:#9CA3AF;margin-top:24px">Questions · (248) 270-8490 · hr@deedavis.biz</p>
</div>`,
  };
}

exports.handler = async (event) => {
  const origin = event.headers?.origin || event.headers?.Origin;
  const cors = portalCors(origin);

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: cors, body: '' };
  }
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const secret = getSecret();
  if (!secret) {
    return {
      statusCode: 503,
      headers: cors,
      body: JSON.stringify({ error: 'Sign-in unavailable. Call (248) 270-8490 NEXUS desk.' }),
    };
  }
  if (!AUTH_PASSWORD) {
    return {
      statusCode: 503,
      headers: cors,
      body: JSON.stringify({ error: 'Email service not configured. Call (248) 270-8490 NEXUS desk.' }),
    };
  }

  let body = {};
  try {
    body = JSON.parse(event.body || '{}');
  } catch {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const email = normEmail(body.email);
  if (!email) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Valid email required' }) };
  }

  // Must have an Active GATEWAY record before we send a code.
  // Use GATEWAY /self (live on PythonAnywhere). /ops/session is preferred after PA reload.
  try {
    const selfUrl = `${OPS_API}/nexus/hr/onboarding/self?email=${encodeURIComponent(email)}`;
    const selfCheck = await fetch(selfUrl, { headers: { Accept: 'application/json' } });
    if (selfCheck.status === 404) {
      return {
        statusCode: 404,
        headers: cors,
        body: JSON.stringify({
          error: 'No active GATEWAY record for that email. Complete onboarding at gateway.deedavis.biz or ask HR.',
        }),
      };
    }
    if (!selfCheck.ok) {
      console.warn('ops-auth-send self check status', selfCheck.status);
      return {
        statusCode: 502,
        headers: cors,
        body: JSON.stringify({ error: 'Could not verify workforce record. Try again shortly.' }),
      };
    }
  } catch (err) {
    console.error('ops-auth-send session check error:', err && err.message ? err.message : err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({
        error: 'Could not reach NEXUS. Try again or call (248) 270-8490.',
        detail: String(err && err.message ? err.message : err).slice(0, 120),
      }),
    };
  }

  const loginToken = createLoginLinkToken(email, secret);
  const otp = otpForEmail(email, secret);
  const link = `${PORTAL_ORIGIN.replace(/\/$/, '')}/?login=${encodeURIComponent(loginToken)}`;
  const mail = buildSignInEmail(email, otp, link);

  try {
    const transport = nodemailer.createTransport({
      service: 'gmail',
      auth: { user: AUTH_EMAIL, pass: AUTH_PASSWORD },
    });
    await transport.sendMail({
      from: `"DDI NEXUS OPS" <${AUTH_EMAIL}>`,
      replyTo: FROM_EMAIL !== AUTH_EMAIL ? FROM_EMAIL : undefined,
      to: email,
      subject: mail.subject,
      text: mail.text,
      html: mail.html,
      envelope: { from: AUTH_EMAIL, to: email },
    });
  } catch (err) {
    console.error('ops-auth-send email error:', err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ error: 'Could not send sign-in email. Try again in a minute.' }),
    };
  }

  return {
    statusCode: 200,
    headers: cors,
    body: JSON.stringify({
      ok: true,
      email,
      message: 'Sign-in link and code sent. Check inbox (and spam).',
      expires_minutes: Math.round(WINDOW_MS / 60000),
    }),
  };
};
