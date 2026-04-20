import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Line, Pie } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement
);

interface ChartsProps {
  history: any[];
  currentState: any;
}

const FACTION_COLORS: Record<string, string> = {
  "None": "#aaaaaa",
  "Warrior": "#ff4444",
  "Scout": "#44ff44",
  "Merchant": "#ffff44",
  "Scholar": "#ff44ff",
  "Raider": "#ff9900",
  "Builder": "#44ffff"
};

const Charts: React.FC<ChartsProps> = ({ history, currentState }) => {
  const lineData = useMemo(() => {
    // Only show last 200 ticks for performance
    const recent = history.slice(-200);
    return {
      labels: recent.map(s => s.tick),
      datasets: [
        {
          label: 'Population',
          data: recent.map(s => s.population),
          borderColor: '#58a6ff',
          backgroundColor: 'rgba(88, 166, 255, 0.5)',
          tension: 0.2,
          pointRadius: 0
        }
      ]
    };
  }, [history]);

  const lineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 }, // prevent lag on live stream
    scales: {
      x: { display: true, ticks: { color: '#8b949e' } },
      y: { display: true, min: 0, ticks: { color: '#8b949e' } },
    },
    plugins: {
      legend: { labels: { color: '#c9d1d9' } }
    }
  };

  const pieData = useMemo(() => {
    if (!currentState || !currentState.factions) return null;
    const factions = currentState.factions;
    const labels = Object.keys(factions);
    const data = Object.values(factions);
    const bgColors = labels.map(l => {
      // Prioritize dynamically generated LLM matrix hex colors instead of legacy fallbacks
      const meta = (currentState.faction_metadata || []).find((m: any) => m.id === l);
      if (meta && meta.color) return meta.color;
      return FACTION_COLORS[l] || "#aaaaaa";
    });

    return {
      labels,
      datasets: [{
        data,
        backgroundColor: bgColors,
        borderColor: '#161b22',
        borderWidth: 2,
      }]
    };
  }, [currentState]);

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 0 },
    plugins: {
      legend: { position: 'bottom' as const, labels: { color: '#c9d1d9' } }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
      <div className="panel" style={{ height: '250px' }}>
        <h2>Population Tracker</h2>
        <div style={{ height: '200px' }}>
          {history.length > 0 && <Line data={lineData} options={lineOptions} />}
        </div>
      </div>
      
      <div className="panel" style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <h2>Faction Dominance</h2>
        <div style={{ flexGrow: 1, minHeight: '200px' }}>
          {pieData && <Pie data={pieData} options={pieOptions} />}
        </div>
      </div>
    </div>
  );
};

export default Charts;
