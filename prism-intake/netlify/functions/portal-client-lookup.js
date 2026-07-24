/** Authenticated CRM + billing lookup for portal dashboard */
const PRISM_API = (process.env.PRISM_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');
const { sessionFromEvent, portalCors } = require('./lib/portal-auth');

async function fetchJson(url) {
  try {
    const res = await fetch(url, { headers: { Accept: 'application/json' } });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

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

  const enc = encodeURIComponent(email);
  const [crmData, billingData] = await Promise.all([
    fetchJson(`${PRISM_API}/prism/crm/lookup?email=${enc}`),
    fetchJson(`${PRISM_API}/prism/billing/lookup?email=${enc}`),
  ]);

  return {
    statusCode: 200,
    headers: cors,
    body: JSON.stringify({
      email,
      crm: crmData,
      billing: billingData,
    }),
  };
};
