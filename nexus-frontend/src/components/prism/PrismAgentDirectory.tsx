import React, { useMemo, useState } from 'react';
import {
  AgentFilterOptions,
  AgentSortKey,
  PrismAgentRecord,
  agentStatusLabel,
  filterAndSortAgents,
  uniqueAgentStates,
} from './prismAgentNetwork';

interface PrismAgentDirectoryProps {
  agents: PrismAgentRecord[];
  loading?: boolean;
  accent: string;
  divisionName?: string;
  divisionTypes?: string[];
  agentSpecialtyLabels?: string[];
  /** Picker mode: compact list, click to select one agent */
  mode?: 'directory' | 'picker';
  onSelectAgent?: (agent: PrismAgentRecord) => void;
  onClose?: () => void;
  pickerTitle?: string;
}

const PAGE_SIZE = 25;

const PrismAgentDirectory: React.FC<PrismAgentDirectoryProps> = ({
  agents,
  loading = false,
  accent,
  divisionName,
  divisionTypes = [],
  agentSpecialtyLabels = [],
  mode = 'directory',
  onSelectAgent,
  onClose,
  pickerTitle = 'Assign field agent',
}) => {
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<AgentFilterOptions['statusFilter']>('all');
  const [stateFilter, setStateFilter] = useState('');
  const [divisionOnly, setDivisionOnly] = useState(mode === 'picker' ? true : true);
  const [sort, setSort] = useState<AgentSortKey>('name');
  const [page, setPage] = useState(1);

  const states = useMemo(() => uniqueAgentStates(agents), [agents]);

  const result = useMemo(
    () =>
      filterAndSortAgents(agents, {
        query,
        statusFilter,
        stateFilter,
        divisionOnly,
        divisionTypes,
        agentSpecialtyLabels,
        sort,
        page,
        pageSize: PAGE_SIZE,
      }),
    [agents, query, statusFilter, stateFilter, divisionOnly, divisionTypes, agentSpecialtyLabels, sort, page]
  );

  const resetPage = () => setPage(1);

  const isPicker = mode === 'picker';

  const shell = (
    <div style={{ display: 'flex', flexDirection: 'column', height: isPicker ? '100%' : undefined }}>
      {/* Toolbar */}
      <div
        style={{
          padding: isPicker ? '16px 20px' : '0 0 16px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: 10,
          alignItems: 'center',
          borderBottom: isPicker ? '1px solid rgba(255,255,255,0.06)' : undefined,
        }}
      >
        {isPicker && (
          <div style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
            <p style={{ fontWeight: 800, fontSize: 18, color: '#FFFFFF' }}>{pickerTitle}</p>
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                style={{ background: '#374151', border: 'none', color: '#F9FAFB', cursor: 'pointer', fontSize: 16, width: 32, height: 32, borderRadius: 8 }}
              >
                ✕
              </button>
            )}
          </div>
        )}

        <input
          type="search"
          placeholder="Search name, city, specialty, ID…"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            resetPage();
          }}
          style={{
            flex: '1 1 220px',
            minWidth: 200,
            padding: '10px 14px',
            borderRadius: 9,
            border: '1px solid rgba(255,255,255,0.14)',
            background: '#252532',
            color: '#FFFFFF',
            fontSize: 14,
            outline: 'none',
          }}
        />

        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value as AgentFilterOptions['statusFilter']);
            resetPage();
          }}
          style={selectStyle}
        >
          <option value="all">All status</option>
          <option value="active">Ready / available</option>
          <option value="busy">On jobs</option>
          <option value="offline">Offline</option>
        </select>

        {states.length > 0 && (
          <select
            value={stateFilter}
            onChange={(e) => {
              setStateFilter(e.target.value);
              resetPage();
            }}
            style={selectStyle}
          >
            <option value="">All states</option>
            {states.map((st) => (
              <option key={st} value={st}>
                {st}
              </option>
            ))}
          </select>
        )}

        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as AgentSortKey)}
          style={selectStyle}
        >
          <option value="name">Sort: Name</option>
          <option value="rating">Sort: Rating</option>
          <option value="active">Sort: Active jobs</option>
          <option value="completed">Sort: Completed</option>
          <option value="location">Sort: Location</option>
        </select>

        {(divisionTypes.length > 0 || agentSpecialtyLabels.length > 0) && (
          <button
            type="button"
            onClick={() => {
              setDivisionOnly((v) => !v);
              resetPage();
            }}
            style={{
              padding: '8px 12px',
              borderRadius: 8,
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
              border: `1px solid ${divisionOnly ? accent + '66' : 'rgba(255,255,255,0.1)'}`,
              background: divisionOnly ? accent + '18' : 'transparent',
              color: divisionOnly ? accent : '#9CA3AF',
            }}
          >
            {divisionOnly ? `${divisionName || 'Division'} only` : 'Full network'}
          </button>
        )}
      </div>

      {/* Summary */}
      <p style={{ fontSize: 12, color: 'rgba(107,114,128,0.85)', padding: isPicker ? '12px 20px 8px' : '12px 0 8px' }}>
        {loading ? 'Loading network…' : (
          <>
            <strong style={{ color: '#E5E7EB' }}>{result.total}</strong>
            {result.total === 1 ? ' agent' : ' agents'}
            {divisionOnly && divisionName ? ` · ${divisionName}` : divisionOnly ? ' · this division' : ' · nationwide network'}
            {query ? ` · matching “${query}”` : ''}
          </>
        )}
      </p>

      {/* Table */}
      <div
        style={{
          flex: isPicker ? 1 : undefined,
          overflow: 'auto',
          border: '1px solid rgba(255,255,255,0.06)',
          borderRadius: 12,
          background: '#14141A',
        }}
      >
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: isPicker ? 14 : 13 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left', background: isPicker ? '#252532' : 'transparent' }}>
              {['Agent', 'Location', 'Specialties', 'Status', 'Jobs', 'Rating', isPicker ? '' : ''].map((h) => (
                <th
                  key={h || 'action'}
                  style={{
                    padding: isPicker ? '12px 16px' : '10px 14px',
                    fontSize: 11,
                    fontWeight: 700,
                    color: '#E5E7EB',
                    textTransform: 'uppercase',
                    letterSpacing: 0.6,
                    width: h === '' && isPicker ? 96 : undefined,
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {!loading && result.items.length === 0 && (
              <tr>
                <td colSpan={7} style={{ padding: 32, textAlign: 'center', color: '#6B7280' }}>
                  No agents match these filters.
                  {divisionOnly && (
                    <>
                      {' '}
                      <button
                        type="button"
                        onClick={() => setDivisionOnly(false)}
                        style={{ background: 'none', border: 'none', color: accent, cursor: 'pointer', textDecoration: 'underline' }}
                      >
                        Search full network
                      </button>
                    </>
                  )}
                </td>
              </tr>
            )}
            {result.items.map((agent) => {
              const st = agentStatusLabel(agent);
              const loc = [agent.city, agent.state].filter(Boolean).join(', ') || '—';
              const specs = (agent.specialties || []).slice(0, 3).join(' · ') || '—';
              const extraSpecs = (agent.specialties?.length || 0) > 3 ? ` +${(agent.specialties?.length || 0) - 3}` : '';

              return (
                <tr
                  key={agent.id}
                  onClick={isPicker && onSelectAgent ? () => onSelectAgent(agent) : undefined}
                  style={{
                    borderBottom: '1px solid rgba(255,255,255,0.04)',
                    cursor: isPicker ? 'pointer' : 'default',
                  }}
                  onMouseEnter={(e) => {
                    if (isPicker) e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'transparent';
                  }}
                >
                  <td style={{ padding: isPicker ? '14px 16px' : '12px 14px' }}>
                    <p style={{ fontWeight: 700, fontSize: isPicker ? 15 : 14, color: '#FFFFFF' }}>{agent.name}</p>
                    <p style={{ fontSize: 12, color: '#D1D5DB', marginTop: 3 }}>{agent.id}</p>
                  </td>
                  <td style={{ padding: isPicker ? '14px 16px' : '12px 14px', color: '#F3F4F6', fontSize: isPicker ? 14 : 13 }}>{loc}</td>
                  <td style={{ padding: isPicker ? '14px 16px' : '12px 14px', color: '#E5E7EB', maxWidth: 220, fontSize: isPicker ? 14 : 13 }}>
                    <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {specs}
                      {extraSpecs}
                    </span>
                  </td>
                  <td style={{ padding: isPicker ? '14px 16px' : '12px 14px' }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: isPicker ? 14 : 12, fontWeight: 600, color: st.color }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: st.color }} />
                      {st.label}
                    </span>
                  </td>
                  <td style={{ padding: isPicker ? '14px 16px' : '12px 14px', color: '#F3F4F6', fontSize: isPicker ? 14 : 13 }}>
                    {agent.activeOrders ?? 0} active
                    <span style={{ color: '#D1D5DB', fontSize: 12 }}> / {agent.ordersCompleted ?? 0} done</span>
                  </td>
                  <td style={{ padding: isPicker ? '14px 16px' : '12px 14px', color: '#FCD34D', fontWeight: 700, fontSize: isPicker ? 15 : 13 }}>
                    {(agent.rating ?? 0).toFixed(1)}★
                  </td>
                  {isPicker ? (
                    <td style={{ padding: '14px 16px' }}>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectAgent?.(agent);
                        }}
                        style={{
                          padding: '10px 16px',
                          borderRadius: 8,
                          border: 'none',
                          background: accent,
                          color: '#fff',
                          fontSize: 13,
                          fontWeight: 800,
                          cursor: 'pointer',
                          minWidth: 72,
                        }}
                      >
                        Assign
                      </button>
                    </td>
                  ) : (
                    <td style={{ padding: '12px 14px' }}>
                      <button
                        type="button"
                        style={{
                          padding: '6px 10px',
                          borderRadius: 7,
                          border: '1px solid rgba(255,255,255,0.08)',
                          background: 'transparent',
                          color: '#9CA3AF',
                          fontSize: 11,
                          cursor: 'pointer',
                        }}
                      >
                        Profile →
                      </button>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {result.totalPages > 1 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: isPicker ? '12px 20px' : '14px 0 0',
            fontSize: 12,
            color: '#9CA3AF',
          }}
        >
          <span>
            Page {result.page} of {result.totalPages}
          </span>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              type="button"
              disabled={result.page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              style={pageBtnStyle(result.page <= 1)}
            >
              ← Prev
            </button>
            <button
              type="button"
              disabled={result.page >= result.totalPages}
              onClick={() => setPage((p) => p + 1)}
              style={pageBtnStyle(result.page >= result.totalPages)}
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );

  if (isPicker) {
    return (
      <div
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 60,
          background: 'rgba(0,0,0,0.78)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 24,
        }}
        onClick={onClose}
      >
        <div
          style={{
            width: '100%',
            maxWidth: 960,
            maxHeight: '88vh',
            background: '#1C1C26',
            borderRadius: 16,
            border: '2px solid rgba(255,255,255,0.14)',
            boxShadow: '0 24px 80px rgba(0,0,0,0.55)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {shell}
        </div>
      </div>
    );
  }

  return shell;
};

const selectStyle: React.CSSProperties = {
  padding: '10px 12px',
  borderRadius: 9,
  border: '1px solid rgba(255,255,255,0.14)',
  background: '#252532',
  color: '#FFFFFF',
  fontSize: 13,
  fontWeight: 500,
};

function pageBtnStyle(disabled: boolean): React.CSSProperties {
  return {
    padding: '6px 12px',
    borderRadius: 7,
    border: '1px solid rgba(255,255,255,0.08)',
    background: disabled ? 'transparent' : '#14141A',
    color: disabled ? '#4B5563' : '#E5E7EB',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontSize: 12,
  };
}

export default PrismAgentDirectory;
