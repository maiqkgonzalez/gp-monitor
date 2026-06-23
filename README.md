# GP-Monitor

A lightweight monitoring tool for **Palo Alto Networks GlobalProtect** firewalls. It polls the firewall API at configurable intervals, stores connected-user counts in a local SQLite database, and exposes an interactive web dashboard for trend visualization.

> **Disclaimer:** This is a personal project built for learning and portfolio purposes. It is provided *as-is*, with no guarantees of functionality, maintenance, security, or fitness for any particular purpose. **Use in production environments is entirely at your own risk.**

---

## Features

- Polls one or more GlobalProtect firewalls simultaneously via their REST API
- Supports filtering by specific gateway(s) or monitoring all gateways at once
- Persists historical data in a local SQLite database (no external DB required)
- Interactive Streamlit dashboard with time-series charts and per-firewall/gateway filters
- Configurable polling interval (in minutes)
- Rotating log file for monitoring service activity (`gp_monitor.log`, 2 MB × 5 backups)
- Handles firewalls with self-signed SSL certificates

---

## Requirements

- Python 3.9+
- Network access to your GlobalProtect firewall management API
- A valid GlobalProtect API key for each firewall

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/maiqkgonzalez/gp-monitor.git
cd gp-monitor

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your configuration file (see Configuration section below)
cp config.yaml.example config.yaml   # edit with your firewall details

# 5. Initialize the database
python3 database.py
```

---

## Configuration

Create a `config.yaml` file in the project root. **This file is gitignored — never commit API keys.**

```yaml
firewalls:
  - name: fw-datacenter-01       # Friendly name (used in the dashboard)
    host: 192.168.1.1            # Firewall IP or hostname
    api_key: YOUR_API_KEY_HERE   # GlobalProtect API key

  - name: fw-branch-01
    host: 10.0.0.1
    api_key: YOUR_API_KEY_HERE
    gateway: "Branch-GW"         # Optional: monitor a single gateway

  - name: fw-hq-01
    host: 10.10.0.1
    api_key: YOUR_API_KEY_HERE
    gateway:                     # Optional: monitor multiple specific gateways
      - "HQ-GW-North"
      - "HQ-GW-South"

interval: "10"                   # Polling interval in minutes
```

**`gateway` field behaviour:**

| Value | Effect |
|-------|--------|
| `null` / omitted | Counts users across all gateways (one record per cycle) |
| `"GatewayName"` | Monitors only that gateway |
| `["GW-A", "GW-B"]` | Monitors each gateway separately |

### Obtaining an API Key

```bash
curl -k -X GET "https://<firewall-ip>/api/?type=keygen&user=<admin-user>&password=<password>"
```

---

## Usage

### Monitoring service (recommended: systemd)

The recommended way to run `main.py` on Linux is as a systemd service so it starts automatically on boot and restarts on failure.

**1. Create the unit file**

```bash
sudo nano /etc/systemd/system/gp-monitor.service
```

```ini
[Unit]
Description=GlobalProtect Monitor
After=network.target

[Service]
Type=simple
User=YOUR_LINUX_USER
WorkingDirectory=/path/to/gp-monitor
ExecStart=/path/to/gp-monitor/.venv/bin/python3 main.py
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

**2. Enable and start the service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable gp-monitor   # start on boot
sudo systemctl start gp-monitor
```

**3. Useful commands**

```bash
sudo systemctl status gp-monitor   # check status
sudo systemctl stop gp-monitor     # stop the service
sudo systemctl restart gp-monitor  # restart the service
journalctl -u gp-monitor -f        # follow systemd logs
```

Activity is also logged to `gp_monitor.log` in the project directory (rotating, 2 MB × 5 backups).

### Dashboard (on-demand)

The Streamlit dashboard is meant to be launched manually whenever you want to visualize the collected data — there is no need to keep it running continuously.

```bash
cd /path/to/gp-monitor
source .venv/bin/activate
streamlit run app.py
```

The dashboard opens automatically in your browser at `http://localhost:8501`.

---

## Project Structure

```
gp-monitor/
├── main.py              # Entry point — monitoring loop
├── app.py               # Streamlit dashboard
├── config_reader.py     # Parses config.yaml
├── api_connector.py     # HTTPS requests to firewall API
├── data_processor.py    # XML parsing and record building
├── database.py          # SQLite writes (INSERT)
├── db_reader.py         # SQLite reads (SELECT) for the dashboard
├── config.yaml          # Your configuration (gitignored)
├── users_gp.db          # SQLite database (gitignored)
├── gp_monitor.log       # Rotating log file (gitignored)
└── requirements.txt
```

### How it works

```
main.py
  └── config_reader.py   → reads config.yaml (firewall list, interval)
  └── api_connector.py   → HTTPS GET to each firewall, returns raw XML
  └── data_processor.py  → counts <entry> tags per gateway in the XML
  └── database.py        → INSERT (timestamp, users, firewall, gateway, status)

app.py (Streamlit)
  └── db_reader.py       → SELECT with date/firewall/gateway filters
  └── Altair charts + Pandas DataFrames rendered in browser
```

### Database schema (`records` table)

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key, autoincrement |
| `timestamp` | TEXT | `YYYY-MM-DD HH:MM:SS` |
| `users` | INTEGER | Connected user count |
| `firewall` | TEXT | Firewall name from config |
| `gateway` | TEXT | Gateway name (nullable) |
| `status` | TEXT | `"connected"` or `"disconnected"` |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.9+ |
| Dashboard | [Streamlit](https://streamlit.io/) |
| Charts | [Altair](https://altair-viz.github.io/) |
| Data | Pandas, SQLite |
| HTTP | Requests |
| Config | PyYAML |

---

## Security Notes

- SSL verification is **disabled** (`verify=False`) to support firewalls with self-signed certificates. Do not expose the monitoring service to untrusted networks.
- API keys are stored in plain text in `config.yaml`. Ensure proper file permissions (`chmod 600 config.yaml`) and never commit this file.
- This tool makes **read-only** API calls — it does not modify any firewall configuration.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Miguel Gonzalez

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**
