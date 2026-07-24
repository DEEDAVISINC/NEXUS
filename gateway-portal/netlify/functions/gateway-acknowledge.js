/** Authenticated typed-name acknowledgment/e-sign — proxies to the GATEWAY self-service API */
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

  const { itemKey, typedName } = body;
  if (!itemKey || !typedName) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'itemKey and typedName are required' }) };
  }

  try {
    const res = await fetch(`${GATEWAY_API}/nexus/hr/onboarding/self/acknowledge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Forwarded-For': event.headers?.['x-nf-client-connection-ip'] || event.headers?.['client-ip'] || '',
      },
      body: JSON.stringify({ email, itemKey, typedName }),
    });
    const data = await res.json().catch(() => ({}));
    return { statusCode: res.status, headers: cors, body: JSON.stringify(data) };
  } catch (err) {
    console.error('gateway-acknowledge error:', err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ error: 'Could not record acknowledgment. Try again or call 855-773-0035.' }),
    };
  }
};
