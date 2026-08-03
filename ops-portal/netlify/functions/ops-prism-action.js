/** Claim / release / patch PRISM desk items */
const { refreshSessionToken, getSecret, portalCors } = require('./lib/ops-auth');

const OPS_API = (process.env.OPS_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');

exports.handler = async (event) => {
  const origin = event.headers?.origin || event.headers?.Origin;
  const cors = portalCors(origin);
  if (event.httpMethod === 'OPTIONS') return { statusCode: 204, headers: cors, body: '' };
  if (!['POST', 'PATCH', 'GET'].includes(event.httpMethod)) {
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

  const id = body.id || (event.queryStringParameters || {}).id;
  const action = (body.action || '').toLowerCase();
  const needsId = !['batch-assign', 'batch_assign'].includes(action);
  if (needsId && !id) {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Item id required' }) };
  }

  let url;
  let method = 'POST';
  let payload = { email: refreshed.email };

  if (action === 'claim') {
    url = `${OPS_API}/ops/prism/items/${encodeURIComponent(id)}/claim`;
  } else if (action === 'request') {
    url = `${OPS_API}/ops/prism/items/${encodeURIComponent(id)}/request`;
  } else if (action === 'release') {
    url = `${OPS_API}/ops/prism/items/${encodeURIComponent(id)}/release`;
    if (body.force) payload.force = true;
  } else if (action === 'assign') {
    url = `${OPS_API}/ops/prism/items/${encodeURIComponent(id)}/assign`;
    if (body.assigneeEmail) payload.assigneeEmail = body.assigneeEmail;
    if (body.assigneeName) payload.assigneeName = body.assigneeName;
  } else if (action === 'batch-assign' || action === 'batch_assign') {
    url = `${OPS_API}/ops/prism/assign-batch`;
    if (body.assigneeEmail) payload.assigneeEmail = body.assigneeEmail;
    if (body.assigneeName) payload.assigneeName = body.assigneeName;
    if (body.orderIds) payload.orderIds = body.orderIds;
  } else if (action === 'callback') {
    url = `${OPS_API}/ops/prism/items/${encodeURIComponent(id)}/callback`;
    if (body.callbackAt) payload.callbackAt = body.callbackAt;
    if (body.note) payload.note = body.note;
  } else if (action === 'patch' || event.httpMethod === 'PATCH') {
    url = `${OPS_API}/ops/prism/items/${encodeURIComponent(id)}`;
    method = 'PATCH';
    if (body.notes !== undefined) payload.notes = body.notes;
    if (body.status) payload.status = body.status;
    if (body.careStatus) payload.careStatus = body.careStatus;
    if (body.activityNote) payload.activityNote = body.activityNote;
  } else if (action === 'get' || event.httpMethod === 'GET') {
    url = `${OPS_API}/ops/prism/items/${encodeURIComponent(id)}?email=${encodeURIComponent(refreshed.email)}`;
    method = 'GET';
  } else {
    return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'action must be request|release|assign|batch-assign|callback|patch|get' }) };
  }

  try {
    const res = await fetch(url, {
      method,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: method === 'GET' ? undefined : JSON.stringify(payload),
    });
    const data = await res.json().catch(() => ({}));
    data.session = refreshed.session;
    return { statusCode: res.status, headers: cors, body: JSON.stringify(data) };
  } catch (err) {
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ error: 'Could not update PRISM item', detail: String(err.message || err).slice(0, 120) }),
    };
  }
};
