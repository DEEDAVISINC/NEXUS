const {
  getSecret,
  normEmail,
  verifyOtp,
  verifyLoginLinkToken,
  createSessionToken,
  portalCors,
  IDLE_TTL_SEC,
  ABSOLUTE_TTL_SEC,
} = require('./lib/ops-auth');

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

  let body = {};
  try {
    body = JSON.parse(event.body || '{}');
  } catch {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  let email = null;
  if (body.login_token) {
    email = verifyLoginLinkToken(body.login_token, secret);
    if (!email) {
      return {
        statusCode: 401,
        headers: cors,
        body: JSON.stringify({ error: 'This sign-in link expired. Request a new code.' }),
      };
    }
  } else {
    email = normEmail(body.email);
    const code = String(body.code || '').trim();
    if (!email || !code) {
      return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Email and 6-digit code required' }) };
    }
    if (!verifyOtp(email, code, secret)) {
      return {
        statusCode: 401,
        headers: cors,
        body: JSON.stringify({ error: 'That code did not match. Use the newest OPS email, or tap the sign-in link.' }),
      };
    }
  }

  const session = createSessionToken(email, secret);
  if (!session) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Could not create session' }) };
  }

  return {
    statusCode: 200,
    headers: cors,
    body: JSON.stringify({
      ok: true,
      email,
      session,
      idle_seconds: IDLE_TTL_SEC,
      absolute_seconds: ABSOLUTE_TTL_SEC,
    }),
  };
};
