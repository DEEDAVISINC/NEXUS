/**
 * MI Bridges Community Partner resources — Cause We Care
 * Source: MDHHS Spring 2026 Community Partner Newsletter (May 19, 2026)
 * CWC + DDI — MDHHS MI Bridges Community Partner since May 15, 2020
 */

export const MI_BRIDGES_PARTNER = {
  partnerSince: 'May 15, 2020',
  role: 'Navigation Partner',
  lpocNote: 'Community partner accounts must be created before attending training or users may not be marked as trained.',
  partnerEmail: 'MDHHSCommunityPartners@michigan.gov',
  clientPortal: 'https://newmibridges.michigan.gov',
  partnerHub: 'https://www.michigan.gov/mdhhs/doing-business/mibridgespartners',
  trainingUrl: 'https://www.michigan.gov/mdhhs/doing-business/mibridgespartners/training',
  toolsUrl: 'https://www.michigan.gov/mdhhs/doing-business/mibridgespartners/tools',
  partnerFaqUrl: 'https://www.michigan.gov/mdhhs/doing-business/mibridgespartners/questions/mi-bridges-community-partners-frequently-asked-questions',
  clientHelpUrl: 'https://newmibridges.michigan.gov/s/isd-landing-page?language=en_US',
  mi211Url: 'https://www.mi211.org',
  newsletterDate: 'Spring 2026',
};

export const MI_BRIDGES_HELP_DESK = {
  phone: '1-844-799-9876',
  tty: '1-833-285-5910',
  hours: 'Monday–Friday, 8:00 AM – 5:00 PM ET',
  desc: 'For residents who need help with MI Bridges account access or ID proofing.',
};

/** FAP Toolkit — SNAP work requirements & payment error rate (Spring 2026 newsletter) */
export const FAP_TOOLKIT = [
  {
    title: 'SNAP Payment Error Rate (PER)',
    desc: 'How Michigan measures benefit accuracy and what it means for families receiving food assistance.',
    url: 'https://www.michigan.gov/mdhhs/assistance-programs/food/snap-payment-error-rate',
    category: 'staff' as const,
  },
  {
    title: 'Work Requirements for Food Assistance',
    desc: 'Time Limited Food Assistance (TLFA) rules — who must meet work requirements and how to comply.',
    url: 'https://www.michigan.gov/mdhhs/assistance-programs/food/learn-more/work-requirements',
    category: 'both' as const,
  },
  {
    title: 'Work Requirements Flyer (PDF)',
    desc: 'Printable flyer for clients — 20 hrs/week average, Michigan Works!, and community service options.',
    url: 'https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Assistance-Programs/Food-Assistance/Work_Requirements_for_Food_Assistance_Flyer.pdf',
    category: 'both' as const,
  },
  {
    title: 'Food Assistance Program',
    desc: 'Apply for SNAP, check eligibility, and manage your case in MI Bridges.',
    url: 'https://www.michigan.gov/mdhhs/assistance-programs/food',
    category: 'family' as const,
  },
];

/** Client-facing FAQ from Spring 2026 newsletter */
export const MI_BRIDGES_CLIENT_FAQ = [
  {
    q: 'How do I confirm my documents were sent to MDHHS?',
    a: 'After you upload a document, you will see an "Upload Successful" screen. You can also go to the "View Documents" page to see everything you have submitted.',
  },
  {
    q: 'How do I renew my benefits?',
    a: 'During your renewal or redetermination period, look for the "Renew Benefits" button on your MI Bridges dashboard.',
  },
];

/** Staff/partner FAQ (MI Bridges for Business) */
export const MI_BRIDGES_PARTNER_FAQ = [
  {
    q: 'How does my client confirm documents were sent to MDHHS?',
    a: 'After upload, they see an "Upload Successful" screen. They can also navigate to "View Documents" to view all previously submitted documents.',
  },
  {
    q: 'How can my client renew their benefits?',
    a: 'During renewal or redetermination, a "Renew Benefits" button appears on their MI Bridges dashboard.',
  },
  {
    q: 'How do I retrieve my username?',
    a: 'Click "Lookup your user ID" on the MI Bridges for Business login page and follow the instructions.',
  },
  {
    q: 'I forgot my password. How do I retrieve it?',
    a: 'Click "Forgot your password?" on the MI Bridges for Business login page and follow the instructions.',
  },
];

