/** Proxy client order history from NEXUS API (GET /prism/orders/my?email=) */
const PRISM_API = process.env.PRISM_API_BASE || 'https://deedavis.pythonanywhere.com';

exports.handler = async (event) => {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Accept',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: cors, body: '' };
  }

  if (event.httpMethod !== 'GET') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const email = (event.queryStringParameters?.email || '').trim().toLowerCase();
  if (!email || !email.includes('@')) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Valid email required' }) };
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
