/** Proxy portal survey submit (POST /prism/nemt/satisfaction/submit) */
const PRISM_API = process.env.PRISM_API_BASE || 'https://deedavis.pythonanywhere.com';

exports.handler = async (event) => {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Accept',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: cors, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: cors, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  let body = event.body || '{}';
  if (event.isBase64Encoded) {
    body = Buffer.from(body, 'base64').toString('utf8');
  }

  try {
    const upstream = await fetch(`${PRISM_API}/prism/nemt/satisfaction/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body,
    });
    const text = await upstream.text();
    return {
      statusCode: upstream.status,
      headers: cors,
      body: text || JSON.stringify({ success: false }),
    };
  } catch (err) {
    console.error('prism-satisfaction-submit proxy error:', err);
    return {
      statusCode: 502,
      headers: cors,
      body: JSON.stringify({ success: false, error: 'Survey service unavailable' }),
    };
  }
};
