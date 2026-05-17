import { useState } from 'react';
import { ArrowUpRight, Building2, LayoutDashboard, Menu, Search, Send, X } from 'lucide-react';
import { CompanyProvider, useCompany } from '../context/CompanyContext';
import { CompanyFilterBar } from '../components/shared/CompanyFilterBar';
import { SignalDetailDrawer } from '../components/shared/SignalDetailDrawer';
import type { DrawerSignal } from '../components/shared/SignalDetailDrawer';
import { CommandCenter } from '../components/pages/CommandCenter';
import { AccountsIntelligence } from '../components/pages/AccountsIntelligence';
import { OpportunitiesPipeline } from '../components/pages/OpportunitiesPipeline';
import { SignalsExplorer } from '../components/pages/SignalsExplorer';
import { OutreachCenter } from '../components/pages/OutreachCenter';
import type { Company } from '../types';

type TabId = 'command_center' | 'accounts' | 'opportunities' | 'signals' | 'outreach';

const NAV_ITEMS: { id: TabId; label: string; Icon: typeof LayoutDashboard }[] = [
  { id: 'command_center', label: 'Command Center', Icon: LayoutDashboard },
  { id: 'accounts', label: 'Accounts Intel', Icon: Building2 },
  { id: 'opportunities', label: 'Opportunities', Icon: ArrowUpRight },
  { id: 'signals', label: 'Signals Explorer', Icon: Search },
  { id: 'outreach', label: 'Outreach & Action', Icon: Send },
];

export function DashboardPage() {
  return (
    <CompanyProvider>
      <DashboardShell />
    </CompanyProvider>
  );
}

function DashboardShell() {
  const { focusedCompany, setFocusedCompany } = useCompany();
  const [activeTab, setActiveTab] = useState<TabId>('command_center');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [selectedSignal, setSelectedSignal] = useState<DrawerSignal | null>(null);

  const handleNavigate = (tab: string, company?: Company) => {
    setActiveTab(tab as TabId);
    if (company) {
      setSelectedCompany(company);
      setFocusedCompany(company);
    }
  };

  const activeCompany = focusedCompany ?? selectedCompany;
  const activeLabel = NAV_ITEMS.find(item => item.id === activeTab)?.label ?? 'Command Center';

  return (
    <div className="min-h-screen flex bg-slate-950 text-slate-100 font-sans">
      <aside className={`${sidebarOpen ? 'w-72' : 'w-20'} hidden md:flex flex-col border-r border-slate-800 bg-slate-900/70 backdrop-blur-md transition-all duration-200 shrink-0`}>
        <div className="h-16 px-4 flex items-center gap-3 border-b border-slate-800">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-accent flex items-center justify-center text-white font-display font-bold text-base shadow-lg shadow-brand-500/20">OI</div>
          {sidebarOpen && (
            <div className="min-w-0">
              <span className="font-display font-bold text-white tracking-tight text-lg block leading-none">Opportunity Intel</span>
              <span className="text-[10px] text-slate-500 font-mono tracking-wider uppercase mt-0.5 block">Pipeline Orchestrator</span>
            </div>
          )}
        </div>

        <button onClick={() => setSidebarOpen(open => !open)} className="mx-4 mt-4 p-2 rounded-lg border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition-colors self-start" title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}>
          {sidebarOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
        </button>

        <nav className="p-4 space-y-2">
          {NAV_ITEMS.map(({ id, label, Icon }) => (
            <TabButton key={id} active={activeTab === id} label={label} Icon={Icon} expanded={sidebarOpen} onClick={() => handleNavigate(id)} />
          ))}
        </nav>
      </aside>

      <div className="flex-1 min-w-0 flex flex-col">
        <header className="h-auto min-h-16 border-b border-slate-800 px-4 md:px-6 py-3 flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between shrink-0 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
          <div className="flex items-center gap-3">
            <button onClick={() => setSidebarOpen(open => !open)} className="md:hidden p-2 rounded-lg border border-slate-800 text-slate-400 hover:text-white">
              <Menu className="w-4 h-4" />
            </button>
            <div>
              <span className="font-display font-bold text-white tracking-tight text-lg block leading-none">{activeLabel}</span>
              <span className="text-[10px] text-slate-500 font-mono tracking-wider uppercase mt-0.5 block">Company-scoped intelligence</span>
            </div>
          </div>
          <CompanyFilterBar />
          {sidebarOpen && (
            <nav className="md:hidden grid grid-cols-1 gap-2 pt-2 border-t border-slate-800">
              {NAV_ITEMS.map(({ id, label, Icon }) => (
                <TabButton key={id} active={activeTab === id} label={label} Icon={Icon} expanded onClick={() => handleNavigate(id)} />
              ))}
            </nav>
          )}
        </header>

        <main className="flex-1 overflow-y-auto p-6 md:p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'command_center' && <CommandCenter onNavigate={handleNavigate} />}
          {activeTab === 'accounts' && (
            <AccountsIntelligence
              selectedCompany={activeCompany}
              onSelectCompany={setSelectedCompany}
              onSelectSignal={setSelectedSignal}
            />
          )}
          {activeTab === 'opportunities' && <OpportunitiesPipeline onSelectSignal={setSelectedSignal} />}
          {activeTab === 'signals' && <SignalsExplorer onSelectSignal={setSelectedSignal} />}
          {activeTab === 'outreach' && <OutreachCenter />}
        </main>
      </div>

      <SignalDetailDrawer signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
    </div>
  );
}

interface TabButtonProps {
  active: boolean;
  label: string;
  Icon: typeof LayoutDashboard;
  expanded: boolean;
  onClick: () => void;
}

function TabButton({ active, label, Icon, expanded, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full px-3 py-2.5 rounded-lg text-xs font-semibold font-mono flex items-center gap-3 transition-all duration-200 ${
        active ? 'bg-brand-500 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
      }`}
      title={expanded ? undefined : label}
    >
      <Icon className="w-4 h-4 shrink-0" />
      {expanded && <span className="truncate">{label}</span>}
    </button>
  );
}
