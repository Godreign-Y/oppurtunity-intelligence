import { useEffect, useState } from 'react';
import { getPipelineRuns } from '../../api/client';
import type { PipelineRun } from '../../types';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';

export function PipelineRunsList({ companyName, onSelectRun }: { companyName: string, onSelectRun: (run: PipelineRun) => void }) {
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let interval: number;
    
    const fetchRuns = async () => {
      try {
        const fetched = await getPipelineRuns(companyName);
        setRuns(fetched);
      } catch (e) {
        console.error("Failed to fetch pipeline runs", e);
      }
    };
    
    setLoading(true);
    fetchRuns().finally(() => setLoading(false));

    interval = window.setInterval(fetchRuns, 3000); // Poll every 3 seconds
    return () => window.clearInterval(interval);
  }, [companyName]);

  if (loading && runs.length === 0) return <div className="text-slate-400 p-4"><Loader2 className="animate-spin inline" /> Loading runs...</div>;
  if (runs.length === 0) return <div className="text-slate-400 p-4">No pipeline runs yet. Start one above.</div>;

  return (
    <div className="mt-8">
      <h3 className="font-display text-lg font-bold text-white mb-4">Recent Pipeline Runs for {companyName}</h3>
      <div className="space-y-3">
        {runs.map(run => (
          <div key={run.id} 
            className="p-4 bg-surface-50 border border-slate-700 rounded-lg cursor-pointer hover:border-brand-500 transition-colors"
            onClick={() => {
              if (run.status === 'completed' || run.status === 'failed') {
                onSelectRun(run);
              }
            }}
          >
            <div className="flex justify-between items-center mb-2">
              <span className="font-mono text-xs text-slate-400">{new Date(run.created_at).toLocaleString()}</span>
              <span className={`text-xs px-2 py-1 rounded-full flex items-center gap-1 ${
                run.status === 'completed' ? 'bg-emerald-900/50 text-emerald-400' :
                run.status === 'failed' ? 'bg-red-900/50 text-red-400' :
                run.status === 'running' ? 'bg-blue-900/50 text-blue-400' :
                'bg-slate-800 text-slate-300'
              }`}>
                {run.status === 'completed' && <CheckCircle className="w-3 h-3" />}
                {run.status === 'failed' && <XCircle className="w-3 h-3" />}
                {run.status === 'running' && <Loader2 className="w-3 h-3 animate-spin" />}
                {run.status === 'pending' && <Clock className="w-3 h-3" />}
                {run.status.toUpperCase()}
              </span>
            </div>
            <div className="text-sm text-slate-300">
              Pipelines: {run.pipelines_selected.join(', ')}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
