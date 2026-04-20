import React, { useState, useEffect } from 'react';
import { Play, Pause, FastForward, SkipForward, Server } from 'lucide-react';
import Renderer from './components/Renderer';
import Charts from './components/Charts';

function App() {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [selectedScenario, setSelectedScenario] = useState('world_v1.json');
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  const [state, setState] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [fullStats, setFullStats] = useState<any[]>([]);
  const [paused, setPaused] = useState(false);
  const [speed, setSpeed] = useState(0.05);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');

  useEffect(() => {
    fetch('http://localhost:8000/api/scenarios')
      .then(r => r.json())
      .then(data => setScenarios(data.scenarios))
      .catch(e => console.error("API not running", e));
  }, []);

  const connect = () => {
    if (ws) ws.close();
    setHistory([]);
    setFullStats([]);
    setState(null);
    setConnectionStatus('Connecting...');
    
    const socket = new WebSocket(`ws://localhost:8000/api/simulate?config=${selectedScenario}`);
    
    socket.onopen = () => setConnectionStatus('Connected (Live)');
    socket.onclose = () => {
      setConnectionStatus('Disconnected');
      setWs(null);
      setPaused(false);
    };
    
    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'init' || data.type === 'tick') {
        const globalEnergy = Math.round(data.agents.reduce((a: number, b: any) => a + b.energy, 0));
        setState(data);
        setHistory(prev => [...prev.slice(-200), data]); // keep last 200 ticks for charts

        setFullStats(prev => [...prev, {
          tick: data.tick,
          weather: data.weather,
          population: data.population,
          animalPopulation: data.animals?.length || 0,
          globalEnergy: globalEnergy,
          factions: JSON.stringify(data.factions || {})
        }]);
      }
    };
    
    setWs(socket);
    setPaused(false);
  };

  const disconnect = () => {
    if (ws) ws.close();
    setWs(null);
    setConnectionStatus('Disconnected');
  };

  const sendCommand = (cmd: string, extra?: any) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action: cmd, ...extra }));
    }
  };

  const togglePause = () => {
    if (paused) {
      sendCommand('play');
      setPaused(false);
    } else {
      sendCommand('pause');
      setPaused(true);
    }
  };

  const handleSpeed = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = parseFloat(e.target.value);
    setSpeed(val);
    sendCommand('speed', { delay: val });
  };

  const exportReport = () => {
    if (fullStats.length === 0) return;
    
    // Dynamically identify all unique factions spawned over the entire simulation
    const factionSet = new Set<string>();
    fullStats.forEach(stat => {
      const fObj = JSON.parse(stat.factions);
      Object.keys(fObj).forEach(k => factionSet.add(k));
    });
    const factionNames = Array.from(factionSet);
    
    let csv = `Tick,Season,Population,Animal_Population,Global_Energy,${factionNames.map(f => `${f}_Pop`).join(',')}\n`;
    fullStats.forEach(stat => {
      const fObj = JSON.parse(stat.factions);
      const factionCols = factionNames.map(name => fObj[name] || 0).join(',');
      csv += `${stat.tick},${stat.weather},${stat.population},${stat.animalPopulation},${stat.globalEnergy},${factionCols}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Aether-1-Report-${selectedScenario}-${new Date().getTime()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#58a6ff', margin: '0 0 20px 0' }}>
            <Server size={24} />
            Aether-1 Engine
          </h1>
          <div style={{ color: connectionStatus.includes('Connected') ? '#44ff44' : '#ff4444', fontSize: '12px', fontWeight: 600, marginBottom: '20px' }}>
            STATUS: {connectionStatus}
          </div>
        </div>

        <div className="panel">
          <h2>Simulation Control</h2>
          <select 
            value={selectedScenario} 
            onChange={(e) => setSelectedScenario(e.target.value)}
            disabled={ws !== null}
            style={{ marginBottom: '10px' }}
          >
            {scenarios.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          
          {ws ? (
            <button className="btn" onClick={disconnect} style={{ color: '#ff4444' }}>Stop Simulation</button>
          ) : (
            <button className="btn btn-primary" onClick={connect}>Initialize World</button>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '10px' }}>
            <button className="btn" onClick={togglePause} disabled={!ws}>
              {paused ? <Play size={16} /> : <Pause size={16} />} 
              {paused ? "Play" : "Pause"}
            </button>
            <button className="btn" onClick={() => sendCommand('step')} disabled={!ws || !paused}>
              <SkipForward size={16} /> Step
            </button>
          </div>

          <button className="btn" onClick={exportReport} disabled={fullStats.length === 0} style={{ width: '100%', marginTop: '10px', background: '#238636', color: '#ffffff' }}>
            Export Metrics CSV
          </button>

          <div style={{ marginTop: '16px' }}>
            <label style={{ fontSize: '12px', color: '#8b949e', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FastForward size={14} /> Engine Speed
            </label>
            <select value={speed} onChange={handleSpeed} disabled={!ws} style={{ marginTop: '8px' }}>
              <option value={0.25}>Slow (250ms)</option>
              <option value={0.05}>Normal (50ms)</option>
              <option value={0.01}>Fast (10ms)</option>
              <option value={0}>Max (0ms)</option>
            </select>
          </div>
        </div>

        {state && state.faction_metadata && state.faction_metadata.length > 0 && (
          <div className="panel" style={{ marginTop: '16px' }}>
            <h2>Ecosystem Factions (LLM)</h2>
            {state.faction_metadata.map((f: any) => (
              <div key={f.id} style={{ marginBottom: '8px', padding: '8px', background: '#1e242b', borderRadius: '4px', borderLeft: `4px solid ${f.color || '#cccccc'}` }}>
                <h3 style={{ margin: '0 0 4px 0', fontSize: '13px', color: '#c9d1d9' }}>{f.id}</h3>
                {f.description && <p style={{ fontSize: '11px', color: '#8b949e', margin: 0, lineHeight: 1.4 }}>{f.description}</p>}
                {state.factions && state.factions[f.id] !== undefined && (
                  <div style={{ fontSize: '10px', color: '#58a6ff', marginTop: '4px', textAlign: 'right' }}>
                    Population: {state.factions[f.id]}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {state && (
          <div className="stat-grid">
            <div className="stat-box">
              <div className="stat-value">{state.tick}</div>
              <div className="stat-label">Current Tick</div>
            </div>
            <div className="stat-box">
              <div className="stat-value" style={{ color: '#44ff44' }}>{state.weather}</div>
              <div className="stat-label">Season</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{state.population}</div>
              <div className="stat-label">Agents Alive</div>
            </div>
            <div className="stat-box">
              <div className="stat-value" style={{ color: '#ffff44' }}>
                {Math.round(state.agents.reduce((a: number, b: any) => a + b.energy, 0))}
              </div>
              <div className="stat-label">Global Energy</div>
            </div>
          </div>
        )}
      </aside>

      <main className="main-view">
        {state ? (
          <Renderer state={state} />
        ) : (
          <div style={{ color: '#8b949e', textAlign: 'center' }}>
            <Server size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
            <p>Awaiting Simulation Initialization...</p>
          </div>
        )}
      </main>

      <aside className="sidebar">
        <Charts history={history} currentState={state} />
      </aside>
    </div>
  );
}

export default App;
