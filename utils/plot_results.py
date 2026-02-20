import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import numpy as np
import config

def apply_style(ax, title, ylabel, style):
    """Applies the chosen aesthetic to a subplot."""
    if style == 'TELEMETRIC':
        ax.set_facecolor('#050505')
        ax.set_title(f"SCN_{title.upper()}", fontfamily='monospace', loc='left', color='#00FF41', pad=10)
        ax.set_ylabel(ylabel.upper(), fontfamily='monospace', fontsize=10, color='#00FF41')
        ax.set_xlabel("CHRONO_STEPS", fontfamily='monospace', fontsize=10, color='#00FF41')
        ax.tick_params(colors='#00FF41', labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor('#00FF41')
            spine.set_alpha(0.3)
        ax.grid(True, alpha=0.1, color='#00FF41', linestyle='--')
    else:  # SCIENTIFIC
        ax.set_title(title.replace('_', ' ').title())
        ax.set_ylabel(ylabel.title())
        ax.set_xlabel("Steps")
        ax.grid(True, alpha=0.3)

def plot_case(case_path):
    """Generates an analytical summary based on the global VISUAL_STYLE."""
    style = getattr(config, 'VISUAL_STYLE', 'SCIENTIFIC').upper()
    plt.style.use('dark_background' if style == 'TELEMETRIC' else 'default')
    
    # 1. Data Retrieval
    repeat_dirs = [d for d in os.listdir(case_path) if os.path.isdir(os.path.join(case_path, d)) and d.isdigit()]
    if not repeat_dirs:
        repeat_dirs = ['.'] if os.path.exists(os.path.join(case_path, 'timeseries.csv')) else []
    
    all_runs = [pd.read_csv(os.path.join(case_path, rd, 'timeseries.csv')) for rd in repeat_dirs 
                if os.path.exists(os.path.join(case_path, rd, 'timeseries.csv'))]
    
    if not all_runs: return

    sample_df = all_runs[0]
    species_names = [col.replace('pop_', '') for col in sample_df.columns if col.startswith('pop_')]
    colors = getattr(config, 'SPECIES_COLORS', {'standard': '#00FF41', 'mutant': '#FF4500'})
    
    fig_bg = '#050505' if style == 'TELEMETRIC' else 'white'
    fig, axes = plt.subplots(2, 2, figsize=(15, 12), facecolor=fig_bg)
    
    title_str = f"▼ RECOVERY_DATA: {os.path.basename(case_path).upper()} // AUDIT_COMPLETE" if style == 'TELEMETRIC' \
                else f"Baseline Analysis: {os.path.basename(case_path)}"
    title_color = '#00FF41' if style == 'TELEMETRIC' else 'black'
    fig.suptitle(title_str, fontsize=16, fontfamily='monospace' if style == 'TELEMETRIC' else None, 
                 color=title_color, fontweight='bold')

    def plot_with_variance(ax, col_prefix, suffix, title, ylabel):
        for sid in species_names:
            col_name = f"{col_prefix}{sid}{suffix}"
            if col_name not in sample_df.columns: continue
            
            data_stack = np.array([run[col_name].values for run in all_runs])
            mean_vals = np.mean(data_stack, axis=0)
            min_vals = np.min(data_stack, axis=0)
            max_vals = np.max(data_stack, axis=0)
            
            color = colors.get(sid, '#00FF41')
            label = f"SIG_{sid.upper()}" if style == 'TELEMETRIC' else sid
            ax.plot(mean_vals, label=label, color=color, lw=2)
            ax.fill_between(range(len(mean_vals)), min_vals, max_vals, color=color, alpha=0.1 if style == 'TELEMETRIC' else 0.2)
        
        apply_style(ax, title, ylabel, style)
        ax.legend(prop={'family': 'monospace', 'size': 8} if style == 'TELEMETRIC' else None)

    # --- Metrics ---
    plot_with_variance(axes[0, 0], "pop_", "", "population_density", "count")
    plot_with_variance(axes[0, 1], "", "_avg_stored_mass", "economic_health", "mass_units")
    
    # --- Mortality Analysis ---
    window = 70  
    death_causes = ['starve', 'senility', 'toxic', 'heat']
    for sid in species_names:
        color = colors.get(sid, '#00FF41')
        rates = {c: pd.Series(np.diff(np.mean([r[f"{sid}_{c}"].values for r in all_runs], axis=0), prepend=0)).rolling(window=window).mean() 
                 for c in death_causes if f"{sid}_{c}" in sample_df.columns}
        
        rate_df = pd.DataFrame(rates).fillna(0)
        if not rate_df.empty and rate_df.sum().sum() > 0:
            leading_cause, leading_rate = rate_df.idxmax(axis=1), rate_df.max(axis=1)
            ax_label = f"STR_{sid.upper()}" if style == 'TELEMETRIC' else f"{sid} Stress"
            axes[1, 0].plot(leading_rate, color=color, lw=1.5, label=ax_label)
            
            for t in range(window, len(leading_rate), 400):
                if leading_rate.iloc[t] > 0.01:
                    tag = f"[{leading_cause.iloc[t][:3].upper()}]" if style == 'TELEMETRIC' else leading_cause.iloc[t][:3].upper()
                    axes[1, 0].text(t, leading_rate.iloc[t], tag, color=color, fontsize=7, 
                                    fontfamily='monospace' if style == 'TELEMETRIC' else None, ha='center', va='bottom')

    apply_style(axes[1, 0], "mortality_stress", "delta_deaths", style)
    plot_with_variance(axes[1, 1], "", "_avg_age", "longevity", "steps")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    ext = 'telemetry_summary.png' if style == 'TELEMETRIC' else 'analysis_summary.png'
    plt.savefig(os.path.join(case_path, ext), dpi=200, facecolor=fig_bg)
    plt.close()
    print(f"📡 {'DATA_ARCHIVED' if style == 'TELEMETRIC' else 'Report Generated'}: {os.path.basename(case_path)}")

    
if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    if os.path.isdir(path):
        # FIX: Check if timeseries.csv exists directly in this folder or subfolders
        if os.path.exists(os.path.join(path, 'timeseries.csv')):
            plot_case(path)
        else:
            # Check one level deep for any folder containing data
            for folder in [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]:
                if os.path.exists(os.path.join(folder, 'timeseries.csv')) or \
                   any(os.path.exists(os.path.join(folder, sub, 'timeseries.csv')) for sub in os.listdir(folder) if os.path.isdir(os.path.join(folder, sub))):
                    plot_case(folder)