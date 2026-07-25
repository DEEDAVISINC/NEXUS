/** Authenticated letter download — proxies NEXUS-generated offer/welcome HTML */
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

  const email = sessionFromEvent(event);
  if (!email) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Sign in required' }) };
  }

  const which = (event.queryStringParameters?.which || 'offer').toLowerCase();
  if (!['offer', 'welcome'].includes(which)) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'which must be offer or welcome' }) };
  }

  try {
    const url = `${GATEWAY_API}/nexus/hr/onboarding/self/letters/${which}?email=${encodeURIComponent(email)}`;
    const res = await fetch(url);
    const html = await res.text();
    if (!res.ok) {
      let err = { error: 'Letter not available' };
      try { err = JSON.parse(html); } catch (_) { /* keep */ }
      return { statusCode: res.status, headers: { ...cors, 'Content-Type': 'application/json' }, body: JSON.stringify(err) };
    }
    return {
      statusCode: 200,
      headers: { ...cors, 'Content-Type': 'text/html; charset=utf-8' },
      body: html,
    };
  } catch (err) {
    console.error('gateway-letter error:', err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ error: 'Could not load letter. Try again or call (248) 270-8490.' }),
    };
  }
};
