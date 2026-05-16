/**
 * components/dashboard/CompanyList.tsx
 * Sidebar list of all tracked companies.
 */

import { useEffect, useState } from 'react';
import { Building2 } from 'lucide-react';
import type { Company } from '../../types';
import { fetchCompanies } from '../../api/client';

interface Props {
  onSelect: (company: Company) => void;
  selectedName: string | null;
}

export function CompanyList({ onSelect, selectedName }: Props) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCompanies()
      .then(setCompanies)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-sm text-slate-500 p-4">Loading companies…</p>;
  }

  if (companies.length === 0) {
    return (
      <div className="p-4 text-center">
        <p className="text-sm text-slate-500">No companies analyzed yet.</p>
        <p className="text-xs text-slate-600 mt-1">Run your first analysis above.</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <p className="text-xs text-slate-500 uppercase tracking-widest font-mono px-2 mb-3">
        Tracked Companies
      </p>
      {companies.map((c) => (
        <button
          key={c.id}
          onClick={() => onSelect(c)}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
            selectedName === c.name
              ? 'bg-brand-500/20 text-brand-400'
              : 'text-slate-300 hover:bg-surface-100'
          }`}
        >
          <Building2 className="w-4 h-4 shrink-0" />
          <div className="min-w-0">
            <p className="font-medium text-sm truncate">{c.name}</p>
            {c.ats_platform && (
              <p className="text-xs text-slate-500 font-mono">{c.ats_platform}</p>
            )}
          </div>
        </button>
      ))}
    </div>
  );
}
