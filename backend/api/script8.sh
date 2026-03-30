# Install Node.js on EC2
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y

# Create React app
cd ~/cloudpilot/frontend
npx create-react-app . --template cra-template
npm install recharts axios

# Replace src/App.js with CloudPilot dashboard
cat > ~/cloudpilot/frontend/src/App.js << 'EOF'
import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const API = `http://${window.location.hostname}:8000`;

export default function App() {
  const [health, setHealth] = useState(null);
  const [recs, setRecs]     = useState([]);

  useEffect(() => {
    fetch(`${API}/health`).then(r=>r.json()).then(setHealth);
    fetch(`${API}/api/recommendations`).then(r=>r.json()).then(d=>setRecs(d.recommendations||[]));
  }, []);

  return (
    <div style={{background:'#0d1117',minHeight:'100vh',color:'#e6edf3',fontFamily:'monospace',padding:'24px'}}>
      <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:32}}>
        <span style={{fontSize:36}}>☁</span>
        <div>
          <h1 style={{margin:0,color:'#58a6ff',fontSize:28}}>CloudPilot</h1>
          <p style={{margin:0,color:'#8b949e',fontSize:13}}>AI-Powered Cloud Cost Optimization</p>
        </div>
        <span style={{marginLeft:'auto',background:'#1e4620',color:'#3fb950',padding:'4px 12px',borderRadius:20,fontSize:12}}>
          ● {health?.status || 'connecting...'}
        </span>
      </div>

      <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:16,marginBottom:32}}>
        {[
          {label:'Monthly Spend',    value:'$122',  sub:'this month',    color:'#58a6ff'},
          {label:'Potential Savings',value:'$127',  sub:'identified',    color:'#3fb950'},
          {label:'Auto-Fixable',     value:'3',     sub:'recommendations',color:'#f78166'},
        ].map(c=>(
          <div key={c.label} style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20}}>
            <div style={{color:'#8b949e',fontSize:12,marginBottom:8}}>{c.label}</div>
            <div style={{color:c.color,fontSize:32,fontWeight:700}}>{c.value}</div>
            <div style={{color:'#8b949e',fontSize:12}}>{c.sub}</div>
          </div>
        ))}
      </div>

      <div style={{background:'#161b22',border:'1px solid #30363d',borderRadius:12,padding:20}}>
        <h2 style={{color:'#58a6ff',marginTop:0,fontSize:16}}>🤖 AI Recommendations</h2>
        {recs.length === 0
          ? <p style={{color:'#8b949e'}}>No recommendations yet. Cost data is being collected...</p>
          : recs.map(r=>(
            <div key={r.id} style={{background:'#0d1117',border:'1px solid #30363d',borderRadius:8,padding:16,marginBottom:12}}>
              <div style={{display:'flex',justifyContent:'space-between'}}>
                <span style={{color:'#e6edf3',fontWeight:600}}>{r.resource}</span>
                <span style={{color:'#3fb950',fontWeight:700}}>${r.monthly_saving}/mo saved</span>
              </div>
              <div style={{color:'#8b949e',fontSize:13,marginTop:6}}>{r.reason}</div>
              <div style={{marginTop:10}}>
                <button style={{background:'#1f6feb',color:'#fff',border:'none',borderRadius:6,padding:'6px 16px',cursor:'pointer',fontSize:12}}>
                  ⚡ Apply Fix
                </button>
              </div>
            </div>
          ))
        }
      </div>
    </div>
  );
}
EOF

# Run React dev server
npm start
