/**
 * src/components/shared/CompanyFilterBar.tsx
 *
 * Company focus selector shown on every page.
 * Lets the user type a company name to filter all signals on the current page.
 * Reads from / writes to CompanyContext so the filter persists across tab switches.
 */

import { useState, useEffect } from 'react';
import { Building2, X, Search } from 'lucide-react';
import { useCompany } from '../../context/CompanyContext';
import { fetchCompanies } from '../../api/client';
import type { Company } from '../../types';

interface CompanyFilterBarProps {
  /** Optional label override (e.g. "Filter by Company" vs "Focus Company") */
  label?: string;
}

export function CompanyFilterBar({ label = 'Focus Company' }: CompanyFilterBarProps) {
  const { focusedCompany, setFocusedCompany } = useCompany();
  const [query, setQuery] = useState('');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [open, setOpen] = useState(false);

  // Load companies whenever query changes
  useEffect(() => {
    if (!query.trim()) {
      setCompanies([]);
      setOpen(false);
      return;
    }
    let cancelled = false;
    fetchCompanies()
      .then((all) => {
        if (cancelled) return;
        const filtered = all.filter((c) =>
          c.name.toLowerCase().includes(query.toLowerCase())
        );
        setCompanies(filtered.slice(0, 8));
        setOpen(filtered.length > 0);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [query]);

  const selectCompany = (company: Company) => {
    setFocusedCompany(company);
    setQuery(company.name);
    setOpen(false);
  };

  const clearFocus = () => {
    setFocusedCompany(null);
    setQuery('');
    setOpen(false);
  };

  return (
    <div className="relative flex items-center gap-2">
      {/* Label */}
      <div className="flex items-center gap-1.5 text-xs text-slate-500 font-mono shrink-0">
        <Building2 className="w-3.5 h-3.5" />
        <span>{label}:</span>
      </div>

      {/* Input */}
      <div className="relative">
        <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-slate-500 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type company name"
          className="bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-8 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 font-mono w-52 transition-all"
        />
        {(query || focusedCompany) && (
          <button
            onClick={clearFocus}
            className="absolute right-2 top-1.5 text-slate-500 hover:text-slate-300 transition-colors"
            aria-label="Clear company filter"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Active badge */}
      {focusedCompany && (
        <span className="px-2 py-0.5 bg-brand-500/20 border border-brand-500/40 rounded text-[10px] font-mono text-brand-400 shrink-0">
          Filtering: {focusedCompany.name}
        </span>
      )}

      {/* Dropdown */}
      {open && companies.length > 0 && (
        <div className="absolute top-full left-16 mt-1 w-64 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl z-50 overflow-hidden">
          {companies.map((company) => (
            <button
              key={company.id}
              onClick={() => selectCompany(company)}
              className="w-full text-left px-3 py-2 text-xs font-mono text-slate-300 hover:bg-slate-800 hover:text-white flex items-center gap-2 transition-colors"
            >
              <Building2 className="w-3 h-3 text-brand-400 shrink-0" />
              {company.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
