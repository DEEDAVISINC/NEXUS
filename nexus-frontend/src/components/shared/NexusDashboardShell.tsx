import React from 'react';

/** Shared VERTEX-style dashboard tokens for NEXUS modules (PRISM, VERTEX, etc.) */
export const NEXUS_SHELL_PAGE =
  'min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 text-gray-100';
export const NEXUS_SHELL_PAD = 'p-8';
export const NEXUS_CONTAINER = 'max-w-7xl mx-auto space-y-6';
export const NEXUS_TITLE =
  'text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent';
export const NEXUS_SUBTITLE = 'text-gray-400 mt-1';
export const NEXUS_PANEL =
  'bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-purple-500/20';
export const NEXUS_PANEL_INNER = 'bg-gray-700/50 rounded-lg p-4';
export const NEXUS_BTN_PRIMARY =
  'px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:from-purple-500 hover:to-pink-500 transition-all font-semibold text-sm text-white';
export const NEXUS_BTN_SECONDARY =
  'px-4 py-2 bg-gray-800 text-gray-400 rounded-lg hover:bg-gray-700 transition-all font-medium text-sm';
export const NEXUS_TAB_ACTIVE =
  'bg-gradient-to-r from-purple-600 to-pink-600 text-white';
export const NEXUS_TAB_IDLE = 'bg-gray-800 text-gray-400 hover:bg-gray-700';

type Accent = 'purple' | 'red' | 'green' | 'yellow' | 'blue' | 'teal' | 'pink';

const ACCENT_BORDER: Record<Accent, string> = {
  purple: 'border-purple-500/20',
  red: 'border-red-500/20',
  green: 'border-green-500/20',
  yellow: 'border-yellow-500/20',
  blue: 'border-blue-500/20',
  teal: 'border-teal-500/20',
  pink: 'border-pink-500/20',
};

const ACCENT_TEXT: Record<Accent, string> = {
  purple: 'text-purple-400',
  red: 'text-red-400',
  green: 'text-green-400',
  yellow: 'text-yellow-400',
  blue: 'text-blue-400',
  teal: 'text-teal-400',
  pink: 'text-pink-400',
};

export const NexusMetricCard: React.FC<{
  label: string;
  value: number | string;
  icon?: string;
  accent?: Accent;
  sub?: string;
}> = ({ label, value, icon, accent = 'purple', sub }) => (
  <div
    className={`bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border ${ACCENT_BORDER[accent]}`}
  >
    <div className="flex items-center justify-between mb-2">
      <span className="text-gray-400 text-sm">{label}</span>
      {icon ? <span className="text-2xl">{icon}</span> : null}
    </div>
    <div className="text-3xl font-bold text-white">{value}</div>
    {sub ? <div className={`text-sm mt-1 ${ACCENT_TEXT[accent]}`}>{sub}</div> : null}
  </div>
);

export const NexusPanel: React.FC<{
  title: string;
  titleAccent?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ title, titleAccent, children, className = '' }) => (
  <div className={`${NEXUS_PANEL} ${className}`}>
    <h3 className={`text-xl font-bold mb-4 text-white ${titleAccent || ''}`}>{title}</h3>
    {children}
  </div>
);

export const NexusListRow: React.FC<{
  onClick?: () => void;
  children: React.ReactNode;
  accentBorder?: string;
}> = ({ onClick, children, accentBorder }) => {
  const Tag = onClick ? 'button' : 'div';
  return (
    <Tag
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      className={`w-full flex items-center gap-4 p-4 bg-gray-700/50 rounded-lg border border-gray-600/40 hover:bg-gray-700/70 transition-all text-left ${
        accentBorder ? `border-l-4 ${accentBorder}` : ''
      }`}
    >
      {children}
    </Tag>
  );
};
