const nodemailer = require('nodemailer');

const ADMIN_EMAIL = process.env.USER_EMAIL || 'info@deedavis.biz';
const EMAIL_FROM = process.env.NEXUS_EMAIL || 'bids.deedavisinc@gmail.com';
const EMAIL_PASSWORD = process.env.NEXUS_EMAIL_PASSWORD;
const PRISM_API_BASE = (process.env.PRISM_API_BASE || 'https://deedavis.pythonanywhere.com').replace(/\/$/, '');

const URGENCY_LABEL = {
  stat: 'STAT',
  emergency: 'STAT',
  'same-day': 'Same Day',
  priority: 'Same Day',
  scheduled: 'Standard',
  routine: 'Standard',
};

function buildEmailBody(data) {
  const priority = URGENCY_LABEL[(data.urgency || 'routine').toLowerCase()] || 'Standard';
  let body = `PRISM SERVICE REQUEST — DEE DAVIS INC.
========================================
Confirmation:  ${data.confirmation || '—'}
Priority:      ${priority}
Service:       ${data.service_label || data.service_key || '—'}
Tier:          ${data.tier || 1}
========================================

CLIENT
Company:       ${data.client_company || '—'}
Contact:       ${data.client_contact || '—'}
Phone:         ${data.client_phone || '—'}
Email:         ${data.client_email || '—'}
PO / Account:  ${data.client_po || '—'}
Address:       ${data.client_address || '—'}

SUBJECT / MEMBER
Name:          ${data.subject_first || ''} ${data.subject_last || ''}`.trim() + `
DOB:           ${data.subject_dob || '—'}
Phone:         ${data.subject_phone || '—'}
ID:            ${data.subject_id || '—'}
Location:      ${data.subject_location || '—'}

SCHEDULING
Date:          ${data.sched_date || '—'}
Time:          ${data.sched_time || '—'} ${data.sched_tz || ''}
Site:          ${data.collection_site || '—'}

Notes:         ${data.notes || '—'}
`;

  const details = data.details || {};
  const detailKeys = Object.keys(details);
  if (detailKeys.length) {
    body += '\nSERVICE DETAILS\n';
    for (const key of detailKeys) {
      const value = details[key];
      if (value && String(value).trim() && String(value).trim() !== '—') {
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
        body += `${label}: ${value}\n`;
      }
    }
  }

  body += `========================================
Submitted via PRISM Client Intake (Netlify)
`;
  return body;
}

async function sendOrderEmail(data) {
  if (!EMAIL_PASSWORD) {
    throw new Error('Email not configured (NEXUS_EMAIL_PASSWORD missing on Netlify)');
  }

  const routing = data.routing_email || ADMIN_EMAIL;
  const recipients = [...new Set([routing, ADMIN_EMAIL])];
  const priority = URGENCY_LABEL[(data.urgency || 'routine').toLowerCase()] || 'Standard';
  const icon = priority === 'STAT' ? '🚨' : priority === 'Same Day' ? '⚡' : '📋';
  const subject = `${icon} PRISM Order — ${data.confirmation} — ${data.service_label || 'Service Request'}`;

  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_SERVER || 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: { user: EMAIL_FROM, pass: EMAIL_PASSWORD },
  });

  await transporter.sendMail({
    from: `PRISM Dispatch <${EMAIL_FROM}>`,
    to: recipients.join(', '),
    subject,
    text: buildEmailBody(data),
  });

  return routing;
}

/** Forward intake payload to NEXUS PRISM API → orders.json + Airtable (dashboard queue). */
async function syncToNexusDashboard(data) {
  const url = `${PRISM_API_BASE}/prism/intake`;
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    });
    const text = await res.text();
    let parsed = {};
    try {
      parsed = text ? JSON.parse(text) : {};
    } catch {
      parsed = { error: text.slice(0, 300) };
    }
    if (!res.ok) {
      return {
        ok: false,
        status: res.status,
        error: parsed.error || `NEXUS API returned ${res.status}`,
      };
    }
    return {
      ok: true,
      order: parsed.order,
      order_id: parsed.order?.id || data.confirmation,
    };
  } catch (err) {
    return { ok: false, error: err.message || 'NEXUS API unreachable' };
  }
}

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

  try {
    const data = JSON.parse(event.body || '{}');
    if (!data.client_email && !data.client_company) {
      return { statusCode: 400, headers: cors, body: JSON.stringify({ error: 'Missing client information' }) };
    }

    // Dashboard sync + email in parallel — order must land in NEXUS PRISM queue
    const [apiResult, emailResult] = await Promise.allSettled([
      syncToNexusDashboard(data),
      sendOrderEmail(data),
    ]);

    const dashboard =
      apiResult.status === 'fulfilled' && apiResult.value?.ok ? apiResult.value : null;
    const dashboardSync = !!dashboard;
    const dashboardError =
      apiResult.status === 'fulfilled' && !apiResult.value?.ok
        ? apiResult.value.error
        : apiResult.status === 'rejected'
          ? apiResult.reason?.message
          : null;

    let routing = data.routing_email || ADMIN_EMAIL;
    let emailSent = false;
    let emailError = null;
    if (emailResult.status === 'fulfilled') {
      emailSent = true;
      routing = emailResult.value;
    } else {
      emailError = emailResult.reason?.message || 'Email failed';
    }

    if (!dashboardSync && !emailSent) {
      return {
        statusCode: 500,
        headers: cors,
        body: JSON.stringify({
          error: `Could not reach PRISM dashboard (${dashboardError || 'unknown'}) and email failed (${emailError})`,
          dashboard_sync: false,
          email_sent: false,
        }),
      };
    }

    let message = '';
    if (dashboardSync && emailSent) {
      message = `Order ${dashboard.order_id || data.confirmation} queued in NEXUS PRISM — email sent to ${routing}`;
    } else if (dashboardSync) {
      message = `Order ${dashboard.order_id || data.confirmation} queued in NEXUS PRISM dashboard (email not sent: ${emailError})`;
    } else {
      message = `Email sent to ${routing} — PRISM dashboard sync pending (${dashboardError})`;
    }

    return {
      statusCode: 200,
      headers: cors,
      body: JSON.stringify({
        success: true,
        confirmation: data.confirmation,
        routing_email: routing,
        dashboard_sync: dashboardSync,
        dashboard_order_id: dashboard?.order_id || null,
        email_sent: emailSent,
        dashboard_warning: dashboardSync ? null : dashboardError,
        message,
      }),
    };
  } catch (err) {
    console.error('prism-intake function error:', err);
    return {
      statusCode: 500,
      headers: cors,
      body: JSON.stringify({ error: err.message || 'Failed to submit order' }),
    };
  }
};
