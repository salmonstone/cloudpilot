import { useState, useEffect } from 'react';

const API = "http://3.110.143.63:8000";

export default function App() {
  const [health, setHealth]   = useState(null);
  const [recs, setRecs]       = useState([]);
  const [costs, setCosts]     = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch health
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(setHealth)
      .catch(() => setHealth(null));

    // Fetch recommendations from YOUR API
    fetch(`${API}/api/recommendations`)
      .then(r => r.json())
      .then(d => { setRecs(d.recommendations || []); setLoading(false); })
      .catch(() => setLoading(false));

    // Fetch costs from YOUR API
    fetch(`${API}/api/costs/summary`)
      .then(r => r.json())
      .then(d => { setCosts(d.costs || []); })
      .catch(() => {});
  }, []);

  const totalSaving = recs.reduce((sum, r) => sum + (parseFloat(r.monthly_saving) || 0), 0);

  return (
    <div style={{background:'#0d1117',minHeight:'100vh',color:'#e6edf3',fontFamily:'monospace',padding:'24px'}}>

      {/* Header */}
      <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:32,borderBottom:'1px solid #30363d',paddingBottom:16}}>
        <span style={{fontSize:36}}>☁</span>
        <div>
          <h1 style={{margin:0,color:'#58a6ff',fontSize:28}}>CloudPilot</h1>
          <p style={{margin:0,color:'#8b949e',fontSize:13}}>AI-Powered Cloud Cost Optimization</p>
        </div>
        <span style={{marginLeft:'auto',background:health?'#1e4620':'#2d1f1f',color:health?'#3fb950':'#f78166',padding:'4px 16px',borderRadius:20,fontSize:12}}>
          {health ? '● Online' : '● Offline'}
        </span>
      </div>

      {/* Stats — REAL data from API */}
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

      {/* Recommendations — REAL data from API */}
      <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20,marginBottom:24}}>
        <h2 style={{color:'#58a6ff',marginTop:0,fontSize:16,marginBottom:16}}>
          🤖 AI Recommendations
          <span style={{color:'#8b949e',fontSize:12,fontWeight:400,marginLeft:8}}>
            — live from your backend
          </span>
        </h2>

        {loading && <p style={{color:'#8b949e'}}>⏳ Loading recommendations...</p>}

        {!loading && recs.length === 0 &&
          <p style={{color:'#8b949e'}}>No recommendations yet. Cost data collecting...</p>
        }

        {recs.map(r => (
          <div key={r.id} style={{background:'#0d1117',border:'1px solid #30363d',borderRadius:8,padding:16,marginBottom:12}}>
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <span style={{color:'#e6edf3',fontWeight:600,fontSize:14}}>{r.resource}</span>
              <span style={{color:'#3fb950',fontWeight:700}}>${parseFloat(r.monthly_saving).toFixed(2)}/mo</span>
            </div>
            <div style={{color:'#58a6ff',fontSize:12,marginTop:4}}>
              {r.current} → {r.suggested}
            </div>
            <div style={{color:'#8b949e',fontSize:13,marginTop:4}}>{r.reason}</div>
            <div style={{display:'flex',gap:8,marginTop:10,alignItems:'center'}}>
              <button
                style={{background:'#1f6feb',color:'#fff',border:'none',borderRadius:6,padding:'6px 18px',cursor:'pointer',fontSize:12,fontFamily:'monospace'}}
                onClick={() => alert(`Fix queued for ${r.resource}!\nSaving: $${r.monthly_saving}/mo`)}
              >
                ⚡ Apply Fix
              </button>
              <span style={{color:'#8b949e',fontSize:11}}>
                Confidence: {Math.round((r.confidence||0)*100)}%
                {r.auto_fixable ? ' ✅ Auto-fixable' : ' ⚠️ Manual review needed'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Cost Breakdown — REAL data from API */}
      <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20,marginBottom:24}}>
        <h2 style={{color:'#58a6ff',marginTop:0,fontSize:16,marginBottom:12}}>
          💰 AWS Cost Breakdown
        </h2>
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

      {/* Backend health */}
      <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20}}>
        <h2 style={{color:'#58a6ff',marginTop:0,fontSize:16,marginBottom:12}}>🔌 Backend Status</h2>
        <pre style={{color:'#3fb950',fontSize:13,margin:0}}>
          {health ? JSON.stringify(health, null, 2) : '⏳ Connecting...'}
        </pre>
      </div>

    </div>
  );
}
