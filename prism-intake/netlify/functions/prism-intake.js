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

const DDI_PHONE = '248.376.4550';
const DDI_EMAIL = 'info@deedavis.biz';

function normEmail(v) {
  const s = (v || '').trim().toLowerCase();
  return s && s.includes('@') ? s : '';
}

function subjectName(data) {
  return `${data.subject_first || ''} ${data.subject_last || ''}`.trim() || 'Member';
}

function scheduleLine(data) {
  return `${data.sched_date || '—'} at ${data.sched_time || '—'} ${data.sched_tz || ''}`.trim();
}

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
Name:          ${subjectName(data)}
DOB:           ${data.subject_dob || '—'}
Phone:         ${data.subject_phone || '—'}
Email:         ${data.subject_email || '—'}
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

function buildRequesterConfirmation(data) {
  const member = subjectName(data);
  const pickup = data.subject_location || '—';
  const dropoff = data.collection_site || '—';
  return `Hi ${data.client_contact || data.client_company || 'there'},

Your service request with Dee Davis Inc. has been received and queued for dispatch.

Confirmation:  ${data.confirmation}
Service:       ${data.service_label || 'Service Request'}
Member/Rider:  ${member}
Scheduled:     ${scheduleLine(data)}
Pickup:        ${pickup}
Destination:   ${dropoff}

Our operations team will coordinate fulfillment per your schedule. You can track this order in the PRISM client portal using the email address on this request.

Questions? Call ${DDI_PHONE} or email ${DDI_EMAIL}.

— PRISM Dispatch
Dee Davis Inc.
755 W. Big Beaver Rd., Suite 2020, Troy, MI 48084
`;
}

function buildRiderConfirmation(data) {
  const member = subjectName(data);
  const requester = data.client_company || data.client_contact || 'Your care coordinator';
  return `Hi ${member.split(' ')[0] || member},

This confirms your scheduled service with Dee Davis Inc.

Confirmation:  ${data.confirmation}
Service:       ${data.service_label || 'Medical mobility'}
Scheduled:     ${scheduleLine(data)}
Pickup:        ${data.subject_location || '—'}
Destination:   ${data.collection_site || '—'}
Requested by:  ${requester}

Please be ready at your pickup location at the scheduled time. Your driver or collector will contact you before arrival when applicable.

Questions? Call ${DDI_PHONE}.

— Dee Davis Inc. / PRISM Dispatch
`;
}

function getTransporter() {
  if (!EMAIL_PASSWORD) {
    throw new Error('Email not configured (NEXUS_EMAIL_PASSWORD missing on Netlify)');
  }
  return nodemailer.createTransport({
    host: process.env.SMTP_SERVER || 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: { user: EMAIL_FROM, pass: EMAIL_PASSWORD },
  });
}

async function sendMail({ to, subject, text }) {
  const transporter = getTransporter();
  await transporter.sendMail({
    from: `PRISM Dispatch <${EMAIL_FROM}>`,
    to,
    subject,
    text,
  });
}

/** Internal ops notification — service routing + admin + sender inbox (if configured). */
async function sendOpsEmail(data) {
  const routing = data.routing_email || ADMIN_EMAIL;
  const recipients = [...new Set(
    [routing, ADMIN_EMAIL, EMAIL_FROM].filter((e) => e && String(e).includes('@'))
  )];
  const priority = URGENCY_LABEL[(data.urgency || 'routine').toLowerCase()] || 'Standard';
  const icon = priority === 'STAT' ? '🚨' : priority === 'Same Day' ? '⚡' : '📋';
  const subject = `${icon} PRISM Order — ${data.confirmation} — ${data.service_label || 'Service Request'}`;

  await sendMail({ to: recipients.join(', '), subject, text: buildEmailBody(data) });
  return routing;
}

/** Client-facing confirmations — requester + member/rider (when emails differ). */
async function sendClientConfirmations(data) {
  const requesterEmail = normEmail(data.client_email);
  const riderEmail = normEmail(data.subject_email);
  const priority = URGENCY_LABEL[(data.urgency || 'routine').toLowerCase()] || 'Standard';
  const icon = priority === 'STAT' ? '🚨' : '📋';
  const baseSubject = `${icon} PRISM Confirmation — ${data.confirmation} — ${data.service_label || 'Service Request'}`;

  let requesterSent = false;
  let riderSent = false;

  if (requesterEmail) {
    await sendMail({
      to: requesterEmail,
      subject: baseSubject,
      text: buildRequesterConfirmation(data),
    });
    requesterSent = true;
  }

  if (riderEmail && riderEmail !== requesterEmail) {
    await sendMail({
      to: riderEmail,
      subject: `${icon} Your Trip Confirmation — ${data.confirmation}`,
      text: buildRiderConfirmation(data),
    });
    riderSent = true;
  } else if (riderEmail && riderEmail === requesterEmail) {
    // Same person — requester email already covers both roles
    riderSent = requesterSent;
  }

  return { requesterSent, riderSent, requesterEmail, riderEmail };
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

    const [apiResult, opsResult, confirmResult] = await Promise.allSettled([
      syncToNexusDashboard(data),
      sendOpsEmail(data),
      sendClientConfirmations(data),
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
    let opsEmailSent = false;
    let emailError = null;
    if (opsResult.status === 'fulfilled') {
      opsEmailSent = true;
      routing = opsResult.value;
    } else {
      emailError = opsResult.reason?.message || 'Ops email failed';
    }

    let requesterConfirmationSent = false;
    let riderConfirmationSent = false;
    if (confirmResult.status === 'fulfilled') {
      requesterConfirmationSent = confirmResult.value.requesterSent;
      riderConfirmationSent = confirmResult.value.riderSent;
    } else if (!emailError) {
      emailError = confirmResult.reason?.message || 'Confirmation email failed';
    }

    const anyEmailSent = opsEmailSent || requesterConfirmationSent || riderConfirmationSent;

    if (!dashboardSync && !anyEmailSent) {
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
    if (dashboardSync && anyEmailSent) {
      message = `Order ${dashboard.order_id || data.confirmation} queued in NEXUS PRISM`;
      if (requesterConfirmationSent) message += ` — confirmation sent to requester`;
      if (riderConfirmationSent) message += ` — confirmation sent to member/rider`;
      if (opsEmailSent) message += ` — ops notified at ${routing}`;
    } else if (dashboardSync) {
      message = `Order ${dashboard.order_id || data.confirmation} queued in NEXUS PRISM dashboard (email not sent: ${emailError})`;
    } else {
      message = `Email sent — PRISM dashboard sync pending (${dashboardError})`;
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
        email_sent: anyEmailSent,
        ops_email_sent: opsEmailSent,
        requester_confirmation_sent: requesterConfirmationSent,
        rider_confirmation_sent: riderConfirmationSent,
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
