import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import os
import config

class Visualizer:
    def __init__(self, simulation):
        self.sim = simulation
        # Detect style from config, default to Scientific
        self.style = getattr(config, 'VISUAL_STYLE', 'SCIENTIFIC').upper()
        
        # 1. Setup Theme and Figure
        if self.style == 'TELEMETRIC':
            plt.style.use('dark_background')
            self.fig, self.ax = plt.subplots(figsize=(11, 8), facecolor='#050505')
            self.ax.set_facecolor('#050505')
            self.ax.axis('off')
            self.interp = 'gaussian' # Soft chemical clouds
        else:
            plt.style.use('default')
            self.fig, self.ax = plt.subplots(figsize=(10, 8))
            self.interp = 'nearest' # Crisp pixel grid

        # 2. Pull Configs
        self.display_field = getattr(config, 'INITIAL_VIEW', 'carbon')
        self.field_configs = getattr(config, 'FIELD_VIZ_CONFIG', {})
        self.key_map = getattr(config, 'KEY_BINDINGS', {})
        self.species_colors = getattr(config, 'SPECIES_COLORS', {})
        
        # 3. Background Field
        conf = self.field_configs.get(self.display_field, {'cmap': 'viridis', 'vmax': 1.0})
        self.im = self.ax.imshow(
            self.sim.fields.fields[self.display_field], 
            animated=True, cmap=conf['cmap'], origin='lower',
            extent=[0, self.sim.shape[1], 0, self.sim.shape[0]],
            vmin=0, vmax=conf['vmax'], zorder=1, interpolation=self.interp
        )
        
        # 4. Agent Display
        s_size = 18 if self.style == 'TELEMETRIC' else 20
        self.scat = self.ax.scatter([], [], s=s_size, edgecolors='white', linewidths=0.2, zorder=2)

        # 5. HUD Initialization
        self._init_hud()
        
        if self.style == 'SCIENTIFIC':
            self.ax.set_title(f"Simulation Audit: {self.sim.logger.run_dir.split('_')[-1]}")
            self.cbar = self.fig.colorbar(self.im, ax=self.ax)

        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        plt.tight_layout()

    def _init_hud(self):
        if self.style == 'TELEMETRIC':
            font = {'family': 'monospace', 'color': '#00FF41', 'weight': 'bold', 'size': 9}
            pos, ha, va = (1.02, 0.98), 'left', 'top'
            bbox = dict(facecolor='black', alpha=0.7, edgecolor='#00FF41', boxstyle='round,pad=0.5')
        else:
            font = {'family': 'monospace', 'color': 'black', 'weight': 'bold', 'size': 9}
            pos, ha, va = (0.98, 0.95), 'right', 'top'
            bbox = dict(facecolor='white', alpha=0.8, edgecolor='gray', lw=0.5)

        self.counter_text = self.ax.text(
            *pos, '', transform=self.ax.transAxes, fontdict=font, 
            ha=ha, va=va, bbox=bbox, zorder=3
        )

    def on_key(self, event):
        if event.key in self.key_map:
            self.display_field = self.key_map[event.key]
            conf = self.field_configs.get(self.display_field, {'cmap': 'viridis', 'vmax': 1.0})
            self.im.set_cmap(conf['cmap'])
            self.im.set_clim(0, conf['vmax'])
            self.fig.canvas.draw_idle()

    def update_visuals(self):
        self.im.set_array(self.sim.fields.fields[self.display_field])
        species_counts = {}
        if self.sim.agents:
            offsets = np.array([a.pos[::-1] for a in self.sim.agents])
            colors = [self.species_colors.get(a.genome.species_id, 'white') for a in self.sim.agents]
            for a in self.sim.agents:
                sid = a.genome.species_id
                species_counts[sid] = species_counts.get(sid, 0) + 1
            self.scat.set_offsets(offsets)
            self.scat.set_facecolors(colors)
        
        avg_e = np.mean([a.energy for a in self.sim.agents]) if self.sim.agents else 0
        
        if self.style == 'TELEMETRIC':
            readout = self._get_telemetric_text(species_counts, avg_e)
        else:
            readout = self._get_scientific_text(species_counts, avg_e)
            
        self.counter_text.set_text(readout)
        return (self.im, self.scat, self.counter_text)

    def _get_telemetric_text(self, counts, avg_e):
        info = ""
        for sid, count in counts.items():
            deaths = self.sim.deaths.get(sid, {})
            top = max(deaths, key=deaths.get) if any(deaths.values()) else "NONE"
            info += f"» {sid:<10} | POP: {count:04d} | RIP: {top.upper()}\n"
        return f"▼ SYSTEM_STATE: RUNNING\n▼ CHRONO_STEP: {self.sim.frame_count:05d}\n▼ AVG_NRG: {avg_e:06.2f}\n{'-'*30}\n{info}\nENTROPY: STABLE"

    def _get_scientific_text(self, counts, avg_e):
        return f"STEP: {self.sim.frame_count}\nPOP: {sum(counts.values())}\nAVG E: {avg_e:.1f}"

    def update(self, frame):
        self.sim.step()
        return self.update_visuals()
        
    def show(self, save_gif=False, folder=None):
        if save_gif and folder:
            subsample_rate = 20  
            total_gif_frames = 150 
            def replay_step(frame):
                for _ in range(subsample_rate):
                    self.sim.step()
                    if not self.sim.agents: break 
                return self.update_visuals()
            ani = FuncAnimation(self.fig, replay_step, frames=total_gif_frames, blit=True)
            save_path = os.path.join(folder, f"{self.style.lower()}_render.gif")
            ani.save(save_path, writer='pillow', fps=15)
        else:
            self.ani = FuncAnimation(self.fig, self.update, interval=1, blit=True, cache_frame_data=False)
            plt.show() 