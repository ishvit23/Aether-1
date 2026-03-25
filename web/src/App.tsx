import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, FastForward, SkipForward, Server } from 'lucide-react';
import Renderer from './components/Renderer';
import Charts from './components/Charts';

function App() {
  const [scenarios, setScenarios] = useState<string[]>([]);
  const [selectedScenario, setSelectedScenario] = useState('world_v1.json');
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  const [state, setState] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
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
        setState(data);
        setHistory(prev => [...prev.slice(-200), data]); // keep last 200 ticks
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
