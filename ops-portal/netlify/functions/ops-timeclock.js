/** OPS timeclock — session = on shift (login in / logout out / heartbeat) */
const { refreshSessionToken, getSecret, portalCors } = require('./lib/ops-auth');

const OPS_API = (process.env.OPS_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');

exports.handler = async (event) => {
  const origin = event.headers?.origin || event.headers?.Origin;
  const cors = portalCors(origin);
  if (event.httpMethod === 'OPTIONS') return { statusCode: 204, headers: cors, body: '' };
  if (!['GET', 'POST'].includes(event.httpMethod)) {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const auth = event.headers?.authorization || event.headers?.Authorization || '';
  const bearer = auth.startsWith('Bearer ') ? auth.slice(7).trim() : '';
  const refreshed = refreshSessionToken(bearer, getSecret());
  if (!refreshed) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Session expired' }) };
  }

  let body = {};
  try {
    body = JSON.parse(event.body || '{}');
  } catch {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  const qs = event.queryStringParameters || {};
  const action = (body.action || qs.action || 'status').toLowerCase().replace(/_/g, '-');

  let path;
  let method = 'POST';
  if (action === 'status') {
    path = '/ops/timeclock/status';
    method = event.httpMethod === 'GET' ? 'GET' : 'POST';
  } else if (['clock-in', 'in', 'session-start', 'ensure'].includes(action)) {
    path = '/ops/timeclock/session-start';
  } else if (['clock-out', 'out', 'session-end'].includes(action)) {
    path = '/ops/timeclock/session-end';
  } else if (action === 'heartbeat') {
    path = '/ops/timeclock/heartbeat';
  } else if (action === 'send-to-vertex' || action === 'vertex') {
    path = '/ops/timeclock/send-to-vertex';
  } else {
    return {
      statusCode: 400,
      headers: cors,
      body: JSON.stringify({
        error: 'action must be status|session-start|session-end|heartbeat|send-to-vertex',
      }),
    };
  }

  const payload = { email: refreshed.email };
  if (body.note) payload.note = body.note;
  if (body.reason) payload.reason = body.reason;
  if (body.source) payload.source = body.source;
  if (body.periodStart) payload.periodStart = body.periodStart;
  if (body.periodEnd) payload.periodEnd = body.periodEnd;
  if (body.workEvent || body.work) payload.workEvent = true;
  if (body.event || body.label) payload.event = body.event || body.label;

  let url = `${OPS_API}${path}`;
  if (method === 'GET') {
    url += `?email=${encodeURIComponent(refreshed.email)}`;
  }

  try {
    const res = await fetch(url, {
      method,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: method === 'GET' ? undefined : JSON.stringify(payload),
    });
    const data = await res.json().catch(() => ({}));
    data.session = refreshed.session;
    data.email = refreshed.email;
    return { statusCode: res.status, headers: cors, body: JSON.stringify(data) };
  } catch (err) {
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({
        error: 'Could not reach OPS timeclock',
        detail: String(err.message || err).slice(0, 120),
      }),
    };
  }
};
