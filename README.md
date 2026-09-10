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

- Python 3.14 (pinned via `.python-version`, Linux)
- Network access to your GlobalProtect firewall management API
- A valid GlobalProtect API key for each firewall

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/maiqkgonzalez/gp-monitor.git
cd gp-monitor

# 2. Create and activate a virtual environment (Linux)
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create your configuration files (see Configuration section below)
cp config.yaml.example config.yaml   # edit with your firewall details (no secrets)
cp .env.example .env                 # fill in real API keys
chmod 600 config.yaml .env users_gp.db

# 5. Initialize the database
python3 database.py
```

---

## Configuration

Hybrid setup: `config.yaml` holds non-sensitive data, `.env` holds secrets.
Both files are gitignored — never commit API keys.

`config.yaml`:

```yaml
firewalls:
  - name: fw-datacenter-01       # Friendly name (used in the dashboard)
    host: 192.168.1.1            # Firewall IP or hostname
    api_key_env: FW_DATACENTER_01_API_KEY  # Name of the env var in .env

  - name: fw-branch-01
    host: 10.0.0.1
    api_key_env: FW_BRANCH_01_API_KEY
    gateway: "Branch-GW"         # Optional: monitor a single gateway

  - name: fw-hq-01
    host: 10.10.0.1
    api_key_env: FW_HQ_01_API_KEY
    gateway:                     # Optional: monitor multiple specific gateways
      - "HQ-GW-North"
      - "HQ-GW-South"

interval: "10"                   # Polling interval in minutes
```

`.env`:

```dotenv
FW_DATACENTER_01_API_KEY=your_real_key_here
FW_BRANCH_01_API_KEY=your_real_key_here
FW_HQ_01_API_KEY=your_real_key_here
```

`config_reader.py` resolves `api_key_env` via `python-dotenv` at startup
and fails fast with `ValueError` if a variable is missing.

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
EnvironmentFile=/path/to/gp-monitor/.env
ExecStart=/path/to/gp-monitor/.venv/bin/python main.py
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
├── config_reader.py     # Parses config.yaml + resolves secrets from .env
├── api_connector.py     # HTTPS requests to firewall API
├── data_processor.py    # XML parsing and record building
├── database.py          # SQLite writes (INSERT)
├── db_reader.py         # SQLite reads (SELECT) for the dashboard
├── config.yaml          # Non-sensitive config, references secrets (gitignored)
├── config.yaml.example  # Template without secrets (committed)
├── .env                 # Real API keys (gitignored, chmod 600)
├── .env.example         # Template without secrets (committed)
├── gp-monitor.service.example  # systemd unit template (Linux)
├── .python-version      # Pinned Python version for venv
├── users_gp.db          # SQLite database (gitignored)
├── gp_monitor.log       # Rotating log file (gitignored)
└── requirements.txt
```

### How it works

```
main.py
  └── config_reader.py   → reads config.yaml + resolves api_key_env from .env
  └── api_connector.py   → HTTPS GET to each firewall, returns raw XML (never logs keys)
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
| Language | Python 3.14 (Linux, see `.python-version`) |
| Dashboard | [Streamlit](https://streamlit.io/) |
| Charts | [Altair](https://altair-viz.github.io/) |
| Data | Pandas, SQLite |
| HTTP | Requests |
| Config | PyYAML + python-dotenv |

---

## Security Notes

- SSL verification is **disabled** (`verify=False`) to support firewalls with self-signed certificates. Do not expose the monitoring service to untrusted networks.
- Secrets live in `.env`, not in `config.yaml`. `config.yaml` only holds `api_key_env` references. Set `chmod 600 .env config.yaml users_gp.db` and never commit `.env`/`config.yaml` (both gitignored).
- API keys/URLs are never logged (`api_connector.py` deliberately avoids logging `params`/`url`).
- This tool makes **read-only** API calls — it does not modify any firewall configuration.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Miguel Gonzalez

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**
