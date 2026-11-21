import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Cloud, LayoutDashboard, Server, Workflow, Play, RefreshCw, XCircle, ShieldCheck, Settings, Activity, BarChart3 } from 'lucide-react';
import './style.css';

const H = () => ({ 'Content-Type': 'application/json', 'X-Role': localStorage.role || 'operator', 'X-Tenant': 'demo' });
async function api(p: string, o: any = {}) { let r = await fetch(p, { ...o, headers: H() }); let d = await r.json(); if (!r.ok) throw Error(d.detail); return d; }

function App() {
  const [page, setPage] = useState('Dashboard');
  const [resources, setResources] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [metrics, setMetrics] = useState('');
  const [audit, setAudit] = useState<any[]>([]);
  const [role, setRole] = useState(localStorage.role || 'operator');
  const [msg, setMsg] = useState('');
  const load = () => Promise.all([api('/api/resources'), api('/api/jobs')]).then(([r, j]) => { setResources(r); setJobs(j); });
  const loadMetrics = () => api('/api/metrics').then(setMetrics);
  const loadAudit = () => api('/api/audit').then(setAudit);
  useEffect(() => { load(); loadMetrics(); }, []);
  async function add(kind: string, priority: string = 'normal', metadata: string = '') {
    try {
      let url = `/api/jobs/${kind}?max_attempts=3&idempotency_key=${kind}-${Date.now()}&priority=${encodeURIComponent(priority)}`;
      if (metadata) url += `&metadata=${encodeURIComponent(metadata)}`;
      await api(url, { method: 'POST' });
      setMsg('Job queued');
      load();
    } catch (e: any) { setMsg(e.message) }
  }
  async function run() { await api('/api/worker/run-one', { method: 'POST' }).catch((e: any) => setMsg(e.message)); load(); }
  async function cancel(id: string) { await api(`/api/jobs/${id}/cancel`, { method: 'POST' }).catch((e: any) => setMsg(e.message)); load(); }
  let nav = [['Dashboard', LayoutDashboard], ['Inventory', Server], ['Workers', Workflow], ['Analytics', Activity], ['Settings', Settings]];
  return (
    <div className="shell">
      <aside>
        <div className="brand"><Cloud />PeaCloud <small>v0.17</small></div>
        {nav.map(([n, I]: any) => <button key={n} className={page === n ? 'on' : ''} onClick={() => setPage(n)}><I size={18} />{n}</button>)}
      </aside>
      <main>
        <header>
          <div><h1>{page}</h1><p>Multi-cloud operations and resilient job processing</p></div>
          <select value={role} onChange={(e) => { setRole(e.target.value); localStorage.role = e.target.value }}><option>viewer</option><option>operator</option><option>admin</option></select>
        </header>
        {msg && <div className="msg">{msg}</div>}
        {page === 'Dashboard' && <div className="cards"><article><span>Resources</span><b>{resources.length}</b></article><article><span>Running</span><b>{resources.filter((x) => x.state === 'running').length}</b></article><article><span>Queued jobs</span><b>{jobs.filter((x) => x.status === 'queued').length}</b></article><article><span>Dead letters</span><b>{jobs.filter((x) => x.status === 'dead_letter').length}</b></article></div>}
        {page === 'Inventory' && <section><div className="title"><h2>Resource inventory</h2><button onClick={load}><RefreshCw size={15} /> Refresh</button></div>{resources.map((x) => <div className="row"><span>{x.name}</span><span className={x.state}>{x.state}</span><span>{x.provider}</span><span>{x.type}</span><span>{x.region}</span></div>)}</section>}
        {page === 'Workers' && (
          <section>
            <div className="title"><h2>Job workers</h2><button onClick={run}><Play size={15} /> Run one job</button></div>
            {jobs.map((x) => <div className="job" key={x.id}><span>{x.kind}</span><span className={x.status}>{x.status}</span><span>{x.attempts}/{x.max_attempts}</span>{x.status === 'queued' && <button onClick={() => cancel(x.id)}><XCircle size={14} /></button>}</div>)}
            <div className="job">
              <label>Enqueue job</label>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <select id="kind" style={{ padding: '6px' }}><option>diagnostic</option><option>inventory-refresh</option><option>discovery</option><option>test-fail</option></select>
                <select id="priority" style={{ padding: '6px' }}><option>normal</option><option>high</option><option>low</option></select>
                <input id="metadata" placeholder="metadata JSON" style={{ padding: '6px', flex: 1 }} />
                <button onClick={() => { const k = (document.getElementById('kind') as HTMLSelectElement).value; const p = (document.getElementById('priority') as HTMLSelectElement).value; const m = (document.getElementById('metadata') as HTMLInputElement).value; add(k, p, m); }}><Play size={15} /> Queue</button>
              </div>
            </div>
          </section>
        )}
        {page === 'Analytics' && (
          <section>
            <div className="title"><h2>Observability</h2><button onClick={loadMetrics}><RefreshCw size={15} /> Refresh metrics</button></div>
            <h3>Prometheus metrics</h3>
            <pre className="metrics">{metrics}</pre>
            {role === 'admin' && (
              <div style={{ marginTop: 24 }}>
                <div className="title"><h2>Audit trail</h2><button onClick={loadAudit}><RefreshCw size={15} /> Load audit</button></div>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead><tr><th style={{ textAlign: 'left', padding: '8px' }}>Time</th><th style={{ textAlign: 'left', padding: '8px' }}>User</th><th style={{ textAlign: 'left', padding: '8px' }}>Action</th><th style={{ textAlign: 'left', padding: '8px' }}>Resource</th><th style={{ textAlign: 'left', padding: '8px' }}>Details</th></tr></thead>
                  <tbody>{audit.map((e, i) => (<tr key={i}><td style={{ padding: '6px' }}>{new Date(e.timestamp * 1000).toLocaleString()}</td><td style={{ padding: '6px' }}>{e.user}</td><td style={{ padding: '6px' }}>{e.action}</td><td style={{ padding: '6px' }}>{e.resource}</td><td style={{ padding: '6px', fontSize: 12, color: '#555' }}>{JSON.stringify(e.details)}</td></tr>))}</tbody>
                </table>
              </div>
            )}
          </section>
        )}
        {page === 'Settings' && <section><div className="title"><h2>Settings</h2></div><p style={{ color: '#666' }}>Version 0.17.0 - Observability, audit logging and job priorities added.</p></section>}
      </main>
    </div>
  );
}

const root = createRoot(document.getElementById('root')!);
root.render(<App />);