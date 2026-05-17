/**
 * src/context/CompanyContext.tsx
 *
 * Global company focus context.
 * All pages read from this context to filter signals by the focused company.
 * Use `useCompany()` to access and set the focused company from any page.
 */

import { createContext, useContext, useState, ReactNode } from 'react';
import type { Company } from '../types';

interface CompanyContextValue {
  /** The currently focused company (null = show all) */
  focusedCompany: Company | null;
  /** Update the focused company */
  setFocusedCompany: (company: Company | null) => void;
  /** Company name string for easy access */
  focusedCompanyName: string | null;
}

const CompanyContext = createContext<CompanyContextValue | null>(null);

/** Wrap your page tree with this provider */
export function CompanyProvider({ children }: { children: ReactNode }) {
  const [focusedCompany, setFocusedCompany] = useState<Company | null>(null);

  return (
    <CompanyContext.Provider
      value={{
        focusedCompany,
        setFocusedCompany,
        focusedCompanyName: focusedCompany?.name ?? null,
      }}
    >
      {children}
    </CompanyContext.Provider>
  );
}

/** Hook to access the company context from any page/component */
export function useCompany(): CompanyContextValue {
  const ctx = useContext(CompanyContext);
  if (!ctx) throw new Error('useCompany must be used inside <CompanyProvider>');
  return ctx;
}
