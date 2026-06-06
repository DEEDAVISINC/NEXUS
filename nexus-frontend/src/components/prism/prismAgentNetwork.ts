/** PRISM field agent network — filter, match, sort (scales to hundreds+) */

export interface PrismAgentRecord {
  id: string;
  name: string;
  specialties?: string[];
  status?: string;
  city?: string;
  state?: string;
  completionRate?: number;
  onTimeRate?: number;
  errorRate?: number;
  rating?: number;
  ordersCompleted?: number;
  activeOrders?: number;
}

export type AgentSortKey = 'name' | 'rating' | 'active' | 'completed' | 'location';

/** Registration / free-text specialty → order type tokens */
const SPECIALTY_TYPE_MAP: Record<string, string[]> = {
  signing: ['notary'],
  ron: ['ron'],
  'collector-dot': ['dot'],
  'collector-nondot': ['non-dot'],
  dna: ['dna'],
  fingerprint: ['fingerprint'],
  background: ['background'],
  courier: ['courier', 'medical_courier', 'rx_delivery'],
  process: ['process'],
  nemt: ['nemt'],
  phlebotomy: ['phlebotomy'],
  dot: ['dot'],
  'non-dot': ['non-dot'],
  notary: ['notary'],
  apostille: ['apostille'],
};

function normalizeStatus(status?: string): 'active' | 'busy' | 'offline' {
  const s = (status || '').toLowerCase();
  if (s === 'busy' || s === 'on_job' || s === 'on job') return 'busy';
  if (s === 'offline' || s === 'inactive') return 'offline';
  return 'active';
}

function agentTypeTokens(agent: PrismAgentRecord): Set<string> {
  const tokens = new Set<string>();
  for (const raw of agent.specialties || []) {
    const key = raw.toLowerCase().trim();
    tokens.add(key);
    (SPECIALTY_TYPE_MAP[key] || []).forEach((t) => tokens.add(t));
    if (key.includes('dot')) tokens.add('dot');
    if (key.includes('nemt') || key.includes('driver')) tokens.add('nemt');
    if (key.includes('notary') || key.includes('signing')) tokens.add('notary');
    if (key.includes('courier')) {
      tokens.add('courier');
      tokens.add('medical_courier');
    }
  }
  return tokens;
}

/** Agent qualifies for a division when specialties overlap division order types or role labels */
export function agentMatchesDivision(
  agent: PrismAgentRecord,
  divisionTypes: string[],
  agentSpecialtyLabels: string[] = []
): boolean {
  if (!divisionTypes.length && !agentSpecialtyLabels.length) return true;

  const tokens = agentTypeTokens(agent);
  const divTypes = divisionTypes.map((t) => t.toLowerCase());

  if (divTypes.some((t) => tokens.has(t))) return true;

  const specText = (agent.specialties || []).join(' ').toLowerCase();
  if (agentSpecialtyLabels.some((label) => specText.includes(label.toLowerCase()))) return true;

  return false;
}

export interface AgentFilterOptions {
  query?: string;
  statusFilter?: 'all' | 'active' | 'busy' | 'offline';
  stateFilter?: string;
  divisionOnly?: boolean;
  divisionTypes?: string[];
  agentSpecialtyLabels?: string[];
  sort?: AgentSortKey;
  page?: number;
  pageSize?: number;
}

export function filterAndSortAgents(
  agents: PrismAgentRecord[],
  opts: AgentFilterOptions
): { items: PrismAgentRecord[]; total: number; page: number; pageSize: number; totalPages: number } {
  const {
    query = '',
    statusFilter = 'all',
    stateFilter = '',
    divisionOnly = true,
    divisionTypes = [],
    agentSpecialtyLabels = [],
    sort = 'name',
    page = 1,
    pageSize = 25,
  } = opts;

  const q = query.trim().toLowerCase();

  let list = [...agents];

  if (divisionOnly && (divisionTypes.length || agentSpecialtyLabels.length)) {
    list = list.filter((a) => agentMatchesDivision(a, divisionTypes, agentSpecialtyLabels));
  }

  if (statusFilter !== 'all') {
    list = list.filter((a) => normalizeStatus(a.status) === statusFilter);
  }

  if (stateFilter) {
    list = list.filter((a) => (a.state || '').toUpperCase() === stateFilter.toUpperCase());
  }

  if (q) {
    list = list.filter((a) => {
      const hay = [
        a.name,
        a.city,
        a.state,
        a.id,
        ...(a.specialties || []),
      ]
        .join(' ')
        .toLowerCase();
      return hay.includes(q);
    });
  }

  list.sort((a, b) => {
    switch (sort) {
      case 'rating':
        return (b.rating ?? 0) - (a.rating ?? 0);
      case 'active':
        return (b.activeOrders ?? 0) - (a.activeOrders ?? 0);
      case 'completed':
        return (b.ordersCompleted ?? 0) - (a.ordersCompleted ?? 0);
      case 'location':
        return `${a.state || ''}${a.city || ''}`.localeCompare(`${b.state || ''}${b.city || ''}`);
      default:
        return (a.name || '').localeCompare(b.name || '');
    }
  });

  const total = list.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(Math.max(1, page), totalPages);
  const start = (safePage - 1) * pageSize;

  return {
    items: list.slice(start, start + pageSize),
    total,
    page: safePage,
    pageSize,
    totalPages,
  };
}

export function countDivisionAgents(
  agents: PrismAgentRecord[],
  divisionTypes: string[],
  agentSpecialtyLabels: string[] = []
): number {
  return agents.filter((a) => agentMatchesDivision(a, divisionTypes, agentSpecialtyLabels)).length;
}

export function agentStatusLabel(agent: PrismAgentRecord): { label: string; color: string } {
  const active = agent.activeOrders ?? 0;
  const norm = normalizeStatus(agent.status);
  if (norm === 'offline') return { label: 'Offline', color: '#6B7280' };
  if (norm === 'busy' || active >= 3) return { label: 'On jobs', color: '#A78BFA' };
  if (active > 0) return { label: 'Available', color: '#34D399' };
  return { label: 'Ready', color: '#34D399' };
}

export function uniqueAgentStates(agents: PrismAgentRecord[]): string[] {
  const set = new Set<string>();
  agents.forEach((a) => {
    if (a.state) set.add(a.state.toUpperCase());
  });
  return Array.from(set).sort();
}