/** Upcoming MDHHS Navigation Trainings — FY end (Spring 2026 newsletter) */
export const NAVIGATION_TRAININGS = [
  { date: 'Thursday, June 25, 2026', time: '10:00 AM – 12:00 PM ET' },
  { date: 'Wednesday, July 29, 2026', time: '2:30 – 4:30 PM ET' },
  { date: 'Monday, August 17, 2026', time: '10:00 AM – 12:00 PM ET' },
  { date: 'Friday, September 25, 2026', time: '1:00 – 3:00 PM ET' },
];

/** Partner tools & outreach materials (Spring 2026 newsletter) */
export const MI_BRIDGES_PARTNER_LINKS = [
  {
    name: 'Community Partner Tools and Resources',
    desc: 'Guides, videos, job aids, and outreach materials for partners.',
    url: MI_BRIDGES_PARTNER.toolsUrl,
  },
  {
    name: 'Community Partner Help Page',
    desc: 'CP ID numbers, viewing client benefits, technical assistance.',
    url: MI_BRIDGES_PARTNER.partnerFaqUrl,
  },
  {
    name: 'MI Bridges Client Help',
    desc: 'Search or browse help topics for residents using MI Bridges.',
    url: MI_BRIDGES_PARTNER.clientHelpUrl,
  },
  {
    name: 'Michigan 211',
    desc: 'Database of 27,000+ programs for Michiganders — search by need and location.',
    url: MI_BRIDGES_PARTNER.mi211Url,
  },
  {
    name: 'Community Partner Training',
    desc: 'Register for Navigation, Referral, or Access partner training.',
    url: MI_BRIDGES_PARTNER.trainingUrl,
  },
];

/** Additional family resources from newsletter — merged into CWC site */
export const MI_BRIDGES_FAMILY_RESOURCES = [
  {
    icon: '📱',
    title: 'MI Bridges — Apply for Benefits',
    desc: 'Food assistance, Medicaid, cash, childcare, and energy help — apply and track your application in one place.',
    url: MI_BRIDGES_PARTNER.clientPortal,
    phone: MI_BRIDGES_HELP_DESK.phone,
    category: 'benefits',
  },
  {
    icon: '📋',
    title: 'Track Your Application',
    desc: 'After applying in MI Bridges, use your dashboard to see application status and next steps.',
    url: MI_BRIDGES_PARTNER.clientPortal,
    category: 'benefits',
  },
  {
    icon: '🔄',
    title: 'Renew Your Benefits',
    desc: 'When it is time to renew, look for the "Renew Benefits" button on your MI Bridges dashboard.',
    url: MI_BRIDGES_PARTNER.clientPortal,
    category: 'benefits',
  },
  {
    icon: '📤',
    title: 'Upload Documents to MDHHS',
    desc: 'Upload verifications from your phone or computer. You will see "Upload Successful" when MDHHS receives them.',
    url: MI_BRIDGES_PARTNER.clientPortal,
    category: 'benefits',
  },
  {
    icon: '🍎',
    title: 'SNAP Work Requirements',
    desc: 'Learn if work requirements apply to your food assistance and how to stay eligible.',
    url: 'https://www.michigan.gov/mdhhs/assistance-programs/food/learn-more/work-requirements',
    category: 'food',
  },
  {
    icon: '☎️',
    title: 'MI Bridges Help Desk',
    desc: MI_BRIDGES_HELP_DESK.desc,
    url: `tel:${MI_BRIDGES_HELP_DESK.phone.replace(/-/g, '')}`,
    phone: `${MI_BRIDGES_HELP_DESK.phone} (TTY: ${MI_BRIDGES_HELP_DESK.tty})`,
    category: 'help',
  },
  {
    icon: '🔍',
    title: 'Michigan 211',
    desc: 'Free, confidential search of 27,000+ Michigan programs — food, housing, health, utilities, and more.',
    url: MI_BRIDGES_PARTNER.mi211Url,
    phone: '211',
    category: 'help',
  },
];
