/** Authenticated OPS entitlements — proxies Flask /ops/session after JWT check.
 *  Falls back to GATEWAY /self + local desk shaping if /ops/session is not live yet.
 */
const {
  refreshSessionToken,
  getSecret,
  portalCors,
} = require('./lib/ops-auth');

const OPS_API = (process.env.OPS_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');

const LEVEL_TO_ROLE = {
  Supervisor: 'supervisor',
  Director: 'supervisor',
  Manager: 'manager',
  Agent: 'cca',
  Staff: 'cca',
};

function fallbackFromSelf(rec) {
  const level = rec.level || '';
  const opsRole = LEVEL_TO_ROLE[level] || 'cca';
  const accounts = String(rec.account || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((name) => ({ name, code: '', emoji: '' }));
  // Without Flask can-work, treat Active + portal access as provisional unlock
  // but surface that full gate needs /ops/session.
  const canWork = (rec.status || '') === 'Active';
  return {
    ok: true,
    person: {
      id: rec.id,
      name: rec.name || '',
      email: rec.email || '',
      companyEmail: rec.companyEmail || '',
      workerType: rec.workerType || '',
      roleTitle: rec.role || '',
      division: rec.division || '',
      level,
      levelCode: '',
      personnelNumber: rec.personnelNumber || '',
      status: rec.status || '',
    },
    opsRole,
    accounts,
    desks: [
      {
        id: 'prism',
        label: 'PRISM Desk',
        status: 'ready',
        description: 'Trip / member coordination queues (account-scoped)',
        unlocked: canWork,
        lockReason: canWork ? null : 'GATEWAY record not Active',
      },
      {
        id: 'claims',
        label: 'Claims',
        status: 'coming_soon',
        description: 'Data entry + manager authorization (Phase D)',
        unlocked: false,
        lockReason: 'Coming in a later phase',
      },
    ],
    canWork,
    canWorkReason: canWork
      ? 'Provisional (reload Flask for full can-work gate)'
      : 'GATEWAY record not Active',
    sessionPolicy: { idleMinutes: 15, warnMinutes: 13, absoluteHours: 12 },
    source: 'gateway-self-fallback',
  };
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

  const secret = getSecret();
  const auth = event.headers?.authorization || event.headers?.Authorization || '';
  const bearer = auth.startsWith('Bearer ') ? auth.slice(7).trim() : '';
  const refreshed = refreshSessionToken(bearer, secret);
  if (!refreshed) {
    return { statusCode: 401, headers: cors, body: JSON.stringify({ error: 'Session expired — sign in again' }) };
  }

  try {
    const opsRes = await fetch(`${OPS_API}/ops/session?email=${encodeURIComponent(refreshed.email)}`, {
      headers: { Accept: 'application/json' },
    });
    const ct = (opsRes.headers.get('content-type') || '').toLowerCase();
    if (opsRes.ok && ct.includes('application/json')) {
      const data = await opsRes.json();
      data.session = refreshed.session;
      data.email = refreshed.email;
      data.source = 'ops-session';
      return { statusCode: 200, headers: cors, body: JSON.stringify(data) };
    }

    const selfRes = await fetch(
      `${OPS_API}/nexus/hr/onboarding/self?email=${encodeURIComponent(refreshed.email)}`,
      { headers: { Accept: 'application/json' } }
    );
    const selfData = await selfRes.json().catch(() => ({}));
    if (!selfRes.ok) {
      return {
        statusCode: selfRes.status,
        headers: cors,
        body: JSON.stringify(selfData.error ? selfData : { error: 'No active GATEWAY record' }),
      };
    }
    const payload = fallbackFromSelf(selfData.record || {});
    payload.session = refreshed.session;
    payload.email = refreshed.email;
    return { statusCode: 200, headers: cors, body: JSON.stringify(payload) };
  } catch (err) {
    console.error('ops-session error:', err && err.message ? err.message : err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({
        error: 'Could not reach NEXUS. Call (248) 270-8490 NEXUS desk.',
        detail: String(err && err.message ? err.message : err).slice(0, 120),
      }),
    };
  }
};
