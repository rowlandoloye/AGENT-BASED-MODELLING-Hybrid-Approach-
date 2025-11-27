# run_simulation.py — batch run for BuildingModel
import mesa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

from model import BuildingModel


def ultra_safe_mean(series):
    if series.empty:
        return np.nan
    values = []
    for cell in series.astype(str):
        nums = re.findall(r"\d+\.?\d*", cell)
        values.extend([float(n) for n in nums])
    return np.mean(values) if values else np.nan


def safe_int(value, default, min_allowed=None, max_allowed=None):
    """Convert to int with optional bounds and sensible fallback."""
    try:
        x = int(round(float(value)))
    except (TypeError, ValueError):
        return default

    if min_allowed is not None and x < min_allowed:
        return default
    if max_allowed is not None and x > max_allowed:
        return default
    return x


print("Loading your real data...")
checklist = pd.read_csv("Mr Rowland Elevator checklist.csv")
questionnaire = pd.read_csv("Mr Rowland Questionnaire.csv")

calib = {
    "avg_wait": ultra_safe_mean(checklist["BAT"])
    if "BAT" in checklist.columns
    else 24.5,
    "dwell_time": ultra_safe_mean(checklist["BDTAD"])
    if "BDTAD" in checklist.columns
    else 10.6,
    "journey_time": ultra_safe_mean(checklist["BJTTJT"])
    if "BJTTJT" in checklist.columns
    else 67.9,

    # Capacity: clamp between 4 and 30
    "capacity": safe_int(
        ultra_safe_mean(checklist["AECP"]) if "AECP" in checklist.columns else 16,
        default=16,
        min_allowed=4,
        max_allowed=30,
    ),

    # Number of elevators: clamp between 1 and 10
    "num_elevators": safe_int(
        ultra_safe_mean(checklist["AEN"]) if "AEN" in checklist.columns else 2,
        default=2,
        min_allowed=1,
        max_allowed=10,
    ),

    "vibration": ultra_safe_mean(checklist["CVLRS"])
    if "CVLRS" in checklist.columns
    else 1.01,
    "noise": ultra_safe_mean(checklist["CNLDB"])
    if "CNLDB" in checklist.columns
    else 55.9,

    # Floors: clamp between 2 and 50
    "num_floors": safe_int(
        ultra_safe_mean(questionnaire["A6"]) if "A6" in questionnaire.columns else 6,
        default=6,
        min_allowed=2,
        max_allowed=50,
    ),
}

print("\nCalibration:")
for k, v in calib.items():
    try:
        print(f"  {k}: {float(v):.2f}")
    except (TypeError, ValueError):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    print("\nRunning 50 simulations (2×2 conditions, 25 iterations each)...")

    results = mesa.batch_run(
        BuildingModel,
        parameters={
            "N_floors": calib["num_floors"],
            "N_elevators": calib["num_elevators"],
            "peak_hour": [True, False],
            "backup_power": [True, False],
            "door_time": calib["dwell_time"],
            "capacity": calib["capacity"],
            "vibration": calib["vibration"],
            "noise": calib["noise"],
            "speed": 3.0,
        },
        iterations=25,
        max_steps=3600,
        number_processes=1,
        display_progress=True,
    )

    results_df = pd.DataFrame(results)
    results_df.to_csv("simulation_results.csv", index=False)
    print("Results saved to simulation_results.csv")

    # Basic plots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    sns.histplot(results_df["Avg_Wait_Time"], ax=axes[0], kde=True)
    axes[0].set_title("Wait Time Distribution")
    axes[0].set_xlabel("Average Wait Time (s)")

    sns.scatterplot(
        data=results_df,
        x="Avg_Journey_Time",
        y="Avg_Satisfaction",
        hue="peak_hour",
        ax=axes[1],
    )
    axes[1].set_title("Journey vs Satisfaction")

    sns.boxplot(
        data=results_df,
        x="backup_power",
        y="Avg_Satisfaction",
        ax=axes[2],
    )
    axes[2].set_title("Backup Power Effect on Satisfaction")
    axes[2].set_xlabel("Backup Power Available")

    plt.tight_layout()
    plt.savefig("thesis_figures.png", dpi=300)
    print("thesis_figures.png created!")
    print("\nAll done! Open thesis_figures.png and simulation_results.csv")
