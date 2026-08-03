const { refreshSessionToken, getSecret, portalCors } = require('./lib/ops-auth');

const OPS_API = (process.env.OPS_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');

exports.handler = async (event) => {
  const origin = event.headers?.origin || event.headers?.Origin;
  const cors = portalCors(origin);
  if (event.httpMethod === 'OPTIONS') return { statusCode: 204, headers: cors, body: '' };
  if (event.httpMethod !== 'GET') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const auth = event.headers?.authorization || event.headers?.Authorization || '';
  const bearer = auth.startsWith('Bearer ') ? auth.slice(7).trim() : '';
  const refreshed = refreshSessionToken(bearer, getSecret());
  if (!refreshed) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Session expired' }) };
  }

  const qs = event.queryStringParameters || {};
  const params = new URLSearchParams({ email: refreshed.email });
  if (qs.view) params.set('view', qs.view);
  if (qs.mine === '1') params.set('mine', '1');
  if (qs.q) params.set('q', qs.q);
  if (qs.demo) params.set('demo', qs.demo);
  try {
    const res = await fetch(
      `${OPS_API}/ops/prism/queue?${params.toString()}`,
      { headers: { Accept: 'application/json' } }
    );
    const data = await res.json().catch(() => ({}));
    data.session = refreshed.session;
    return { statusCode: res.status, headers: cors, body: JSON.stringify(data) };
  } catch (err) {
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ error: 'Could not reach NEXUS PRISM queue', detail: String(err.message || err).slice(0, 120) }),
    };
  }
};
