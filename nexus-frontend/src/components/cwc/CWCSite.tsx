import React, { useState, useEffect, useCallback } from 'react';
import {
  MI_BRIDGES_PARTNER,
  MI_BRIDGES_HELP_DESK,
  MI_BRIDGES_CLIENT_FAQ,
  FAP_TOOLKIT,
  MI_BRIDGES_FAMILY_RESOURCES,
} from '../../data/cwcMiBridgesResources';

type Page = 'home' | 'about' | 'programs' | 'shield' | 'resources' | 'contact';

const movementKeyframes = `
@keyframes cwc-drift {
  0%, 100% { transform: translateX(0); }
  25%      { transform: translateX(6px) translateY(-1px); }
  50%      { transform: translateX(-4px) translateY(1px); }
  75%      { transform: translateX(3px); }
}
`;

const MovementWord: React.FC<{ color?: string; className?: string }> = ({ color, className = '' }) => (
  <span
    className={className}
    style={{
      display: 'inline-block',
      animation: 'cwc-drift 3.5s ease-in-out infinite',
      color: color || 'inherit',
    }}
  >
    movement.
  </span>
);

const YELLOW = '#F5C23E';
const YELLOW_PALE = '#FEF3D0';
const BLUE = '#1F3FAE';
const BLUE_DARK = '#142A7A';
const BLUE_DEEPER = '#0D1D5C';
const WHITE = '#FFFFFF';

const PROGRAMS = [
  {
    id: 'kids-in-comfort',
    name: 'Kids in Comfort',
    tagline: 'Every child deserves a safe space',
    description: 'Providing essential household items — beds, bedding, clothing, and personal care products — so children in transition have comfort and dignity.',
    icon: '🏠',
  },
  {
    id: 'forever-food-fund',
    name: 'Forever Food Fund',
    tagline: 'Feeding our community',
    description: 'Addressing food insecurity through partnerships with local food banks, community gardens, and direct meal distribution to families in need.',
    icon: '🍎',
  },
  {
    id: 'sole-purpose',
    name: 'Sole Purpose',
    tagline: 'One step at a time',
    description: 'Providing quality footwear to children and adults who need it. Because every journey starts with the right pair of shoes.',
    icon: '👟',
  },
  {
    id: 'haircuts-for-heroes',
    name: 'Hair Cuts for Heroes',
    tagline: 'Confidence starts here',
    description: 'Free haircuts and grooming services for children heading back to school, adults reentering the workforce, and veterans in our community.',
    icon: '💈',
  },
  {
    id: 'benefits-navigation',
    name: 'Benefits Navigation',
    tagline: 'MDHHS MI Bridges Community Partner',
    description: 'Official MI Bridges navigators help Michigan families apply for SNAP, Medicaid, cash assistance, childcare, and energy help — from account setup through approval. CWC has been an MDHHS Community Partner since May 2020.',
    icon: '📱',
  },
  {
    id: 'shield',
    name: 'SHIELD',
    tagline: 'Family Health & Safety Navigation',
    description: 'CWC navigators connect Michigan families to health screening, safe housing, emergency placement, benefits enrollment, and wraparound care — all coordinated through one system.',
    icon: '🛡️',
  },
];

const NAV_LINKS: { id: Page; label: string }[] = [
  { id: 'home', label: 'Home' },
  { id: 'about', label: 'About' },
  { id: 'programs', label: 'Programs' },
  { id: 'shield', label: 'SHIELD' },
  { id: 'resources', label: 'Resources' },
  { id: 'contact', label: 'Contact' },
];

type FamilyResource = {
  icon: string;
  title: string;
  desc: string;
  url: string;
  category: string;
  phone?: string;
};

const FAMILY_RESOURCES: FamilyResource[] = [
  { icon: '🏠', title: 'Apply for Home Lead Services', desc: 'Find out if your home qualifies for free lead inspection and repair.', url: 'https://www.michigan.gov/mileadsafe/lead-services/apply-for-home-lead-services', category: 'home' },
  { icon: '💧', title: 'Get Ahead of Lead', desc: 'Learn about Michigan\'s drinking water safety and lead prevention programs.', url: 'https://www.michigan.gov/mileadsafe/get-ahead-of-lead', category: 'home' },
  ...MI_BRIDGES_FAMILY_RESOURCES.filter(r => r.title !== 'Michigan 211'),
  { icon: '🍎', title: 'WIC — Nutrition for Families', desc: 'Healthy food and nutrition support for pregnant women, new moms, and young children.', url: 'https://www.michigan.gov/mdhhs/assistance-programs/wic', category: 'food' },
  { icon: '🏩', title: 'Housing Assistance', desc: 'Emergency housing, rental help, and affordable housing programs across Michigan.', url: 'https://www.michigan.gov/mshda', category: 'housing' },
  { icon: '🔥', title: 'Utility Bill Help (THAW)', desc: 'Struggling with heat or electric bills? THAW can help keep the lights on.', url: 'https://www.thawfund.org', category: 'housing' },
  { icon: '📞', title: 'Dial 211', desc: 'Free, confidential connection to local help — food, housing, health, and more. Available 24/7.', url: 'https://www.211.org', category: 'help' },
  { icon: '☠️', title: 'Poison Control', desc: 'If your child has been exposed to lead paint chips or any toxic substance, call immediately.', url: 'tel:1-800-222-1222', phone: '1-800-222-1222', category: 'help' },
  { icon: '🍽️', title: 'Find a Food Bank', desc: 'Locate free food distribution near you.', url: 'https://www.gcfb.org', category: 'food' },
  { icon: '💡', title: 'DTE Energy Assistance', desc: 'Low-income energy programs to help with your utility bills.', url: 'https://newlook.dteenergy.com/wps/wcm/connect/dte-web/home/billing-and-payments/payment-assistance', phone: '800-477-4747', category: 'housing' },
  { icon: '🥕', title: 'Forgotten Harvest', desc: 'Free food rescue and distribution across metro Detroit.', url: 'https://www.forgottenharvest.org', category: 'food' },
  { icon: '🏘️', title: 'Wayne Metro Emergency Help', desc: 'Emergency assistance for families in Wayne County — rent, utilities, and more.', url: 'https://www.waynemetro.org', phone: '313-388-9799', category: 'housing' },
  { icon: '🌐', title: 'MiSide', desc: 'Mental health, housing, Head Start, career services, veteran support, and more — all under one roof in Detroit.', url: 'https://miside.org/get-help', category: 'help' },
];

const TEAM = [
  { name: 'Dieasha D. Davis', title: 'Executive Director', bio: 'Founder of Cause We Care. Passionate about building systems that connect families to the resources they deserve.' },
  { name: 'Gary C. Felton Jr.', title: 'Director · U.S. Veteran', bio: 'Veteran leader bringing discipline, service, and heart to Cause We Care\'s mission. Dedicated to ensuring every family in our community has a champion in their corner.' },
];

const STATS = [
  { value: '500+', label: 'Families Served' },
  { value: '6', label: 'Active Programs' },
  { value: '50+', label: 'Benefits Applications' },
  { value: '2020', label: 'MI Bridges Partner' },
];

/** Home / Programs card click → page */
function programDestination(id: string): Page {
  if (id === 'shield') return 'shield';
  if (id === 'benefits-navigation') return 'resources';
  return 'programs';
}

