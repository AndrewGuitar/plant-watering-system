import spidev
import RPi.GPIO as GPIO
import time
import csv
import os
from datetime import datetime
 
# ----------------------------
# Configuration
# ----------------------------
 
# MCP3008 channel the soil sensor is wired to
SOIL_CHANNEL = 0
 
# Relay control pin (BCM numbering)
RELAY_PIN = 17
 
# Calibration values from testing (adjust for your own sensor/soil)
DRY_VALUE = 850   # raw ADC reading in dry air
WET_VALUE = 400   # raw ADC reading fully submerged in water
 
# Water when soil moisture percentage drops below this
MOISTURE_THRESHOLD_PERCENT = 30
 
# How long to run the pump each time it waters (seconds)
PUMP_RUN_TIME = 5
 
# How often to check the soil (seconds)
CHECK_INTERVAL = 60
 
# Minimum time between waterings, to avoid back-to-back watering
# while the soil is still absorbing the last round (seconds)
MIN_TIME_BETWEEN_WATERING = 300
 
# Set to True to relay is "active low" (many cheap relay boards are)
RELAY_ACTIVE_LOW = True
 
# Log file path
LOG_FILE = "watering_log.csv"
 
 
# ----------------------------
# Setup
# ----------------------------
 
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
 
# Start with the pump off
PUMP_OFF = GPIO.HIGH if RELAY_ACTIVE_LOW else GPIO.LOW
PUMP_ON = GPIO.LOW if RELAY_ACTIVE_LOW else GPIO.HIGH
GPIO.output(RELAY_PIN, PUMP_OFF)
 
 
def init_log():
    """Create the log file with headers if it doesn't already exist."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "raw_value", "moisture_percent", "watered"])
 
 
def log_reading(raw_value, moisture_percent, watered):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(timespec="seconds"),
                          raw_value, round(moisture_percent, 1), watered])
 
 
# ----------------------------
# Sensor reading
# ----------------------------
 
def read_channel(channel):
    """Read a raw 10-bit value (0-1023) from the given MCP3008 channel."""
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data
 
 
def raw_to_percent(raw_value):
    """
    Convert a raw ADC reading to an approximate moisture percentage,
    using the dry/wet calibration values. Higher percent = wetter.
    """
    # Clamp raw value within the calibrated range before converting
    clamped = max(min(raw_value, DRY_VALUE), WET_VALUE)
    percent = (DRY_VALUE - clamped) / (DRY_VALUE - WET_VALUE) * 100
    return percent
 
 
# ----------------------------
# Pump control
# ----------------------------
 
def run_pump(duration=PUMP_RUN_TIME):
    print(f"Watering for {duration} seconds...")
    GPIO.output(RELAY_PIN, PUMP_ON)
    time.sleep(duration)
    GPIO.output(RELAY_PIN, PUMP_OFF)
    print("Done watering.")
 
 
# ----------------------------
# Main loop
# ----------------------------
 
def main():
    init_log()
    last_watered_time = 0
 
    print("Starting plant watering system. Press Ctrl+C to stop.")
 
    try:
        while True:
            raw_value = read_channel(SOIL_CHANNEL)
            moisture_percent = raw_to_percent(raw_value)
 
            print(f"Soil moisture: {moisture_percent:.1f}% (raw={raw_value})")
 
            watered = False
            time_since_last_watering = time.time() - last_watered_time
 
            if (moisture_percent < MOISTURE_THRESHOLD_PERCENT
                    and time_since_last_watering > MIN_TIME_BETWEEN_WATERING):
                run_pump()
                last_watered_time = time.time()
                watered = True
            elif moisture_percent < MOISTURE_THRESHOLD_PERCENT:
                print("Soil is dry, but skipping watering to avoid overwatering "
                      f"(last watered {int(time_since_last_watering)}s ago).")
 
            log_reading(raw_value, moisture_percent, watered)
            time.sleep(CHECK_INTERVAL)
 
    except KeyboardInterrupt:
        print("\nStopping. Cleaning up GPIO...")
 
    finally:
        GPIO.output(RELAY_PIN, PUMP_OFF)
        GPIO.cleanup()
        spi.close()
 
 
if __name__ == "__main__":
    main()
