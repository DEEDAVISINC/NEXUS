/** Authenticated GATEWAY onboarding record lookup for the portal dashboard */
const GATEWAY_API = (process.env.GATEWAY_API_BASE || process.env.PRISM_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');
const { sessionFromEvent, portalCors } = require('./lib/portal-auth');

exports.handler = async (event) => {
  const origin = event.headers?.origin || event.headers?.Origin;
  const cors = portalCors(origin);

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: cors, body: '' };
  }

  if (event.httpMethod !== 'GET') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  // Email comes from the verified session token — never trust a query param here.
  const email = sessionFromEvent(event);
  if (!email) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Sign in required' }) };
  }

  try {
    const res = await fetch(`${GATEWAY_API}/nexus/hr/onboarding/self?email=${encodeURIComponent(email)}`, {
      headers: { Accept: 'application/json' },
    });
    const data = await res.json().catch(() => ({}));
    return { statusCode: res.status, headers: cors, body: JSON.stringify(data) };
  } catch (err) {
    console.error('gateway-my-record error:', err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ error: 'Could not reach onboarding system. Call 855-773-0035 for help.' }),
    };
  }
};
