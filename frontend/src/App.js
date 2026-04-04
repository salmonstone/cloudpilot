import { useState, useEffect } from 'react';

const API = 'http://www.pilotcost.online';

export default function App() {
  const [health, setHealth]     = useState(null);
  const [recs, setRecs]         = useState([]);
  const [costs, setCosts]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = () => {
    fetch(`${API}/health`)
      .then(r => r.json()).then(setHealth).catch(() => setHealth(null));

    fetch(`${API}/api/recommendations`)
      .then(r => r.json())
      .then(d => { setRecs(d.recommendations || []); setLoading(false); })
      .catch(() => setLoading(false));

    fetch(`${API}/api/costs/summary`)
      .then(r => r.json())
      .then(d => setCosts(d.costs || [])).catch(() => {});
  };

  const refreshData = async () => {
    setRefreshing(true);
    await fetch(`${API}/api/recommendations/refresh`, { method: 'POST' });
    setTimeout(() => { fetchData(); setRefreshing(false); }, 2000);
  };

  useEffect(() => { fetchData(); }, []);

  const totalSaving = recs.reduce((s, r) => s + (parseFloat(r.monthly_saving) || 0), 0);

  return (
    <div style={{background:'#0d1117',minHeight:'100vh',color:'#e6edf3',fontFamily:'monospace',padding:'24px'}}>

      {/* Header */}
      <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:32,borderBottom:'1px solid #30363d',paddingBottom:16}}>
        <span style={{fontSize:36}}>☁</span>
        <div>
          <h1 style={{margin:0,color:'#58a6ff',fontSize:28}}>CloudPilot</h1>
          <p style={{margin:0,color:'#8b949e',fontSize:13}}>AI-Powered Cloud Cost Optimization — pilotcost.online</p>
        </div>
        <span style={{marginLeft:'auto',background:health?'#1e4620':'#2d1f1f',color:health?'#3fb950':'#f78166',padding:'4px 16px',borderRadius:20,fontSize:12}}>
          {health ? '● Online' : '● Offline'}
        </span>
      </div>

      {/* Stats */}
      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:16,marginBottom:32}}>
        <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20}}>
          <div style={{color:'#8b949e',fontSize:12,marginBottom:8}}>Total Potential Savings</div>
          <div style={{color:'#3fb950',fontSize:36,fontWeight:700}}>${totalSaving.toFixed(2)}</div>
          <div style={{color:'#8b949e',fontSize:12}}>per month — AI identified</div>
        </div>
        <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20}}>
          <div style={{color:'#8b949e',fontSize:12,marginBottom:8}}>Recommendations</div>
          <div style={{color:'#58a6ff',fontSize:36,fontWeight:700}}>{recs.length}</div>
          <div style={{color:'#8b949e',fontSize:12}}>issues found</div>
        </div>
        <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20}}>
          <div style={{color:'#8b949e',fontSize:12,marginBottom:8}}>Auto-Fixable</div>
          <div style={{color:'#f78166',fontSize:36,fontWeight:700}}>
            {recs.filter(r => r.auto_fixable).length}
          </div>
          <div style={{color:'#8b949e',fontSize:12}}>one-click fixes</div>
        </div>
      </div>

      {/* Recommendations */}
      <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20,marginBottom:24}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
          <h2 style={{color:'#58a6ff',margin:0,fontSize:16}}>🤖 AI Recommendations — live from backend</h2>
          <button
            onClick={refreshData}
            disabled={refreshing}
            style={{background:'#1f6feb',color:'#fff',border:'none',borderRadius:6,padding:'6px 16px',cursor:'pointer',fontSize:12,fontFamily:'monospace'}}
          >
            {refreshing ? '⏳ Refreshing...' : '🔄 Refresh AI'}
          </button>
        </div>

        {loading && <p style={{color:'#8b949e'}}>⏳ Loading...</p>}
        {!loading && recs.length === 0 && <p style={{color:'#8b949e'}}>No recommendations yet.</p>}

        {recs.map(r => (
          <div key={r.id} style={{background:'#0d1117',border:'1px solid #30363d',borderRadius:8,padding:16,marginBottom:12}}>
            <div style={{display:'flex',justifyContent:'space-between'}}>
              <span style={{color:'#e6edf3',fontWeight:600}}>{r.resource}</span>
              <span style={{color:'#3fb950',fontWeight:700}}>${parseFloat(r.monthly_saving).toFixed(2)}/mo</span>
            </div>
            <div style={{color:'#58a6ff',fontSize:12,marginTop:4}}>{r.current} → {r.suggested}</div>
            <div style={{color:'#8b949e',fontSize:13,marginTop:4}}>{r.reason}</div>
            <button
              style={{marginTop:10,background:'#1f6feb',color:'#fff',border:'none',borderRadius:6,padding:'6px 18px',cursor:'pointer',fontSize:12}}
              onClick={() => alert(`Fix queued for ${r.resource}!\nSaving: $${r.monthly_saving}/mo`)}
            >
              ⚡ Apply Fix — Save ${r.monthly_saving}/mo
            </button>
          </div>
        ))}
      </div>

      {/* Cost Breakdown */}
      <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20,marginBottom:24}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:12}}>
          <h2 style={{color:'#58a6ff',margin:0,fontSize:16}}>💰 AWS Cost Breakdown</h2>
          <button
            onClick={fetchData}
            style={{background:'#161b22',color:'#8b949e',border:'1px solid #30363d',borderRadius:6,padding:'4px 12px',cursor:'pointer',fontSize:11}}
          >
            🔄 Refresh
          </button>
        </div>
        {costs.length === 0
          ? <p style={{color:'#8b949e',fontSize:13}}>⏳ Fetching cost data...</p>
          : costs.map((c,i) => (
            <div key={i} style={{display:'flex',justifyContent:'space-between',padding:'8px 0',borderBottom:'1px solid #21262d'}}>
              <span style={{color:'#e6edf3',fontSize:13}}>{c.service}</span>
              <span style={{color:'#f78166',fontWeight:600}}>${c.cost}/mo</span>
            </div>
          ))
        }
      </div>

      {/* Backend Status */}
      <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20}}>
        <h2 style={{color:'#58a6ff',marginTop:0,fontSize:16}}>🔌 Backend Status</h2>
        <pre style={{color:'#3fb950',fontSize:13,margin:0}}>
          {health ? JSON.stringify(health, null, 2) : '⏳ Connecting...'}
        </pre>
      </div>

    </div>
  );
}
