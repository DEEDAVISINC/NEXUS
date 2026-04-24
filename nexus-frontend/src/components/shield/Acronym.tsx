import React from 'react';

/**
 * SHIELD acronym — three variants, one name.
 *
 *   operations — internal navigator view; what the system does for staff.
 *   mission    — public / family-facing; child welfare emphasis.
 *   compliance — MDHHS / grants / auditor; formal process framing.
 *
 * Layout:
 *   inline — single row ("Support · Health · Intake · Enrollment · Linkage · Delivery")
 *   grid   — six columns, big letter + word underneath (brand moment)
 */

export type AcronymVariant = 'operations' | 'mission' | 'compliance';

export const SHIELD_ACRONYMS: Record<AcronymVariant, { label: string; words: [string, string, string, string, string, string] }> = {
  operations: { label: 'Operations', words: ['Support',   'Health', 'Intake', 'Enrollment', 'Linkage', 'Delivery'] },
  mission:    { label: 'Mission',    words: ['Screening', 'Health', 'Intake', 'Early',      'Lead',    'Defense']  },
  compliance: { label: 'Compliance', words: ['Screening', 'Health', 'Intake', 'Enrollment', 'Linkage', 'Defense']  },
};

const LETTERS: [string, string, string, string, string, string] = ['S', 'H', 'I', 'E', 'L', 'D'];

interface AcronymProps {
  variant: AcronymVariant;
  layout?: 'inline' | 'grid';
  letterClass?: string;
  wordClass?: string;
  dividerClass?: string;
  className?: string;
}

const SHIELDAcronym: React.FC<AcronymProps> = ({
  variant,
  layout = 'inline',
  letterClass,
  wordClass,
  dividerClass = 'text-slate-500',
  className = '',
}) => {
  const { words } = SHIELD_ACRONYMS[variant];

  if (layout === 'grid') {
    return (
      <div className={`grid grid-cols-6 gap-2 ${className}`}>
        {LETTERS.map((letter, i) => (
          <div key={i} className="text-center">
            <div className={letterClass ?? 'text-2xl md:text-3xl font-black text-[#f5c23e] leading-none'}>{letter}</div>
            <div className={wordClass ?? 'text-[10px] md:text-xs uppercase tracking-wider font-bold text-[#1f3fae] mt-1'}>
              {words[i]}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`flex flex-wrap items-center gap-x-1.5 gap-y-0.5 ${className}`}>
      {words.map((word, i) => (
        <React.Fragment key={i}>
          <span className={wordClass ?? 'text-[10px] uppercase tracking-wider font-bold text-[#8ea2d6]'}>
            <span className={letterClass ?? 'text-[#f5c23e]'}>{word.charAt(0)}</span>
            {word.slice(1)}
          </span>
          {i < words.length - 1 && <span className={`text-[10px] ${dividerClass}`}>·</span>}
        </React.Fragment>
      ))}
    </div>
  );
};

export default SHIELDAcronym;
