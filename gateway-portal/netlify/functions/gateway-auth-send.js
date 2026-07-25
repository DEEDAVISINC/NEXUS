const nodemailer = require('nodemailer');
const {
  getSecret,
  normEmail,
  otpForEmail,
  createLoginLinkToken,
  portalCors,
  WINDOW_MS,
} = require('./lib/portal-auth');

// AUTH_EMAIL is the real Gmail account that authenticates to Gmail's SMTP relay.
// FROM_EMAIL is what recipients see in the From: header — hr@deedavis.biz once
// it's added + verified as a "Send mail as" alias on the AUTH_EMAIL account
// (Gmail Settings -> Accounts and Import -> Send mail as -> Add another email
// address). Until that alias is verified, Gmail silently sends as AUTH_EMAIL
// regardless of what FROM_EMAIL says, so this is safe to set early.
const AUTH_EMAIL = process.env.NEXUS_EMAIL || 'bids.deedavisinc@gmail.com';
const AUTH_PASSWORD = process.env.NEXUS_EMAIL_PASSWORD;
const FROM_EMAIL = process.env.GATEWAY_FROM_EMAIL || AUTH_EMAIL;
const EMAIL_PASSWORD = AUTH_PASSWORD; // back-compat with the config-check below
const PORTAL_ORIGIN = process.env.PORTAL_PUBLIC_URL || 'https://gateway.deedavis.biz';

function cleanNamePart(value) {
  return String(value || '')
    .replace(/[\u0000-\u001f<>&"'`]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 60);
}

function buildSignInEmail(email, otp, link, firstName, lastName) {
  const mins = Math.round(WINDOW_MS / 60000);
  const first = cleanNamePart(firstName);
  const last = cleanNamePart(lastName);
  const fullName = [first, last].filter(Boolean).join(' ');
  const greeting = first ? `Hi ${first},` : 'Hi,';
  const greetingHtml = first
    ? `<p style="font-size:15px;line-height:1.6">Hi <b>${first}</b>,</p>`
    : '';
  const nameLine = fullName
    ? `\nThis sign-in was requested for ${fullName}.\n`
    : '';
  const nameLineHtml = fullName
    ? `<p style="font-size:12px;color:#6B6458;line-height:1.6">Requested for <b>${fullName}</b>.</p>`
    : '';

  return {
    subject: first
      ? `${first}, your DDI GATEWAY sign-in code: ${otp}`
      : `Your DDI GATEWAY sign-in code: ${otp}`,
    text: `DDI GATEWAY — Onboarding Portal — sign in

${greeting}
${nameLine}
Fastest option — tap the link (no typing):
${link}

Or enter this 6-digit code on the sign-in page (valid about ${mins} minutes):
${otp}

If you request another email within that hour, it will be the SAME code — you do not need to wait for a different one.

If you did not request this, ignore this email.

Questions? Call (248) 270-8490 NEXUS desk or email hr@deedavis.biz.

— Dee Davis Inc. GATEWAY Onboarding Portal
`,
    html: `
<div style="font-family:Montserrat,Inter,sans-serif;max-width:480px;color:#0B1E3D">
  <p style="font-size:14px;font-weight:700;letter-spacing:.08em;text-transform:uppercase">DDI GATEWAY — Onboarding Portal</p>
  ${greetingHtml}
  ${nameLineHtml}
  <p style="font-size:15px;line-height:1.6"><b>Fastest:</b> tap the button below (no typing).</p>
  <p style="margin:20px 0">
    <a href="${link}" style="display:inline-block;background:#0B1E3D;color:#2DD4BF;padding:14px 24px;text-decoration:none;font-weight:700;font-size:12px;letter-spacing:.12em;text-transform:uppercase;border-radius:6px">Sign in to my onboarding</a>
  </p>
  <p style="font-size:15px;line-height:1.6">Or enter this code on the sign-in page (valid about ${mins} minutes):</p>
  <p style="font-size:32px;font-weight:800;letter-spacing:.25em;margin:16px 0">${otp}</p>
  <p style="font-size:12px;color:#6B6458;line-height:1.6">Resending within the hour emails the <b>same</b> code — check spam before waiting for a new one.</p>
  <p style="font-size:12px;color:#6B6458;line-height:1.6">Didn't request this? You can ignore this message.</p>
  <p style="font-size:11px;color:#B5AFA5;margin-top:24px">Questions · <a href="tel:+12482708490" style="color:#0B1E3D">(248) 270-8490</a> NEXUS desk · <a href="mailto:hr@deedavis.biz" style="color:#0B1E3D">hr@deedavis.biz</a></p>
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
      body: JSON.stringify({ error: 'Sign-in is temporarily unavailable. Call (248) 270-8490 NEXUS desk or email hr@deedavis.biz.' }),
    };
  }

  if (!EMAIL_PASSWORD) {
    return {
      statusCode: 503,
      headers: cors,
      body: JSON.stringify({ error: 'Email service not configured. Call (248) 270-8490 NEXUS desk or email hr@deedavis.biz.' }),
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

  const firstName = cleanNamePart(body.firstName || body.first_name);
  const lastName = cleanNamePart(body.lastName || body.last_name);
  if (!firstName || !lastName) {
    return {
      statusCode: 400,
      headers: cors,
      body: JSON.stringify({ error: 'First name and last name are required' }),
    };
  }

  const loginToken = createLoginLinkToken(email, secret);
  const otp = otpForEmail(email, secret);
  const link = `${PORTAL_ORIGIN.replace(/\/$/, '')}/?login=${encodeURIComponent(loginToken)}`;
  const mail = buildSignInEmail(email, otp, link, firstName, lastName);

  try {
    const transport = nodemailer.createTransport({
      service: 'gmail',
      auth: { user: AUTH_EMAIL, pass: AUTH_PASSWORD },
    });
    // Deliverability rule: authenticate + envelope as the real Gmail account
    // (AUTH_EMAIL). Putting hr@deedavis.biz in From: alone often lands OTP
    // mail in spam when SPF/DKIM for deedavis.biz doesn't align with Gmail's
    // relay. Visible From stays AUTH_EMAIL; Reply-To points at hr@ so replies
    // still hit the HR alias. GATEWAY_FROM_EMAIL (hr@) is kept as Reply-To.
    const info = await transport.sendMail({
      from: `"DDI GATEWAY Onboarding" <${AUTH_EMAIL}>`,
      replyTo: FROM_EMAIL !== AUTH_EMAIL ? FROM_EMAIL : undefined,
      to: email,
      subject: mail.subject,
      text: mail.text,
      html: mail.html,
      envelope: { from: AUTH_EMAIL, to: email },
    });
    console.log('gateway-auth-send OK:', JSON.stringify({
      messageId: info.messageId, accepted: info.accepted, rejected: info.rejected, response: info.response,
      from: AUTH_EMAIL, replyTo: FROM_EMAIL,
    }));
  } catch (err) {
    console.error('gateway-auth-send email error:', err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({
        error: 'Could not send sign-in email. Try again in a minute or call (248) 270-8490 NEXUS desk.',
      }),
    };
  }

  return {
    statusCode: 200,
    headers: cors,
    body: JSON.stringify({
      ok: true,
      email,
      message: 'Sign-in link and code sent. Check your inbox (and spam).',
      expires_minutes: Math.round(WINDOW_MS / 60000),
    }),
  };
};
