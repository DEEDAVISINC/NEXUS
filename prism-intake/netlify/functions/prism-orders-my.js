/** Proxy client order history — requires portal session (Bearer token) */
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

  const email = sessionFromEvent(event);
  if (!email) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Sign in required' }) };
  }

  try {
    const upstream = await fetch(
      `${PRISM_API}/prism/orders/my?email=${encodeURIComponent(email)}`,
      { headers: { Accept: 'application/json' } }
    );
    const text = await upstream.text();
    return {
      statusCode: upstream.status,
      headers: cors,
      body: text || JSON.stringify({ orders: [], total: 0, email }),
    };
  } catch (err) {
    console.error('prism-orders-my proxy error:', err);
    return {
      statusCode: 200,
      headers: cors,
      body: JSON.stringify({ orders: [], total: 0, email, offline: true }),
    };
  }
};
