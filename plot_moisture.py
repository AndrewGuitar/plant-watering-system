import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
 
LOG_FILE = "watering_log.csv"
OUTPUT_IMAGE = "moisture_chart.png"
 
 
def load_log(path):
    timestamps = []
    moisture_values = []
    watered_points = []  # (timestamp, moisture) for readings where the pump ran
 
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = datetime.fromisoformat(row["timestamp"])
            moisture = float(row["moisture_percent"])
            timestamps.append(ts)
            moisture_values.append(moisture)
            if row["watered"] == "True":
                watered_points.append((ts, moisture))
 
    return timestamps, moisture_values, watered_points
 
 
def plot_moisture(timestamps, moisture_values, watered_points):
    fig, ax = plt.subplots(figsize=(10, 5))
 
    # Main moisture line
    ax.plot(timestamps, moisture_values, color="seagreen", linewidth=1.5, label="Soil moisture (%)")
 
    # Mark points where the pump actually watered
    if watered_points:
        watered_ts, watered_vals = zip(*watered_points)
        ax.scatter(watered_ts, watered_vals, color="royalblue", zorder=5, label="Pump activated")
 
    ax.set_xlabel("Time")
    ax.set_ylabel("Soil Moisture (%)")
    ax.set_title("Soil Moisture Over Time")
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True, alpha=0.3)
 
    # Format the x-axis nicely for dates/times
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
 
    fig.tight_layout()
    fig.savefig(OUTPUT_IMAGE, dpi=150)
    print(f"Saved chart to {OUTPUT_IMAGE}")
 
 
if __name__ == "__main__":
    timestamps, moisture_values, watered_points = load_log(LOG_FILE)
 
    if not timestamps:
        print(f"No data found in {LOG_FILE} yet. Run the watering script first to collect readings.")
    else:
        plot_moisture(timestamps, moisture_values, watered_points)