export default function CWCSite() {
  const [page, setPage] = useState<Page>('home');
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    const metaDesc = document.querySelector('meta[name="description"]');
    const themeColor = document.querySelector('meta[name="theme-color"]');
    const prevTitle = document.title;
    const prevDesc = metaDesc?.getAttribute('content') ?? '';
    const prevTheme = themeColor?.getAttribute('content') ?? '';
    if (metaDesc) {
      metaDesc.setAttribute(
        'content',
        'Cause We Care — Michigan 501(c)(3). We connect families to food, housing, health navigation, education support, and community resources. Care. Navigate. Transform.',
      );
    }
    if (themeColor) themeColor.setAttribute('content', BLUE);
    return () => {
      document.title = prevTitle;
      if (metaDesc) metaDesc.setAttribute('content', prevDesc);
      if (themeColor) themeColor.setAttribute('content', prevTheme);
    };
  }, []);

  useEffect(() => {
    const label =
      page === 'home' ? 'Cause We Care' :
      page === 'about' ? 'About' :
      page === 'programs' ? 'Programs' :
      page === 'shield' ? 'SHIELD' :
      page === 'resources' ? 'Resources' :
      page === 'contact' ? 'Contact' : 'Cause We Care';
    document.title = page === 'home' ? `${label} | Michigan` : `${label} | Cause We Care`;
  }, [page]);

  const onNavigate = useCallback((p: Page) => {
    setPage(p);
    setMenuOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const headerSolid = scrollY > 60;

  return (
    <div className="min-h-screen" style={{ fontFamily: "'Inter', 'Segoe UI', system-ui, sans-serif" }}>
      <style>{movementKeyframes}</style>
      {/* NAV */}
      <nav
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
        style={{
          background: headerSolid ? BLUE : 'transparent',
          boxShadow: headerSolid ? '0 2px 20px rgba(0,0,0,.25)' : 'none',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            <button onClick={() => onNavigate('home')} className="flex items-center gap-3 group">
              <img src="/cwc-logo.png" alt="Cause We Care" className="h-10 sm:h-12 rounded-lg" />
              <div className="hidden sm:block">
                <div className="text-lg font-bold" style={{ color: YELLOW }}>CAUSE WE CARE</div>
                <div className="text-[10px] uppercase tracking-[.2em]" style={{ color: 'rgba(255,255,255,.7)' }}>501(c)(3) &middot; MI Bridges Community Partner</div>
              </div>
            </button>

            {/* Desktop nav */}
            <div className="hidden md:flex items-center gap-1">
              {NAV_LINKS.map(l => (
                <button
                  key={l.id}
                  onClick={() => onNavigate(l.id)}
                  className="px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200"
                  style={{
                    color: page === l.id ? BLUE : WHITE,
                    background: page === l.id ? YELLOW : 'transparent',
                  }}
                >
                  {l.label}
                </button>
              ))}
              <a
                href="https://givebutter.com/causewecare"
                target="_blank"
                rel="noopener noreferrer"
                className="ml-3 px-5 py-2.5 rounded-full text-sm font-bold transition-all duration-200 hover:scale-105"
                style={{ background: YELLOW, color: BLUE }}
              >
                Donate Now
              </a>
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden p-2 rounded-lg"
              style={{ color: YELLOW }}
            >
              <svg width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                {menuOpen ? (
                  <><line x1="6" y1="6" x2="22" y2="22"/><line x1="22" y1="6" x2="6" y2="22"/></>
                ) : (
                  <><line x1="4" y1="7" x2="24" y2="7"/><line x1="4" y1="14" x2="24" y2="14"/><line x1="4" y1="21" x2="24" y2="21"/></>
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden px-4 pb-4" style={{ background: BLUE }}>
            {NAV_LINKS.map(l => (
              <button
                key={l.id}
                onClick={() => onNavigate(l.id)}
                className="block w-full text-left px-4 py-3 rounded-lg text-base font-semibold mb-1"
                style={{
                  color: page === l.id ? BLUE : WHITE,
                  background: page === l.id ? YELLOW : 'transparent',
                }}
              >
                {l.label}
              </button>
            ))}
            <a
              href="https://givebutter.com/causewecare"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center mt-2 px-5 py-3 rounded-full text-base font-bold"
              style={{ background: YELLOW, color: BLUE }}
            >
              Donate Now
            </a>
          </div>
        )}
      </nav>

      {/* PAGE CONTENT */}
      {page === 'home' && <HomePage onNavigate={onNavigate} />}
      {page === 'about' && <AboutPage onNavigate={onNavigate} />}
      {page === 'programs' && <ProgramsPage onNavigate={onNavigate} />}
      {page === 'shield' && <ShieldPage />}
      {page === 'resources' && <ResourcesPage />}
      {page === 'contact' && <ContactPage />}

      {/* FOOTER */}
      <footer style={{ background: BLUE_DEEPER }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <img src="/cwc-logo.png" alt="Cause We Care" className="h-14 rounded-lg mb-4" />
              <p className="text-sm font-black tracking-wider uppercase mb-1" style={{ color: YELLOW }}>Care. Navigate. Transform.</p>
              <p className="text-[10px] italic mb-3" style={{ color: 'rgba(245,194,62,.5)' }}>More than a mission — a <MovementWord color="rgba(245,194,62,.7)" /></p>
              <p className="text-sm leading-relaxed" style={{ color: 'rgba(255,255,255,.6)' }}>
                Cause We Care is a 501(c)(3) nonprofit and MDHHS MI Bridges Community Partner serving families across Michigan. Your donation is tax-deductible to the fullest extent allowed by law.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-bold uppercase tracking-wider mb-4" style={{ color: YELLOW }}>Programs</h4>
              {PROGRAMS.map(p => (
                <button key={p.id} onClick={() => onNavigate('programs')} className="block text-sm mb-2 hover:underline" style={{ color: 'rgba(255,255,255,.7)' }}>
                  {p.icon} {p.name}
                </button>
              ))}
            </div>
            <div>
              <h4 className="text-sm font-bold uppercase tracking-wider mb-4" style={{ color: YELLOW }}>Contact</h4>
              <p className="text-sm mb-2" style={{ color: 'rgba(255,255,255,.7)' }}>T: 517.225.3950</p>
              <p className="text-sm mb-2" style={{ color: 'rgba(255,255,255,.7)' }}>E: info@cwecare.org</p>
              <p className="text-sm mb-4" style={{ color: 'rgba(255,255,255,.7)' }}>cwecare.org</p>
              <a
                href="/program-narrative"
                className="inline-block text-sm font-semibold mb-4 hover:underline"
                style={{ color: YELLOW }}
              >
                Program Infrastructure (Partners) →
              </a>
              <div className="flex gap-3">
                {[
                  { name: 'Facebook', url: 'https://www.facebook.com/cwecare.org' },
                  { name: 'Instagram', url: 'https://www.instagram.com/causewecarenpo' },
                  { name: 'LinkedIn', url: 'https://www.linkedin.com/company/cause-we-care-michigan' },
                ].map(s => (
                  <a key={s.name} href={s.url} target="_blank" rel="noopener noreferrer" className="w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold transition-all hover:scale-110" style={{ background: 'rgba(255,255,255,.1)', color: YELLOW }}>
                    {s.name[0]}
                  </a>
                ))}
              </div>
            </div>
          </div>
          <div className="mt-10 pt-6 border-t flex flex-col sm:flex-row items-center justify-between gap-4" style={{ borderColor: 'rgba(255,255,255,.1)' }}>
            <p className="text-xs" style={{ color: 'rgba(255,255,255,.4)' }}>&copy; {new Date().getFullYear()} Cause We Care. All rights reserved.</p>
            <p className="text-xs" style={{ color: 'rgba(255,255,255,.4)' }}>Powered by people who care.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   HOME PAGE
   ═══════════════════════════════════════════════════════════════════ */
function HomePage({ onNavigate }: { onNavigate: (p: Page) => void }) {
  return (
    <>
      {/* HERO */}
      <section
        className="relative min-h-[90vh] flex items-center justify-center overflow-hidden"
        style={{ background: `linear-gradient(135deg, ${BLUE_DARK} 0%, ${BLUE} 50%, ${BLUE_DEEPER} 100%)` }}
      >
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 rounded-full" style={{ background: YELLOW, filter: 'blur(120px)' }} />
          <div className="absolute bottom-20 right-10 w-96 h-96 rounded-full" style={{ background: YELLOW, filter: 'blur(160px)' }} />
        </div>
        <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider" style={{ background: 'rgba(245,194,62,.15)', color: YELLOW }}>
            501(c)(3) &middot; MI Bridges Community Partner &middot; Michigan
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-black leading-[1.05] mb-4" style={{ color: WHITE }}>
            Cause We Care,{' '}
            <span style={{ color: YELLOW }}>You Should Too.</span>
          </h1>
          <div className="mb-6">
            <p className="text-2xl sm:text-3xl font-black tracking-wide" style={{ color: YELLOW }}>Care. Navigate. Transform.</p>
            <p className="text-sm italic mt-1" style={{ color: 'rgba(245,194,62,.6)' }}>More than a mission — a <MovementWord color="rgba(245,194,62,.8)" /></p>
          </div>
          <p className="text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed" style={{ color: 'rgba(255,255,255,.75)' }}>
            We connect families to the resources they need — food security, safe housing, education essentials, health navigation, and community support. Because every family deserves someone in their corner.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => onNavigate('programs')}
              className="px-8 py-4 rounded-full text-base font-bold transition-all duration-200 hover:scale-105 shadow-lg"
              style={{ background: YELLOW, color: BLUE }}
            >
              Our Programs
            </button>
            <button
              onClick={() => onNavigate('shield')}
              className="px-8 py-4 rounded-full text-base font-bold transition-all duration-200 hover:scale-105 border-2"
              style={{ borderColor: YELLOW, color: YELLOW, background: 'transparent' }}
            >
              Refer a Family
            </button>
          </div>
        </div>
      </section>

      {/* STATS BAR */}
      <section style={{ background: YELLOW }}>
        <div className="max-w-5xl mx-auto px-4 py-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          {STATS.map(s => (
            <div key={s.label} className="text-center">
              <div className="text-3xl sm:text-4xl font-black" style={{ color: BLUE }}>{s.value}</div>
              <div className="text-sm font-semibold mt-1" style={{ color: BLUE_DARK }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* WHAT WE DO */}
      <section className="py-20" style={{ background: WHITE }}>
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-black mb-4" style={{ color: BLUE }}>What We Do</h2>
            <p className="text-lg max-w-2xl mx-auto" style={{ color: '#555' }}>
              Six programs, one mission: make sure no family faces hardship alone.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PROGRAMS.map(p => (
              <div
                key={p.id}
                className="relative rounded-2xl p-6 transition-all duration-300 hover:shadow-xl cursor-pointer group flex flex-col"
                style={{ background: '#F8F9FB', border: '1px solid #E8EBF0' }}
                onClick={() => onNavigate(programDestination(p.id))}
              >
                <div className="text-3xl mb-3">{p.icon}</div>
                <h3 className="text-lg font-bold mb-1" style={{ color: BLUE }}>{p.name}</h3>
                <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: '#999' }}>{p.tagline}</p>
                <p className="text-sm leading-relaxed flex-1" style={{ color: '#666' }}>{p.description}</p>
                <div className="mt-4 pt-4 border-t" style={{ borderColor: '#E8EBF0' }}>
                  <span className="text-sm font-bold group-hover:underline" style={{ color: BLUE }}>
                    {p.id === 'benefits-navigation' ? 'Get MI Bridges help →' : p.id === 'shield' ? 'Learn about SHIELD →' : 'Learn how you can help →'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW TO HELP */}
      <section className="py-20" style={{ background: YELLOW_PALE }}>
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl font-black mb-4" style={{ color: BLUE }}>How Can I Help?</h2>
            <p className="text-lg" style={{ color: BLUE_DARK }}>Cause We Care, You Should Too!</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { title: 'Volunteer', icon: '🤝', text: 'If you have the time and skills, consider volunteering to assist with organizing and distributing resources, coordinating shelter options, or providing emotional support.' },
              { title: 'Donate', icon: '💛', text: 'Your financial contributions, no matter the amount, can make a significant impact. Every donation brings us one step closer to reaching our goals.' },
              { title: 'Spread the Word', icon: '📢', text: 'Share our campaign across social media, emails, and community boards. The more people who know, the greater the support we can garner.' },
              { title: 'Sponsor', icon: '🏢', text: 'We welcome partnerships with businesses and corporations interested in supporting our cause. Your sponsorship makes a substantial difference.' },
            ].map(c => (
              <div key={c.title} className="rounded-2xl p-6 text-center transition-all duration-300 hover:shadow-lg hover:-translate-y-1" style={{ background: WHITE }}>
                <div className="text-4xl mb-4">{c.icon}</div>
                <h3 className="text-lg font-bold mb-3" style={{ color: BLUE }}>{c.title}</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#666' }}>{c.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* RESOURCES BANNER */}
      <section className="py-14" style={{ background: '#F8F9FB' }}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-2xl sm:text-3xl font-black mb-3" style={{ color: BLUE }}>Looking for Help?</h2>
          <p className="text-base mb-6" style={{ color: '#666' }}>
            We've gathered Michigan's most important family resources in one place — food, housing, health, utilities, and more. No sign-up needed.
          </p>
          <button
            onClick={() => onNavigate('resources')}
            className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105 shadow-md"
            style={{ background: YELLOW, color: BLUE }}
          >
            View All Resources
          </button>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16" style={{ background: BLUE }}>
        <div className="max-w-3xl mx-auto px-4 text-center">
          <p className="text-sm font-bold uppercase tracking-wider mb-2" style={{ color: 'rgba(245,194,62,.6)' }}>Care. Navigate. Transform.</p>
          <h2 className="text-3xl sm:text-4xl font-black mb-4" style={{ color: YELLOW }}>Ready to Make a Difference?</h2>
          <p className="text-lg mb-8" style={{ color: 'rgba(255,255,255,.7)' }}>
            Whether you volunteer an hour, donate a dollar, or share our story — you're helping a family in Michigan. More than a mission — a <MovementWord color="rgba(245,194,62,.8)" />
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a
              href="https://givebutter.com/causewecare"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105 shadow-lg"
              style={{ background: YELLOW, color: BLUE }}
            >
              Donate Now
            </a>
            <button
              onClick={() => onNavigate('contact')}
              className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105 border-2"
              style={{ borderColor: YELLOW, color: YELLOW }}
            >
              Get in Touch
            </button>
          </div>
        </div>
      </section>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   ABOUT PAGE
   ═══════════════════════════════════════════════════════════════════ */
function AboutPage({ onNavigate }: { onNavigate: (p: Page) => void }) {
  return (
    <>
      <section className="pt-28 pb-16" style={{ background: `linear-gradient(135deg, ${BLUE_DARK}, ${BLUE})` }}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl sm:text-5xl font-black mb-4" style={{ color: WHITE }}>About <span style={{ color: YELLOW }}>Cause We Care</span></h1>
          <p className="text-xl font-black tracking-wide mb-1" style={{ color: YELLOW }}>Care. Navigate. Transform.</p>
          <p className="text-sm italic" style={{ color: 'rgba(245,194,62,.6)' }}>More than a mission — a <MovementWord color="rgba(245,194,62,.8)" /></p>
        </div>
      </section>

      {/* OUR STORY */}
      <section className="py-16" style={{ background: WHITE }}>
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-black mb-6 text-center" style={{ color: BLUE }}>Our Story</h2>
          <div className="max-w-3xl mx-auto">
            <p className="text-lg leading-relaxed mb-6 text-center" style={{ color: '#555' }}>
              Cause We Care started with a simple question: <em>What if every family in crisis had someone in their corner?</em>
            </p>
            <p className="text-base leading-relaxed mb-6" style={{ color: '#555' }}>
              Founded in 2023, we saw too many families falling through the cracks — children sleeping on floors, parents choosing between groceries and rent, families displaced by unsafe housing with nowhere to turn. Government programs exist, but navigating them is overwhelming. Community resources are out there, but finding them takes time families don't have.
            </p>
            <p className="text-base leading-relaxed mb-6" style={{ color: '#555' }}>
              So we built something different. Not another referral list. Not another hotline. A hands-on, navigator-driven approach where real people walk with families through every step — from the first call to the final solution. We don't point fingers at problems. We solve them.
            </p>
            <p className="text-base leading-relaxed" style={{ color: '#555' }}>
              Today, Cause We Care operates six direct-service programs across Michigan, partnering with state agencies, healthcare systems, and community organizations to reach families who need us most. We're a 501(c)(3) nonprofit and official <strong>MDHHS MI Bridges Community Partner since {MI_BRIDGES_PARTNER.partnerSince}</strong> — our navigators help families apply for food assistance, Medicaid, cash, childcare, and more through MI Bridges.
            </p>
          </div>
        </div>
      </section>

      {/* MISSION & VISION */}
      <section className="py-16" style={{ background: '#F8F9FB' }}>
        <div className="max-w-5xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="rounded-2xl p-8" style={{ background: WHITE, border: '1px solid #E8EBF0' }}>
              <div className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl mb-6" style={{ background: YELLOW }}>🎯</div>
              <h2 className="text-2xl font-black mb-4" style={{ color: BLUE }}>Our Mission</h2>
              <p className="text-base leading-relaxed mb-4" style={{ color: '#555' }}>
                To connect Michigan families with the resources, support, and navigation they need to overcome hardship — without barriers, without judgment, and without delay.
              </p>
              <p className="text-base leading-relaxed" style={{ color: '#555' }}>
                We meet people where they are. We walk with them until the problem is solved. And we never stop fighting for their success.
              </p>
            </div>
            <div className="rounded-2xl p-8" style={{ background: WHITE, border: '1px solid #E8EBF0' }}>
              <div className="w-14 h-14 rounded-xl flex items-center justify-center text-2xl mb-6" style={{ background: YELLOW }}>🔮</div>
              <h2 className="text-2xl font-black mb-4" style={{ color: BLUE }}>Our Vision</h2>
              <p className="text-base leading-relaxed mb-4" style={{ color: '#555' }}>
                A Michigan where no family faces crisis alone. Where every child sleeps in a safe bed. Where every parent knows where their next meal is coming from. Where health hazards don't force families from their homes.
              </p>
              <p className="text-base leading-relaxed" style={{ color: '#555' }}>
                We envision a future where community care is the standard — not the exception.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* OUR VALUES */}
      <section className="py-16" style={{ background: BLUE }}>
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-3xl font-black mb-4 text-center" style={{ color: YELLOW }}>Our Values</h2>
          <p className="text-base text-center mb-12 max-w-2xl mx-auto" style={{ color: 'rgba(255,255,255,.7)' }}>
            These are not words on a wall. This is how we make decisions, every single day.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { 
                icon: '❤️', 
                title: 'Community First', 
                text: "Every decision we make starts with one question: what does the family need? Not what is convenient for us. Not what looks good on paper. What actually helps." 
              },
              { 
                icon: '🚪', 
                title: 'No Barriers', 
                text: "In the services we provide, we do not gatekeep resources. If you need help with something we offer, you get it — without unnecessary hoops, paperwork, or waiting periods." 
              },
              { 
                icon: '📊', 
                title: 'Accountability', 
                text: "Every program is tracked, measured, and improved. We use real data to drive real outcomes. If something is not working, we fix it. Period." 
              },
              { 
                icon: '🤝', 
                title: 'Dignity Always', 
                text: "We treat every family with the respect they deserve. Hardship does not define people — it is just a moment they are moving through. We are honored to help." 
              },
              { 
                icon: '💪', 
                title: 'Relentless Follow-Through', 
                text: "We do not hand someone a phone number and wish them luck. We stay with families from first contact to final resolution. We do not stop until the problem is solved." 
              },
              { 
                icon: '🌉', 
                title: 'Bridge Building', 
                text: "No organization can do it alone. We partner with state agencies, healthcare systems, businesses, and community groups to build networks that actually work." 
              },
            ].map(v => (
              <div key={v.title} className="rounded-2xl p-6" style={{ background: 'rgba(255,255,255,.1)' }}>
                <div className="text-3xl mb-4">{v.icon}</div>
                <h4 className="text-base font-bold mb-2" style={{ color: YELLOW }}>{v.title}</h4>
                <p className="text-sm leading-relaxed" style={{ color: 'rgba(255,255,255,.8)' }}>{v.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WHAT MAKES US DIFFERENT */}
      <section className="py-16" style={{ background: WHITE }}>
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-3xl font-black mb-8 text-center" style={{ color: BLUE }}>What Makes Us Different</h2>
          <div className="space-y-6">
            {[
              {
                title: 'We Navigate, Not Just Refer',
                text: "Most organizations give you a list of phone numbers. We give you a navigator — a real person who walks with you through every step, makes the calls with you, fills out the forms with you, and doesn't stop until you're taken care of."
              },
              {
                title: 'We Move Fast',
                text: "When a family is in crisis, they can't wait weeks for a committee to approve help. Our programs are designed for speed — getting resources in hands within days, not months."
              },
              {
                title: 'We Track Everything',
                text: "Every family, every service, every outcome is documented. Not for bureaucracy — for accountability. We know exactly who we've helped, how we helped them, and what happened next."
              },
              {
                title: 'We Partner Strategically',
                text: "We don't try to do everything ourselves. We build relationships with the best organizations in each space — so when a family needs specialized help, we know exactly who to call."
              },
            ].map((item, i) => (
              <div key={item.title} className="flex gap-4 items-start">
                <div className="w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center text-lg font-black" style={{ background: YELLOW, color: BLUE }}>
                  {i + 1}
                </div>
                <div>
                  <h4 className="text-lg font-bold mb-1" style={{ color: BLUE }}>{item.title}</h4>
                  <p className="text-base" style={{ color: '#555' }}>{item.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16" style={{ background: '#F8F9FB' }}>
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-black mb-8 text-center" style={{ color: BLUE }}>Leadership</h2>
          <div className="max-w-3xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-6">
            {TEAM.map(t => (
              <div key={t.name} className="rounded-2xl p-6 text-center" style={{ background: WHITE, border: '1px solid #E8EBF0' }}>
                <div className="w-20 h-20 rounded-full mx-auto mb-4 flex items-center justify-center text-2xl font-black" style={{ background: YELLOW, color: BLUE }}>
                  {t.name.split(' ').map(n => n[0]).join('')}
                </div>
                <h3 className="text-lg font-bold" style={{ color: BLUE }}>{t.name}</h3>
                <p className="text-sm font-semibold mb-3" style={{ color: YELLOW }}>{t.title}</p>
                <p className="text-sm" style={{ color: '#666' }}>{t.bio}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16" style={{ background: BLUE }}>
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-black mb-4" style={{ color: YELLOW }}>Partner With Us</h2>
          <p className="text-base mb-8" style={{ color: 'rgba(255,255,255,.7)' }}>
            Cause We Care partners with organizations across Michigan to deliver the programs our families depend on. If your agency, business, or community group wants to make a difference — let's talk.
          </p>
          <button onClick={() => onNavigate('contact')} className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105" style={{ background: YELLOW, color: BLUE }}>
            Get in Touch
          </button>
        </div>
      </section>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   PROGRAMS PAGE
   ═══════════════════════════════════════════════════════════════════ */
function ProgramsPage({ onNavigate }: { onNavigate: (p: Page) => void }) {
  return (
    <>
      <section className="pt-28 pb-16" style={{ background: `linear-gradient(135deg, ${BLUE_DARK}, ${BLUE})` }}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl sm:text-5xl font-black mb-4" style={{ color: WHITE }}>Our <span style={{ color: YELLOW }}>Programs</span></h1>
          <p className="text-lg" style={{ color: 'rgba(255,255,255,.7)' }}>Six initiatives, one mission: meet families where they are.</p>
        </div>
      </section>

      <section className="py-16" style={{ background: WHITE }}>
        <div className="max-w-5xl mx-auto px-4 space-y-8">
          {PROGRAMS.map((p, i) => (
            <div
              key={p.id}
              className="rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-xl"
              style={{ background: '#F8F9FB', border: '1px solid #E8EBF0' }}
            >
              <div className="flex flex-col md:flex-row items-stretch">
                <div className="md:w-24 flex items-center justify-center p-6 text-5xl" style={{ background: YELLOW_PALE }}>
                  {p.icon}
                </div>
                <div className="flex-1 p-6 md:p-8">
                  <h3 className="text-xl font-bold mb-1" style={{ color: BLUE }}>{p.name}</h3>
                  <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: '#999' }}>{p.tagline}</p>
                  <p className="text-sm leading-relaxed mb-4" style={{ color: '#666' }}>{p.description}</p>
                  <div className="flex flex-wrap gap-3">
                    {p.id === 'shield' ? (
                      <button onClick={() => onNavigate('shield')} className="px-5 py-2.5 rounded-full text-sm font-bold transition-all hover:scale-105" style={{ background: YELLOW, color: BLUE }}>
                        Learn More About SHIELD
                      </button>
                    ) : p.id === 'benefits-navigation' ? (
                      <>
                        <button onClick={() => onNavigate('resources')} className="px-5 py-2.5 rounded-full text-sm font-bold transition-all hover:scale-105" style={{ background: YELLOW, color: BLUE }}>
                          MI Bridges Resources
                        </button>
                        <a href="/refer" className="px-5 py-2.5 rounded-full text-sm font-bold transition-all hover:scale-105 border-2" style={{ borderColor: BLUE, color: BLUE, background: 'transparent' }}>
                          Request a Navigator
                        </a>
                      </>
                    ) : (
                      <button onClick={() => onNavigate('contact')} className="px-5 py-2.5 rounded-full text-sm font-bold transition-all hover:scale-105" style={{ background: YELLOW, color: BLUE }}>
                        Get Involved
                      </button>
                    )}
                    {p.id !== 'benefits-navigation' && (
                    <button onClick={() => onNavigate('contact')} className="px-5 py-2.5 rounded-full text-sm font-bold transition-all hover:scale-105 border-2" style={{ borderColor: BLUE, color: BLUE, background: 'transparent' }}>
                      Donate to This Cause
                    </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   SHIELD PAGE
   ═══════════════════════════════════════════════════════════════════ */
function ShieldPage() {
  const [openService, setOpenService] = useState<number | null>(null);

  const SERVICES = [
    {
      name: 'Blood Lead Level Testing',
      icon: '🩸',
      headline: 'It starts with one simple test — and we bring it to you.',
      story: "Every child in Michigan under the age of four is required to be tested for lead exposure. But for many families, finding time to get to a clinic is the hardest part. That is why we come to you. We send a certified technician directly to your home to perform a quick and painless blood draw — no clinic visit, no waiting room, no time off work. We schedule the test, we send the technician, and we make sure you get the results. One simple test can change everything.",
      who: 'We provide the mobile testing — a certified technician comes to your home at a time that works for you.',
      how: 'Your navigator schedules the mobile blood draw, our technician arrives at your door, performs the test, and results come directly to your navigator who follows up with next steps.',
    },
    {
      name: 'Case Management',
      icon: '📋',
      headline: 'When results come back elevated, we don\'t wait.',
      story: 'If a child\'s blood lead level comes back high, the state\'s prevention program kicks in. But the system is overwhelmed. Families get lost in paperwork, callbacks, and waiting lists. Our navigators step in to make sure the family is enrolled, the case is opened, and every follow-up happens on time. We become the family\'s advocate inside the system.',
      who: 'Our navigators make sure the family actually gets through the process.',
      how: 'We walk the family through every step, handle the forms, follow up on their behalf, and don\'t close the case until the child is safe.',
    },
    {
      name: 'NEMT Transportation',
      icon: '🚗',
      headline: 'When follow-up is needed, the ride is already handled.',
      story: "If a child's initial blood test comes back elevated, follow-up appointments are critical — specialist visits, confirmatory testing, developmental screenings. But a mom without a car, working two jobs, cannot take three buses with a toddler to get there. So she cancels. This happens every day across Michigan. When lead is found and follow-up care is needed, we make sure transportation is never the barrier. The ride shows up. The child gets the care they need. It is that simple.",
      who: 'Our team coordinates transportation for every follow-up appointment.',
      how: 'When elevated results require follow-up care, your navigator arranges the ride — door to door, no cost to the family, no appointments missed.',
    },
    {
      name: 'Lead Remediation',
      icon: '🔧',
      headline: 'We don\'t just find the problem — we fix the house.',
      story: 'When lead is found in a home — in the paint, the pipes, the soil — that family can\'t stay there safely. But finding the right contractor, understanding the inspection process, and navigating funding — it\'s overwhelming. We coordinate the entire remediation from inspection to clearance testing, so the family can come back to a home that\'s truly safe.',
      who: 'Certified contractors do the work. Our team manages the entire process.',
      how: 'Your navigator connects the family with contractors, coordinates inspections, tracks the timeline, and confirms the home passes clearance.',
    },
    {
      name: 'Housing Navigation',
      icon: '🏠',
      headline: 'When your home isn\'t safe, we find you somewhere that is.',
      story: 'During lead remediation, a family might need to leave their home for days or even weeks. Some families are already in unstable housing. We don\'t just say "good luck." We find temporary placement, coordinate with landlords, connect families to state and federal housing resources, and make sure nobody ends up on a couch or in a car while their home is being fixed.',
      who: 'Our navigators handle the search, the calls, and the coordination.',
      how: 'From emergency hotel placement during abatement to long-term housing support, your navigator stays with the family until they\'re settled.',
    },
    {
      name: 'Benefits Enrollment',
      icon: '📱',
      headline: 'Families shouldn\'t have to fight for help they qualify for.',
      story: 'Food assistance. Health coverage. Childcare. Energy assistance. Emergency relief. Michigan has programs for all of it — but the application process is confusing, time-consuming, and easy to mess up. Our navigators sit with the family, pull together the documents, walk through the applications, and don\'t stop until everything is submitted and approved. If a family qualifies, they should receive it. Period.',
      who: 'Our navigators handle the entire application process.',
      how: 'From gathering documents to submitting applications to following up on approvals — the navigator does the heavy lifting so the family doesn\'t have to.',
    },
    {
      name: 'Water Filter Safety Net',
      icon: '💧',
      headline: 'Clean water shouldn\'t be a luxury.',
      story: 'In homes with lead service lines or older plumbing, the water coming out of the tap may not be safe. Families shouldn\'t have to wonder. We deploy certified water filters, make sure they\'re installed correctly, set up replacement schedules, and track compliance — because a filter only works if it\'s maintained.',
      who: 'Our team deploys and maintains filters through state programs.',
      how: 'A navigator arranges installation, checks in on filter replacement, and makes sure the family has clean drinking water — not just once, but ongoing.',
    },
    {
      name: 'Community Health Worker Home Visits',
      icon: '🤝',
      headline: 'Sometimes the best thing you can do is show up.',
      story: 'A navigator walks into a home and sees what no intake form can capture — a broken window letting in cold air, empty shelves in the kitchen, a child sleeping on the floor. Our home visits aren\'t check-the-box wellness visits. They\'re real conversations with real families, identifying what\'s actually going on and connecting them to every resource available. That\'s how you build trust. That\'s how you change outcomes.',
      who: 'Our own trained community health navigators.',
      how: 'The navigator visits the home, assesses the full picture — environmental risks, social needs, barriers — and builds a personalized plan with the family.',
    },
    {
      name: 'Nurse Home Visits',
      icon: '👩‍⚕️',
      headline: 'When a family needs clinical eyes in the home.',
      story: 'Some situations need more than a navigator — they need a nurse. A child with elevated blood lead may need developmental screening. A parent may have health questions they\'re afraid to ask. Our nurse home visits bring clinical expertise directly to the family\'s door, in their space, on their terms. No waiting room. No judgment. Just care.',
      who: 'Licensed nurses — coordinated by our team.',
      how: 'When a navigator identifies a clinical need, a nurse visit is scheduled — in the home, at a time that works for the family.',
    },
  ];

  return (
    <>
      <section className="pt-28 pb-16" style={{ background: `linear-gradient(135deg, ${BLUE_DARK}, ${BLUE})` }}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 mb-4 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider" style={{ background: 'rgba(245,194,62,.15)', color: YELLOW }}>
            🛡️ Michigan Lead-Safe Initiative
          </div>
          <h1 className="text-4xl sm:text-5xl font-black mb-4" style={{ color: WHITE }}>
            <span style={{ color: YELLOW }}>SHIELD</span>
          </h1>
          <p className="text-lg mb-2" style={{ color: 'rgba(255,255,255,.9)' }}>Screening, Housing, Intake, Education, Lead Defense</p>
          <p className="text-sm font-bold mb-4" style={{ color: YELLOW }}>Every Family Deserves a SHIELD</p>
          <p className="text-base max-w-2xl mx-auto mb-8" style={{ color: 'rgba(255,255,255,.6)' }}>
            Our flagship program connects Michigan families to comprehensive health screening, remediation, and wraparound services — all in one coordinated system.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a href="/refer" className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105 shadow-lg" style={{ background: YELLOW, color: BLUE }}>
              I Need Help for My Family
            </a>
            <a href="/status" className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105 border-2" style={{ borderColor: YELLOW, color: YELLOW, background: 'transparent' }}>
              Check My Status
            </a>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16" style={{ background: WHITE }}>
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-2xl font-black mb-10 text-center" style={{ color: BLUE }}>How SHIELD Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { step: '01', title: 'Referral', text: 'A caseworker, health department, or family submits a referral through our secure intake portal.' },
              { step: '02', title: 'Navigator Assigned', text: 'A trained CWC Community Health Worker is assigned within 48 hours and contacts the family.' },
              { step: '03', title: 'Services Activated', text: 'Testing scheduled, transportation arranged, benefits enrolled, housing secured — whatever the family needs.' },
              { step: '04', title: 'Verified Complete', text: 'Every service is confirmed through two-way verification. Nothing slips through the cracks.' },
            ].map(s => (
              <div key={s.step} className="text-center">
                <div className="w-14 h-14 rounded-full mx-auto mb-4 flex items-center justify-center text-lg font-black" style={{ background: YELLOW, color: BLUE }}>{s.step}</div>
                <h3 className="text-base font-bold mb-2" style={{ color: BLUE }}>{s.title}</h3>
                <p className="text-sm" style={{ color: '#666' }}>{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 9 Service Lines */}
      <section className="py-16" style={{ background: '#F8F9FB' }}>
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-black mb-2 text-center" style={{ color: BLUE }}>9 Ways We Show Up</h2>
          <p className="text-center text-sm mb-10" style={{ color: '#999' }}>Click any service to hear the story behind it.</p>
          <div className="space-y-3">
            {SERVICES.map((s, i) => {
              const isOpen = openService === i;
              return (
                <div
                  key={i}
                  className="rounded-2xl overflow-hidden transition-all duration-300"
                  style={{ background: WHITE, border: isOpen ? `2px solid ${YELLOW}` : '1px solid #E8EBF0' }}
                >
                  <button
                    onClick={() => setOpenService(isOpen ? null : i)}
                    className="w-full flex items-center gap-4 p-5 text-left transition-all hover:bg-slate-50"
                  >
                    <div className="text-3xl shrink-0">{s.icon}</div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-base font-bold" style={{ color: BLUE }}>{s.name}</h4>
                      <p className="text-sm mt-0.5" style={{ color: isOpen ? BLUE : '#999' }}>{s.headline}</p>
                    </div>
                    <div
                      className="shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-transform duration-300"
                      style={{
                        background: isOpen ? YELLOW : '#F0F1F3',
                        color: isOpen ? BLUE : '#999',
                        transform: isOpen ? 'rotate(45deg)' : 'rotate(0deg)',
                      }}
                    >
                      +
                    </div>
                  </button>
                  {isOpen && (
                    <div className="px-5 pb-6 pt-0">
                      <div className="ml-[3.25rem] border-t pt-5" style={{ borderColor: '#E8EBF0' }}>
                        <p className="text-sm leading-relaxed mb-5" style={{ color: '#555' }}>
                          {s.story}
                        </p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="rounded-xl p-4" style={{ background: YELLOW_PALE }}>
                            <div className="text-[10px] uppercase tracking-wider font-bold mb-1.5" style={{ color: BLUE }}>Who does this?</div>
                            <p className="text-sm" style={{ color: '#555' }}>{s.who}</p>
                          </div>
                          <div className="rounded-xl p-4" style={{ background: YELLOW_PALE }}>
                            <div className="text-[10px] uppercase tracking-wider font-bold mb-1.5" style={{ color: BLUE }}>How does it work?</div>
                            <p className="text-sm" style={{ color: '#555' }}>{s.how}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Resources for families */}
      <section className="py-16" style={{ background: WHITE }}>
        <div className="max-w-4xl mx-auto px-4">
          <h2 className="text-2xl font-black mb-2 text-center" style={{ color: BLUE }}>Resources For You</h2>
          <p className="text-center text-sm mb-10" style={{ color: '#999' }}>You don't have to wait for us. These links connect you directly to Michigan programs you may qualify for.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FAMILY_RESOURCES.slice(0, 9).map(r => {
              const isPhone = r.url.startsWith('tel:');
              return (
              <a
                key={r.title}
                href={r.url}
                {...(!isPhone ? { target: '_blank', rel: 'noopener noreferrer' } as const : {})}
                className="rounded-2xl p-5 transition-all hover:shadow-lg hover:scale-[1.02] group flex flex-col"
                style={{ background: '#F8F9FB', border: '1px solid #E8EBF0' }}
              >
                <div className="text-2xl mb-2">{r.icon}</div>
                <h4 className="text-sm font-bold mb-1 group-hover:underline" style={{ color: BLUE }}>{r.title}</h4>
                <p className="text-xs leading-relaxed flex-1" style={{ color: '#666' }}>{r.desc}</p>
                {r.phone && <p className="text-xs font-bold mt-2" style={{ color: BLUE }}>{r.phone}</p>}
                <div className="mt-3 text-[10px] uppercase tracking-wider font-bold" style={{ color: YELLOW }}>{isPhone ? 'Call →' : 'Visit →'}</div>
              </a>
              );
            })}
          </div>
        </div>
      </section>

      {/* SHIELD Portals */}
      <section className="py-16" style={{ background: BLUE }}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-2xl font-black mb-3" style={{ color: YELLOW }}>Need Help? Start Here.</h2>
          <p className="text-sm mb-8" style={{ color: 'rgba(255,255,255,.6)' }}>Whether you're a family looking for support or a professional referring someone — we've got a door for you.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'I Need Help', href: '/refer', desc: 'Request services for your family' },
              { label: 'Check My Status', href: '/status', desc: 'See where your case stands' },
              { label: 'Submit a Referral', href: '/refer', desc: 'For agencies & professionals' },
              { label: 'Partner Portal', href: '/mdhhs', desc: 'For state & agency partners' },
            ].map(l => (
              <a
                key={l.label}
                href={l.href}
                className="block rounded-xl p-5 text-center transition-all hover:scale-105 hover:shadow-lg"
                style={{ background: BLUE_DARK }}
              >
                <div className="text-base font-bold mb-1" style={{ color: YELLOW }}>{l.label}</div>
                <div className="text-xs" style={{ color: 'rgba(255,255,255,.5)' }}>{l.desc}</div>
              </a>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   RESOURCES PAGE
   ═══════════════════════════════════════════════════════════════════ */
function ResourcesPage() {
  return (
    <>
      <section className="pt-28 pb-16" style={{ background: `linear-gradient(135deg, ${BLUE_DARK}, ${BLUE})` }}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl sm:text-5xl font-black mb-4" style={{ color: WHITE }}>
            Resources <span style={{ color: YELLOW }}>For You</span>
          </h1>
          <p className="text-lg max-w-2xl mx-auto" style={{ color: 'rgba(255,255,255,.7)' }}>
            Cause We Care is an official MI Bridges Community Partner. Use these links to apply for benefits, track your application, upload documents, and find help across Michigan.
          </p>
        </div>
      </section>

      {/* MI Bridges partner + client help */}
      <section className="py-14" style={{ background: YELLOW_PALE }}>
        <div className="max-w-5xl mx-auto px-4">
          <div className="rounded-2xl p-8 mb-10" style={{ background: WHITE, border: `2px solid ${YELLOW}` }}>
            <div className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: BLUE }}>MDHHS MI Bridges Community Partner</div>
            <h2 className="text-2xl font-black mb-3" style={{ color: BLUE }}>Need Help With Benefits?</h2>
            <p className="text-sm leading-relaxed mb-4" style={{ color: '#555' }}>
              Our navigators can sit with you, walk through MI Bridges applications, help upload documents, and follow up until your case is complete — food assistance, Medicaid, cash, childcare, and energy help.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <a href={MI_BRIDGES_PARTNER.clientPortal} target="_blank" rel="noopener noreferrer" className="px-6 py-3 rounded-full text-sm font-bold text-center transition-all hover:scale-105" style={{ background: YELLOW, color: BLUE }}>
                Open MI Bridges
              </a>
              <a href="/refer" className="px-6 py-3 rounded-full text-sm font-bold text-center transition-all hover:scale-105 border-2" style={{ borderColor: BLUE, color: BLUE }}>
                Ask a CWC Navigator for Help
              </a>
            </div>
            <p className="text-xs mt-4" style={{ color: '#888' }}>
              MI Bridges Help Desk: {MI_BRIDGES_HELP_DESK.phone} · TTY {MI_BRIDGES_HELP_DESK.tty} · {MI_BRIDGES_HELP_DESK.hours}
            </p>
          </div>

          <h3 className="text-lg font-black mb-4 text-center" style={{ color: BLUE }}>Common MI Bridges Questions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
            {MI_BRIDGES_CLIENT_FAQ.map(f => (
              <div key={f.q} className="rounded-xl p-5" style={{ background: WHITE, border: '1px solid #E8EBF0' }}>
                <h4 className="text-sm font-bold mb-2" style={{ color: BLUE }}>{f.q}</h4>
                <p className="text-sm leading-relaxed" style={{ color: '#666' }}>{f.a}</p>
              </div>
            ))}
          </div>

          <h3 className="text-lg font-black mb-4 text-center" style={{ color: BLUE }}>SNAP &amp; Food Assistance</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {FAP_TOOLKIT.filter(t => t.category !== 'staff').map(t => (
              <a key={t.title} href={t.url} target="_blank" rel="noopener noreferrer" className="rounded-xl p-5 transition-all hover:shadow-md group block" style={{ background: WHITE, border: '1px solid #E8EBF0' }}>
                <h4 className="text-sm font-bold mb-1 group-hover:underline" style={{ color: BLUE }}>{t.title}</h4>
                <p className="text-xs leading-relaxed" style={{ color: '#666' }}>{t.desc}</p>
              </a>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16" style={{ background: WHITE }}>
        <div className="max-w-5xl mx-auto px-4">
          <h2 className="text-2xl font-black mb-2 text-center" style={{ color: BLUE }}>All Michigan Resources</h2>
          <p className="text-sm text-center mb-10" style={{ color: '#888' }}>Food, housing, health, utilities, lead safety, and more.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FAMILY_RESOURCES.map(r => {
              const isPhone = r.url.startsWith('tel:');
              return (
              <a
                key={r.title}
                href={r.url}
                {...(!isPhone ? { target: '_blank', rel: 'noopener noreferrer' } as const : {})}
                className="rounded-2xl p-6 transition-all hover:shadow-lg hover:scale-[1.02] group flex flex-col"
                style={{ background: '#F8F9FB', border: '1px solid #E8EBF0' }}
              >
                <div className="text-3xl mb-3">{r.icon}</div>
                <h4 className="text-base font-bold mb-1 group-hover:underline" style={{ color: BLUE }}>{r.title}</h4>
                <p className="text-sm leading-relaxed flex-1" style={{ color: '#666' }}>{r.desc}</p>
                {r.phone && <p className="text-sm font-bold mt-3" style={{ color: BLUE }}>{r.phone}</p>}
                <div className="mt-4 text-xs uppercase tracking-wider font-bold" style={{ color: YELLOW }}>{isPhone ? 'Call →' : 'Visit →'}</div>
              </a>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-16" style={{ background: YELLOW_PALE }}>
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-2xl font-black mb-4" style={{ color: BLUE }}>Need More Help?</h2>
          <p className="text-base mb-6" style={{ color: '#555' }}>
            If you or your family needs support that goes beyond a single resource — we're here. Our navigators will sit with you, figure out what you need, and help you through every step.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <a href="/refer" className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105 shadow-lg" style={{ background: YELLOW, color: BLUE }}>
              Request Help for Your Family
            </a>
            <a href="/status" className="px-8 py-4 rounded-full text-base font-bold transition-all hover:scale-105 border-2" style={{ borderColor: BLUE, color: BLUE, background: 'transparent' }}>
              Check Your Case Status
            </a>
          </div>
        </div>
      </section>
    </>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   CONTACT PAGE
   ═══════════════════════════════════════════════════════════════════ */
function ContactPage() {
  const [form, setForm] = useState({ name: '', email: '', message: '' });
  const [sent, setSent] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSent(true);
  };

  return (
    <>
      <section className="pt-28 pb-16" style={{ background: `linear-gradient(135deg, ${BLUE_DARK}, ${BLUE})` }}>
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl sm:text-5xl font-black mb-4" style={{ color: WHITE }}>Get in <span style={{ color: YELLOW }}>Touch</span></h1>
          <p className="text-lg" style={{ color: 'rgba(255,255,255,.7)' }}>We'd love to hear from you.</p>
        </div>
      </section>

      <section className="py-16" style={{ background: WHITE }}>
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-1 md:grid-cols-2 gap-12">
          <div>
            <h2 className="text-2xl font-black mb-6" style={{ color: BLUE }}>Contact Information</h2>
            <div className="space-y-4 mb-8">
              <div className="flex items-start gap-3">
                <span className="text-xl">📞</span>
                <div>
                  <div className="text-sm font-bold" style={{ color: BLUE }}>Phone</div>
                  <div className="text-sm" style={{ color: '#666' }}>517.225.3950</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">📧</span>
                <div>
                  <div className="text-sm font-bold" style={{ color: BLUE }}>Email</div>
                  <div className="text-sm" style={{ color: '#666' }}>info@cwecare.org</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">🌐</span>
                <div>
                  <div className="text-sm font-bold" style={{ color: BLUE }}>Website</div>
                  <div className="text-sm" style={{ color: '#666' }}>cwecare.org</div>
                </div>
              </div>
            </div>
            <div className="flex gap-3 mb-8">
              {[
                { name: 'Facebook', url: 'https://www.facebook.com/cwecare.org' },
                { name: 'Instagram', url: 'https://www.instagram.com/causewecarenpo' },
                { name: 'LinkedIn', url: 'https://www.linkedin.com/company/cause-we-care-michigan' },
              ].map(s => (
                <a key={s.name} href={s.url} target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold transition-all hover:scale-110" style={{ background: YELLOW_PALE, color: BLUE }}>
                  {s.name[0]}
                </a>
              ))}
            </div>
            <div className="rounded-2xl p-6" style={{ background: YELLOW_PALE }}>
              <h3 className="text-base font-bold mb-2" style={{ color: BLUE }}>Tax-Deductible Donations</h3>
              <p className="text-sm leading-relaxed mb-4" style={{ color: '#666' }}>
                CAUSE WE CARE is a 501(c)(3) nonprofit and MDHHS MI Bridges Community Partner (EIN 92-3602670). Your donation is tax-deductible to the fullest extent allowed by law.
              </p>
              <div className="space-y-2">
                {[
                  { label: 'Givebutter', url: 'https://givebutter.com/causewecare', icon: '💛', primary: true },
                  { label: 'Kids in Comfort Campaign', url: 'https://givebutter.com/kidsincomfort', icon: '🏠', primary: false },
                  { label: 'Haircuts for Heroes Campaign', url: 'https://givebutter.com/haircutsforheroes', icon: '💈', primary: false },
                ].map(d => (
                  <a
                    key={d.label}
                    href={d.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition-all hover:scale-[1.02]"
                    style={{
                      background: d.primary ? YELLOW : WHITE,
                      color: BLUE,
                      border: d.primary ? 'none' : '1px solid #E8EBF0',
                    }}
                  >
                    <span className="text-lg">{d.icon}</span>
                    <span className="flex-1">{d.label}</span>
                    <span style={{ color: '#999' }}>&rarr;</span>
                  </a>
                ))}
              </div>
              <p className="text-[11px] mt-3 text-center" style={{ color: '#999' }}>
                All donations processed securely through Givebutter.
              </p>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-black mb-6" style={{ color: BLUE }}>Send Us a Message</h2>
            {sent ? (
              <div className="rounded-2xl p-8 text-center" style={{ background: YELLOW_PALE }}>
                <div className="text-4xl mb-4">💛</div>
                <h3 className="text-xl font-bold mb-2" style={{ color: BLUE }}>Thank You!</h3>
                <p className="text-sm" style={{ color: '#666' }}>We received your message and will get back to you soon.</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-bold mb-1" style={{ color: BLUE }}>Name</label>
                  <input
                    type="text"
                    required
                    value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2"
                    style={{ borderColor: '#E8EBF0', '--tw-ring-color': YELLOW } as React.CSSProperties}
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold mb-1" style={{ color: BLUE }}>Email</label>
                  <input
                    type="email"
                    required
                    value={form.email}
                    onChange={e => setForm({ ...form, email: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2"
                    style={{ borderColor: '#E8EBF0', '--tw-ring-color': YELLOW } as React.CSSProperties}
                    placeholder="you@email.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold mb-1" style={{ color: BLUE }}>Message</label>
                  <textarea
                    required
                    rows={5}
                    value={form.message}
                    onChange={e => setForm({ ...form, message: e.target.value })}
                    className="w-full px-4 py-3 rounded-xl text-sm border focus:outline-none focus:ring-2 resize-none"
                    style={{ borderColor: '#E8EBF0', '--tw-ring-color': YELLOW } as React.CSSProperties}
                    placeholder="How can we help?"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full py-3.5 rounded-full text-base font-bold transition-all hover:scale-[1.02]"
                  style={{ background: YELLOW, color: BLUE }}
                >
                  Send Message
                </button>
              </form>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
