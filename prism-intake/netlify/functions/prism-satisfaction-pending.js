/** Proxy pending ride surveys — requires portal session */
const PRISM_API = process.env.PRISM_API_BASE || 'https://deedavis.pythonanywhere.com';
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

  const sessionEmail = sessionFromEvent(event);
  if (!sessionEmail) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Sign in required' }) };
  }

  const qs = event.queryStringParameters || {};
  const params = new URLSearchParams();
  params.set('email', sessionEmail);
  if (qs.phone) params.set('phone', qs.phone);
  if (qs.order_ids) params.set('order_ids', qs.order_ids);

  try {
    const upstream = await fetch(
      `${PRISM_API}/prism/nemt/satisfaction/pending?${params.toString()}`,
      { headers: { Accept: 'application/json' } }
    );
    const text = await upstream.text();
    return {
      statusCode: upstream.status,
      headers: cors,
      body: text || JSON.stringify({ pending: [], count: 0 }),
    };
  } catch (err) {
    console.error('prism-satisfaction-pending proxy error:', err);
    return {
      statusCode: 200,
      headers: cors,
      body: JSON.stringify({ pending: [], count: 0, offline: true }),
    };
  }
};
