/** Deep-link query params for NEXUS Command Center (App.tsx reads on load). */
export const NEXUS_ROUTES = {
  landing: '/',
  nova: '/?view=opportunity-hunter',
  ddcssHideSnpRevenue: '/?view=ddcss&tab=hide-snp-revenue',
  prismNemtRevenue: '/?view=prism&division=transport&section=revenue',
  gpss: '/?view=gpss',
  prism: '/?view=prism',
  vertex: '/?view=vertex',
} as const;

export type NexusDeepLink = {
  view: string;
  tab?: string;
  division?: string;
  section?: string;
};

export function buildNexusPath(link: NexusDeepLink): string {
  const params = new URLSearchParams();
  params.set('view', link.view);
  if (link.tab) params.set('tab', link.tab);
  if (link.division) params.set('division', link.division);
  if (link.section) params.set('section', link.section);
  return `/?${params.toString()}`;
}
