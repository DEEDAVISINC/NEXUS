/** Authenticated document upload — proxies to the GATEWAY self-service API */
const GATEWAY_API = (process.env.GATEWAY_API_BASE || process.env.PRISM_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');
const { sessionFromEvent, portalCors } = require('./lib/portal-auth');

exports.handler = async (event) => {
  const origin = event.headers?.origin || event.headers?.Origin;
  const cors = portalCors(origin);

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: cors, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const email = sessionFromEvent(event);
  if (!email) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Sign in required' }) };
  }

  let body = {};
  try {
    body = JSON.parse(event.body || '{}');
  } catch {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const { docType, filename, contentBase64, contentType } = body;
  if (!docType || !filename || !contentBase64) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'docType, filename, and contentBase64 are required' }) };
  }

  try {
    const res = await fetch(`${GATEWAY_API}/nexus/hr/onboarding/self/documents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      // email is the session-verified value, never the client-supplied one
      body: JSON.stringify({ email, docType, filename, contentBase64, contentType }),
    });
    const data = await res.json().catch(() => ({}));
    return { statusCode: res.status, headers: cors, body: JSON.stringify(data) };
  } catch (err) {
    console.error('gateway-upload error:', err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ error: 'Upload failed. Try again or call (248) 270-8490 NEXUS desk.' }),
    };
  }
};
