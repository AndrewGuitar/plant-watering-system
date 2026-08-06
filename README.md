# Automated Plant Watering System

A Raspberry Pi-based irrigation system that monitors soil moisture in real time and automatically waters a plant when it gets too dry. Built as a hands-on embedded systems and Python project.

## Overview

This project automates plant watering using a Raspberry Pi 4, a capacitive soil moisture sensor, and a relay-controlled pump. 

## How It Works

1. The soil moisture sensor outputs an analog voltage based on soil conductivity.
2. The MCP3008 analog-to-digital converter reads that analog signal over SPI and converts it into a digital value the Pi can process.
3. A Python script continuously reads this value and compares it against a calibrated moisture threshold.
4. If the soil is too dry, the script triggers a relay, which switches on a USB water pump.
5. A cooldown timer prevents the system from repeatedly triggering the pump in short succession (avoiding overwatering).
6. Every reading and pump activation is logged to a CSV file with timestamps.
7. A separate script reads that CSV and generates a moisture-over-time chart, marking when the pump activated.

## Hardware

| Component | Model |
|---|---|
| Microcontroller | Raspberry Pi 4 Model B (2GB) |
| ADC | MCP3008 (Bridgold) |
| Soil Moisture Sensor | YELUFT Capacitive Soil Moisture Sensor v2.0 |
| Relay Module | AEDIKO Relay Module |
| Pump | PULACO USB Submersible Pump |

## Wiring

**MCP3008 → Raspberry Pi (SPI)**
| MCP3008 Pin | Connects To |
|---|---|
| CLK | GPIO11 (SPI0 SCLK) |
| DOUT | GPIO9 (SPI0 MISO) |
| DIN | GPIO10 (SPI0 MOSI) |
| CS/SHDN | GPIO8 (SPI0 CE0) |
| VDD | 3.3V |
| VREF | 3.3V |
| AGND | GND |
| DGND | GND |
| CH0 | Soil moisture sensor analog output |

**Notes:**
- All grounds (Pi, MCP3008, relay, sensor) share a common ground rail.
- The pump draws power from a separate USB power source, not directly from the Pi, to avoid current draw issues.

## Repo Structure

- `plant_watering.py` — Main control script. Reads soil moisture via the MCP3008 in a loop, applies threshold logic, controls the relay/pump, includes a cooldown timer, and logs readings to CSV.
- `plot_moisture.py` — Reads the CSV log and generates a time-series chart of moisture levels, with markers showing when the pump was activated.

## Setup & Usage

**Requirements:** Raspberry Pi with SPI enabled, Python 3, `spidev`, `RPi.GPIO`, `matplotlib`

1. Enable SPI on the Pi via `raspi-config` (Interface Options → SPI → Enable).
2. Clone this repo directly onto the Raspberry Pi (the scripts rely on GPIO/SPI hardware access and will not run on a Windows/Mac laptop):
```bash
   git clone <your-repo-url>
   cd <repo-folder>
```
3. Install dependencies:
```bash
   pip install spidev RPi.GPIO matplotlib
```
4. Run the main watering script:
```bash
   python3 plant_watering.py
```
5. Once you have logged data, generate a moisture chart:
```bash
   python3 plot_moisture.py
```

