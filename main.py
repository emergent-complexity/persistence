import sys
import config
import time
from src.logger import DataLogger
from src.engine import Simulation
from utils.viz import Visualizer

def get_seed():
    if config.RANDOM_SEED is not None:
        active_seed = config.RANDOM_SEED
    else:
        active_seed = int(time.time_ns() % 1e9)
    return active_seed
    
def run_headless(this_seed, name, steps=config.MAX_STEPS_HEADLESS):
    logger = DataLogger(run_name=name, seed=this_seed)
    sim = Simulation(this_seed, logger)
    print(f"🚀 Running Headless: {name}")
    try:
        for _ in range(steps):
            sim.step()
            if sim.frame_count % config.AUDIT_INTERVAL == 0:
                sim.check_mass_integrity()
                sim.check_energy_integrity()
            if not sim.agents: break
    finally:
        m, e = sim.check_mass_integrity(), sim.check_energy_integrity()
        sim.save_audit_report(m, e)
        sim.logger.save_to_disk()

if __name__ == "__main__":
    args = sys.argv[1:]
    this_seed = get_seed()
    if "--headless" in args:
        run_headless(this_seed, "Headless_Run")
    elif "--replay" in args:
        try:
            folder_path = sys.argv[sys.argv.index("--replay") + 1]
            sim = Simulation.from_history(folder_path)
            viz = Visualizer(sim)
            print(f"🎬 Recording replay for: {folder_path}")
            viz.show(save_gif=True, folder=folder_path)
            # Run a final audit on the replayed end-state
            sim.check_mass_integrity() 
        except (IndexError, ValueError):
            print("❌ Error: Provide a path! Usage: python main.py --replay Results/Run_Folder")
        pass
    else:
        logger = DataLogger(run_name="Live_Run", seed=this_seed)
        sim = Simulation(this_seed, logger)
        try:
            viz = Visualizer(sim)
            print(f"Starting GUI:")
            viz.show() 
        finally:
            # This runs when the window is closed
            print("\n[CLOSING SIMULATION]")
            m, e = sim.check_mass_integrity(), sim.check_energy_integrity()
            sim.save_audit_report(m, e)
            sim.logger.save_to_disk()