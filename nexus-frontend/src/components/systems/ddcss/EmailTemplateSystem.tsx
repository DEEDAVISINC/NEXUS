import React, { useState, useEffect, useCallback } from 'react';
import { api } from '../../../api/client';

/**
 * DDCSS — Email Template Generator (HTML + placeholders, company_info-backed).
 * Categories and variants are loaded from GET /email-templates/categories.
 */

type Variant = { key: string; label: string };
type Category = { key: string; label: string; variants: Variant[] };

export const EmailTemplateSystem: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [category, setCategory] = useState('mco_hide_snp');
  const [variant, setVariant] = useState('cold_outreach');
  const [recipientFirstName, setRecipientFirstName] = useState('');
  const [planDisplayName, setPlanDisplayName] = useState('HAP CareSource MI Health Link');
  const [customParagraph, setCustomParagraph] = useState('');
  const [subject, setSubject] = useState('');
  const [html, setHtml] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copyOk, setCopyOk] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await api.getEmailTemplateCategories();
        if (!cancelled && res.categories?.length) {
          setCategories(res.categories);
          const first = res.categories[0];
          setCategory(first.key);
          if (first.variants?.length) setVariant(first.variants[0].key);
        }
      } catch {
        if (!cancelled) setCategories([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const currentVariants = categories.find((c) => c.key === category)?.variants ?? [];

  const generate = useCallback(async () => {
    setLoading(true);
    setError(null);
    setCopyOk(false);
    try {
      const res = await api.generateEmailTemplate({
        category,
        variant,
        recipientFirstName: recipientFirstName.trim() || undefined,
        planDisplayName: planDisplayName.trim() || undefined,
        customParagraph: customParagraph.trim() || undefined,
      });
      if (!res.success) {
        setError(res.error || 'Generation failed');
        setHtml('');
        setSubject('');
        return;
      }
      setHtml(res.html || '');
      setSubject(res.subject || '');
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Request failed');
      setHtml('');
      setSubject('');
    } finally {
      setLoading(false);
    }
  }, [category, variant, recipientFirstName, planDisplayName, customParagraph]);

  const copyHtml = () => {
    if (!html) return;
    void navigator.clipboard.writeText(html).then(() => {
      setCopyOk(true);
      setTimeout(() => setCopyOk(false), 2000);
    });
  };

  const copySubject = () => {
    if (!subject) return;
    void navigator.clipboard.writeText(subject).then(() => {
      setCopyOk(true);
      setTimeout(() => setCopyOk(false), 2000);
    });
  };

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-indigo-700/50">
      <h3 className="text-2xl font-bold mb-2 text-indigo-300">📧 Email Templates (DDCSS)</h3>
      <p className="text-gray-400 text-sm mb-6">
        Generated HTML uses <code className="text-indigo-400">company_info.py</code> for DDI credentials. Each category offers: Cold Outreach, Warm Follow Up, Inbound Response.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Category</label>
          <select
            value={category}
            onChange={(e) => {
              const next = e.target.value;
              setCategory(next);
              const cat = categories.find((c) => c.key === next);
              if (cat?.variants?.length) setVariant(cat.variants[0].key);
            }}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
          >
            {categories.length === 0 ? (
              <option value="mco_hide_snp">MCO — MI Health Link / HIDE SNP</option>
            ) : (
              categories.map((c) => (
                <option key={c.key} value={c.key}>
                  {c.label}
                </option>
              ))
            )}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Version</label>
          <select
            value={variant}
            onChange={(e) => setVariant(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
          >
            {(currentVariants.length ? currentVariants : [
              { key: 'cold_outreach', label: 'Cold Outreach' },
              { key: 'warm_follow_up', label: 'Warm Follow Up' },
              { key: 'inbound_response', label: 'Inbound Response' },
            ]).map((v) => (
              <option key={v.key} value={v.key}>
                {v.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-3 mb-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Recipient first name</label>
          <input
            value={recipientFirstName}
            onChange={(e) => setRecipientFirstName(e.target.value)}
            placeholder="Dana"
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Plan / program display name</label>
          <input
            value={planDisplayName}
            onChange={(e) => setPlanDisplayName(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Optional extra paragraph</label>
          <textarea
            value={customParagraph}
            onChange={(e) => setCustomParagraph(e.target.value)}
            rows={3}
            placeholder="Additional context (inserted at {{CUSTOM_PARAGRAPH}})"
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-sm"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        <button
          type="button"
          onClick={() => void generate()}
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 px-4 py-2 rounded-lg text-sm font-semibold"
        >
          {loading ? 'Generating…' : 'Generate'}
        </button>
        {subject && (
          <button type="button" onClick={copySubject} className="bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded-lg text-sm">
            Copy subject
          </button>
        )}
        {html && (
          <button type="button" onClick={copyHtml} className="bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded-lg text-sm">
            {copyOk ? 'Copied' : 'Copy HTML'}
          </button>
        )}
      </div>

      {error && <div className="text-red-400 text-sm mb-4">{error}</div>}

      {subject && (
        <div className="mb-2 text-sm">
          <span className="text-gray-500">Suggested subject: </span>
          <span className="text-gray-200">{subject}</span>
        </div>
      )}

      {html && (
        <div className="border border-gray-600 rounded-lg overflow-hidden bg-white">
          <iframe title="Email preview" srcDoc={html} className="w-full min-h-[320px] border-0" sandbox="allow-same-origin" />
        </div>
      )}
    </div>
  );
};

export default EmailTemplateSystem;
