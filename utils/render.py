import sys
import os

# Add the project root (parent directory) to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import config
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from src.engine import Simulation
from utils.viz import Visualizer

class NullLogger:
    """A silent logger to prevent creating redundant files during rendering."""
    def log_step(self, data): pass
    def save_to_disk(self): pass
    @property
    def run_dir(self): return "REPLAY_BUFFER"

def get_run_metadata(folder):
    meta_path = os.path.join(folder, "metadata.json")
    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"❌ No metadata found in {folder}")
    with open(meta_path, 'r') as f:
        return json.load(f)

def social_render(run_folder, mode="timelapse", start_step=0, duration=200, target_field='carbon'):
    # 1. Setup Environment
    meta = get_run_metadata(run_folder)
    original_seed = meta['seed']
    style = getattr(config, 'VISUAL_STYLE', 'SCIENTIFIC').upper()
    
    print(f"📡 RECONSTRUCTING_UNIVERSE | Style: {style} | Seed: {original_seed}")
    
    # 2. Reconstruct Simulation & Visualizer
    sim = Simulation(seed=original_seed, logger=NullLogger())
    viz = Visualizer(sim)
    
    # 3. Apply Field Choice
    viz.display_field = target_field
    conf = viz.field_configs.get(target_field, {'cmap': 'magma', 'vmax': 1.0})
    viz.im.set_cmap(conf['cmap'])
    viz.im.set_clim(0, conf['vmax'])
    if hasattr(viz, 'cbar'):
        viz.cbar.set_label(f"Concentration ({target_field})")
    
    # 4. Fix Framing for HUD
    # Scientific mode needs less margin; Telemetric needs more for the sidebar
    right_margin = 0.72 if style == 'TELEMETRIC' else 0.85
    viz.fig.subplots_adjust(right=right_margin, left=0.05, top=0.95, bottom=0.05)
    
    save_path = os.path.join(run_folder, f"render_{style.lower()}_{target_field}_{mode}.mp4")
    
    # 5. Define Animation Logic
    if mode == "timelapse":
        total_steps = getattr(config, 'MAX_STEPS_HEADLESS', 20000)
        num_frames = getattr(config, 'RENDER_INTERVAL', 200)
        stride = total_steps // num_frames
        
        def update(frame):
            for _ in range(stride):
                sim.step()
                if not sim.agents: break
            return viz.update_visuals()

    elif mode == "event":
        print(f"⏩ FAST-FORWARDING to step {start_step}...")
        for _ in range(start_step):
            sim.step()
        
        num_frames = duration
        def update(frame):
            sim.step()
            return viz.update_visuals()
    else:
        raise ValueError(f"❌ Unknown mode: '{mode}'. Use 'timelapse' or 'event'.")
        
    # 6. Final Render
    ani = FuncAnimation(viz.fig, update, frames=num_frames, blit=True)
    
    print(f"🎬 RENDERING: {save_path}")
    # Higher DPI for Telemetric to keep the green glow and text sharp
    render_dpi = 150 if style == 'TELEMETRIC' else 120
    ani.save(save_path, writer='ffmpeg', fps=20, dpi=render_dpi)
    print(f"✅ AUDIT_COMPLETE: {style} render saved.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python render.py <folder> <mode: timelapse/event> <field> [start_step] [duration]")
    else:
        path = sys.argv[1]
        m = sys.argv[2]
        field = sys.argv[3] if len(sys.argv) > 3 else 'carbon'
        s = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        d = int(sys.argv[5]) if len(sys.argv) > 5 else 200
        
        social_render(path, m, s, d, field)