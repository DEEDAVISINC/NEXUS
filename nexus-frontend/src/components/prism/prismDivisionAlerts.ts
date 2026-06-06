/** Shared logic: which orders need ops attention + per-division counts for PRISM Hub bells */

export interface PrismOrderAlertSource {
  type?: string;
  service_key?: string;
  status?: string;
  agent?: string;
  priority?: string;
}

export interface PrismDivisionAlertTarget {
  id: string;
  types: string[];
}

const TERMINAL_STATUSES = ['complete', 'completed', 'verified', 'closed', 'cancelled'];

/** Intake service_key → order type(s) used on division cards */
const SERVICE_KEY_TYPES: Record<string, string[]> = {
  'testing-drug': ['dot', 'non-dot'],
  'testing-occhealth': ['phlebotomy'],
  'testing-lead': ['phlebotomy'],
  fingerprint: ['fingerprint'],
  background: ['background'],
  dna: ['dna'],
  nemt: ['nemt'],
  arena: ['nemt'],
  courier: ['medical_courier', 'courier'],
  notary: ['notary', 'ron', 'apostille', 'process'],
  credentialing: ['credentialing'],
  workforce: ['phlebotomy'],
};

export function orderNeedsAttention(order: PrismOrderAlertSource): boolean {
  const status = (order.status || '').toLowerCase();
  if (TERMINAL_STATUSES.some((t) => status.includes(t))) return false;

  if (status === 'new' || status === 'pending' || status.includes('received')) return true;
  if (!(order.agent || '').trim()) return true;

  const pri = (order.priority || '').toLowerCase();
  if (pri === 'stat' || pri === 'same day') return true;

  return false;
}

function orderTypeTokens(order: PrismOrderAlertSource): Set<string> {
  const tokens = new Set<string>();
  const type = (order.type || '').toLowerCase();
  const sk = (order.service_key || '').toLowerCase();
  if (type) tokens.add(type);
  if (sk) {
    tokens.add(sk);
    (SERVICE_KEY_TYPES[sk] || []).forEach((t) => tokens.add(t));
  }
  return tokens;
}

export function countDivisionNotifications(
  orders: PrismOrderAlertSource[],
  divisions: PrismDivisionAlertTarget[]
): Record<string, number> {
  const counts: Record<string, number> = {};
  divisions.forEach((d) => {
    counts[d.id] = 0;
  });

  for (const order of orders) {
    if (!orderNeedsAttention(order)) continue;
    const tokens = orderTypeTokens(order);
    for (const div of divisions) {
      if (!div.types.length) continue;
      if (div.types.some((t) => tokens.has(t.toLowerCase()))) {
        counts[div.id] += 1;
      }
    }
  }

  return counts;
}

export function totalNeedsAttention(orders: PrismOrderAlertSource[]): number {
  return orders.filter(orderNeedsAttention).length;
}
