import React, { useRef, useEffect, useState } from 'react';

interface RendererProps {
  state: any;
}

const FACTION_COLORS: Record<string, string> = {
  "None": "#aaaaaa",
  "Warrior": "#ff4444",
  "Scout": "#44ff44",
  "Merchant": "#ffff44",
  "Scholar": "#ff44ff",
  "Raider": "#ff9900",
  "Builder": "#44ffff",
  "Frost-Walkers": "#00ffff",
  "Snow-Hunters": "#ffffff",
};

const EMOTES: Record<string, string> = {
  "attacking": "⚔️",
  "eating": "🍖",
  "reproducing": "❤️",
  "fleeing": "💨",
  "trading": "💰",
  "hunting": "🏹",
  "building": "🔨"
};

const CELL_SIZE = 16;
const TILE_GRASS = 0;
const TILE_WALL = 1;
const TILE_NEST = 2;
const TILE_AGENT = 3;

// Global cache for Tinted Agent Sprites
const tintedSpriteCache = new Map<string, HTMLCanvasElement>();

function getTintedSprite(factionId: string, baseImage: HTMLImageElement): HTMLCanvasElement {
  if (tintedSpriteCache.has(factionId)) {
    return tintedSpriteCache.get(factionId)!;
  }
  
  const canvas = document.createElement("canvas");
  canvas.width = CELL_SIZE;
  canvas.height = CELL_SIZE;
  const ctx = canvas.getContext("2d");
  if (ctx) {
    // Draw the white agent base
    ctx.drawImage(baseImage, TILE_AGENT * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE, 0, 0, CELL_SIZE, CELL_SIZE);
    
    // Multiply blend the faction color
    ctx.globalCompositeOperation = "multiply";
    ctx.fillStyle = FACTION_COLORS[factionId] || "#aaaaaa";
    ctx.fillRect(0, 0, CELL_SIZE, CELL_SIZE);
    
    // Restore composite operation (so outline remains black and interior is colored)
    ctx.globalCompositeOperation = "destination-in";
    ctx.drawImage(baseImage, TILE_AGENT * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE, 0, 0, CELL_SIZE, CELL_SIZE);
  }
  
  tintedSpriteCache.set(factionId, canvas);
  return canvas;
}

const Renderer: React.FC<RendererProps> = ({ state }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [tilesLoaded, setTilesLoaded] = useState(false);
  const tilesImageRef = useRef<HTMLImageElement>(new Image());

  useEffect(() => {
    tilesImageRef.current.src = "/tiles.png";
    tilesImageRef.current.onload = () => {
      setTilesLoaded(true);
    };
  }, []);

  useEffect(() => {
    if (!state || !state.grid || !tilesLoaded) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = state.grid.width * CELL_SIZE;
    canvas.height = state.grid.height * CELL_SIZE;
    const img = tilesImageRef.current;

    // 1. Draw Base Terrain (Grass everywhere)
    for (let y = 0; y < state.grid.height; y++) {
      for (let x = 0; x < state.grid.width; x++) {
        ctx.drawImage(img, TILE_GRASS * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE, x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
      }
    }

    // 2. Draw Static Structures & Resources
    if (state.cells) {
      state.cells.forEach((cell: any) => {
        const px = cell.x * CELL_SIZE;
        const py = cell.y * CELL_SIZE;

        if (cell.structure) {
          const kind = cell.structure.kind || cell.structure; 
          if (kind === 'wall') {
            ctx.drawImage(img, TILE_WALL * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE, px, py, CELL_SIZE, CELL_SIZE);
          } else if (kind === 'nest') {
            ctx.drawImage(img, TILE_NEST * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE, px, py, CELL_SIZE, CELL_SIZE);
          }
        }

        // Draw Resources (subtle green dot for food)
        if (cell.resources && cell.resources['food'] > 0 && cell.structure === null) {
          ctx.fillStyle = `rgba(0, 255, 0, ${Math.min(1.0, cell.resources['food'] / 20)})`;
          ctx.beginPath();
          ctx.arc(px + CELL_SIZE/2, py + CELL_SIZE/2, 3, 0, Math.PI * 2);
          ctx.fill();
        }
      });
    }

    // 3. Draw Animals (Rabbits and Wolves as Emojis for now, distinguishing them from humanoids)
    if (state.animals) {
      state.animals.forEach((animal: any) => {
        const px = animal.x * CELL_SIZE + CELL_SIZE / 2;
        const py = animal.y * CELL_SIZE + CELL_SIZE / 2;
        ctx.font = `${CELL_SIZE - 2}px Arial`;
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        if (animal.kind === 'rabbit') {
          ctx.fillText("🐇", px, py);
        } else if (animal.kind === 'wolf') {
          ctx.fillText("🐺", px, py);
        }
      });
    }

    // 4. Draw Agents (Humanoids) and Emotes
    if (state.agents) {
      state.agents.forEach((agent: any) => {
        const px = agent.x * CELL_SIZE;
        const py = agent.y * CELL_SIZE;
        const factionId = agent.faction || "None";
        
        // Fetch Tinted Sprite from Cache Layer
        const sprite = getTintedSprite(factionId, img);
        ctx.drawImage(sprite, px, py);

        // Draw Action Emotes natively floating above sprite
        if (agent.state && EMOTES[agent.state]) {
            ctx.font = "10px Arial";
            ctx.textAlign = "center";
            ctx.fillText(EMOTES[agent.state], px + CELL_SIZE/2, py - 4);
        }
      });
    }

    // 5. Apply Global Atmospheric Seasonal Filters
    if (state.weather === "Winter") {
       ctx.fillStyle = "rgba(255, 255, 255, 0.25)";
       ctx.fillRect(0, 0, canvas.width, canvas.height);
    } else if (state.weather === "Autumn") {
       ctx.fillStyle = "rgba(255, 120, 0, 0.15)";
       ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

  }, [state, tilesLoaded]);

  return (
    <div style={{ padding: '4px', background: '#111', borderRadius: '4px', border: '2px solid #30363d', display: 'inline-block' }}>
      <canvas ref={canvasRef} style={{ display: 'block', imageRendering: 'pixelated' }} />
    </div>
  );
};

export default Renderer;
