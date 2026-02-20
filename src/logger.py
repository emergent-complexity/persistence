# Persistence vAlpha - The Entropy Audit
# Copyright (C) 2026  emergent-complexity
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation.

import pandas as pd
import os
import shutil
import json
from datetime import datetime

class FileSystemManager:
    def __init__(self, base_dir="Results"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
            
    def create_run_folder(self, run_name=None):
        """Creates a unique timestamped folder for the simulation run."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_label = f"{timestamp}_{run_name}" if run_name else timestamp
        run_path = os.path.join(self.base_dir, folder_label)
        os.makedirs(run_path, exist_ok=True)
        return run_path

    def snapshot_config(self, run_path):
        """Copies the current config.py into the results folder for provenance."""
        if os.path.exists("config.py"):
            shutil.copy("config.py", os.path.join(run_path, "config_snapshot.py"))

class DataLogger:
    def __init__(self, run_name=None, seed=None):
        self.active_seed = seed
        self.fs = FileSystemManager()
        self.run_dir = self.fs.create_run_folder(run_name)
        self.csv_path = os.path.join(self.run_dir, "timeseries.csv")
        self.meta_path = os.path.join(self.run_dir, "metadata.json")
        self.history = []
        
        # Immediate snapshot upon initialization
        self.fs.snapshot_config(self.run_dir)
        
    def log_step(self, step_data):
        """Appends the step dictionary provided by Simulation.step()."""
        self.history.append(step_data)

    def save_to_disk(self):
        if not self.history:
            print("❌ Warning: No data in history to save.")
            return

        try:
            # 1. Save CSV
            df = pd.DataFrame(self.history)
            df.to_csv(self.csv_path, index=False)
            
            # 2. Key Check
            pop_key = 'total_population' if 'total_population' in df.columns else 'population'
            
            # 3. Metadata
            # Use .get() everywhere to prevent KeyErrors from stopping the save
            metadata = {
                "run_id": os.path.basename(self.run_dir),
                "seed": self.active_seed,
                "timestamp": datetime.now().isoformat(),
                "total_steps": len(self.history),
                "final_population": int(df[pop_key].iloc[-1]) if not df.empty else 0,
                "max_population": int(df[pop_key].max()) if not df.empty else 0,
                "species_final_counts": {k: int(df[k].iloc[-1]) for k in df.columns if k.startswith('pop_')},
            }
            
            

            with open(self.meta_path, 'w') as f:
                json.dump(metadata, f, indent=4)
                
            print(f"✅ Data successfully saved to: {self.run_dir}")
        except Exception as e:
            print(f"❌ Failed to save data: {e}")