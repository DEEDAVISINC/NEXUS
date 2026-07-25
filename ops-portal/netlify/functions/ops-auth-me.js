const {
  sessionFromEvent,
  refreshSessionToken,
  getSecret,
  portalCors,
  IDLE_TTL_SEC,
  ABSOLUTE_TTL_SEC,
} = require('./lib/ops-auth');

exports.handler = async (event) => {
  const origin = event.headers?.origin || event.headers?.Origin;
  const cors = portalCors(origin);

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: cors, body: '' };
  }
  if (event.httpMethod !== 'GET') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  const secret = getSecret();
  const auth = event.headers?.authorization || event.headers?.Authorization || '';
  const bearer = auth.startsWith('Bearer ') ? auth.slice(7).trim() : '';
  const refreshed = refreshSessionToken(bearer, secret);
  if (!refreshed) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Session expired' }) };
  }

  return {
    statusCode: 200,
    headers: cors,
    body: JSON.stringify({
      ok: true,
      email: refreshed.email,
      session: refreshed.session,
      idle_seconds: IDLE_TTL_SEC,
      absolute_seconds: ABSOLUTE_TTL_SEC,
      session_started: refreshed.sst,
    }),
  };
};
