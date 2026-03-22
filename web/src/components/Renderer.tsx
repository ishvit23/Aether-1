import React, { useRef, useEffect } from 'react';

interface RendererProps {
  state: any;
}

// Map Factions to Hex colors for distinct visibility
const FACTION_COLORS: Record<string, string> = {
  "None": "#aaaaaa",
  "Warrior": "#ff4444",
  "Scout": "#44ff44",
  "Merchant": "#ffff44",
  "Scholar": "#ff44ff",
  "Raider": "#ff9900",
  "Builder": "#44ffff"
};

const WEATHER_TINTS: Record<string, string> = {
  "Spring": "rgba(100, 255, 100, 0.05)",
  "Summer": "rgba(255, 255, 100, 0.05)",
  "Autumn": "rgba(255, 150, 50, 0.05)",
  "Winter": "rgba(200, 200, 255, 0.15)",
};

const Renderer: React.FC<RendererProps> = ({ state }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!state || !state.grid) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const CELL_SIZE = 14;
    canvas.width = state.grid.width * CELL_SIZE;
    canvas.height = state.grid.height * CELL_SIZE;

    // Clear board
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Weather background tint
    const tint = WEATHER_TINTS[state.weather] || "rgba(0,0,0,0)";
    ctx.fillStyle = tint;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw Grid (optional subtle lines)
    ctx.strokeStyle = '#1e242b';
    ctx.lineWidth = 1;
    for (let x = 0; x <= state.grid.width; x++) {
      ctx.beginPath();
      ctx.moveTo(x * CELL_SIZE, 0);
      ctx.lineTo(x * CELL_SIZE, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y <= state.grid.height; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * CELL_SIZE);
      ctx.lineTo(canvas.width, y * CELL_SIZE);
      ctx.stroke();
    }

    // Draw Static Cells (Structures / Resources)
    if (state.cells) {
      state.cells.forEach((cell: any) => {
        const px = cell.x * CELL_SIZE;
        const py = cell.y * CELL_SIZE;

        // Draw Structure
        if (cell.structure === 'wall') {
          ctx.fillStyle = '#444';
          ctx.fillRect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2);
        } else if (cell.structure === 'nest') {
          ctx.fillStyle = '#665511';
          ctx.fillRect(px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4);
          ctx.strokeStyle = '#cc9900';
          ctx.strokeRect(px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4);
        }

        // Draw Resources (subtle green for food)
        if (cell.resources && cell.resources['food'] > 0 && cell.structure === null) {
          ctx.fillStyle = `rgba(0, 255, 0, ${Math.min(1.0, cell.resources['food'] / 20)})`;
          ctx.beginPath();
          ctx.arc(px + CELL_SIZE/2, py + CELL_SIZE/2, 2, 0, Math.PI * 2);
          ctx.fill();
        }
      });
    }

    // Draw Agents
    if (state.agents) {
      state.agents.forEach((agent: any) => {
        const px = agent.x * CELL_SIZE + CELL_SIZE / 2;
        const py = agent.y * CELL_SIZE + CELL_SIZE / 2;

        ctx.fillStyle = FACTION_COLORS[agent.faction || "None"] || "#aaaaaa";
        
        ctx.beginPath();
        // Slightly bigger if high energy
        const radius = Math.min(CELL_SIZE / 2 - 2, Math.max(2, (agent.energy / 100) * (CELL_SIZE / 2)));
        ctx.arc(px, py, radius, 0, Math.PI * 2);
        ctx.fill();

        // Outline if in combat
        if (agent.state === 'attacking') {
          ctx.strokeStyle = '#fff';
          ctx.lineWidth = 2;
          ctx.stroke();
        }
      });
    }

  }, [state]);

  return (
    <div style={{ padding: '10px', background: '#000', borderRadius: '8px', border: '1px solid #30363d' }}>
      <canvas ref={canvasRef} style={{ display: 'block' }} />
    </div>
  );
};

export default Renderer;
