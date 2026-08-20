# 🛡️ HoneyWire SOAR — Agentic Threat Engine

HoneyWire SOAR is an automated, AI-driven Security Operations Center (SOC) triage and response engine designed to capture, analyze, and mitigate threat telemetry originating from honeypot sensors in real time.

By integrating local LLM inference (**Ollama / Llama 3.2**) with automated local Linux firewall enforcement (**iptables**) and incident notifications (**Discord Webhooks**), HoneyWire SOAR eliminates manual triage overhead for routine attack signatures.

---

## 📐 System Architecture

```text
[ Sensor / Log Telemetry ]
           │ (stdin stream)
           ▼
┌──────────────────────────────────────┐
│       HoneyWire SOAR Engine          │
│                                      │
│  1. Extract & Validate IP           │
│  2. Check Subnet Whitelist           │
│  3. Consult Local Llama 3.2 Model    │
└──────────────────┬───────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌─────────────────┐ ┌──────────────────┐
│ Fire-and-Forget │ │  Block Enforced  │
│ Low/Ignored     │ │ (iptables DROP)  │
└─────────────────┘ └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Discord SOC Alert│
                    └──────────────────┘

```

---

## 🛠️ Key Features

* **Agentic AI Triage**: Evaluates unstructured log strings using a local **Llama 3.2** model via Ollama to determine attack vectors, threat severity, and required response actions.
* **Granular Whitelisting**: Suppresses internal network noise (`127.0.0.1`, `10.0.2.2`, `192.168.x.x`) prior to invoking AI models.
* **Automated Mitigation**: Automatically appends `iptables DROP` rules to both `INPUT` and `DOCKER-USER` chains upon detecting high-severity attacks requiring blocking.
* **Real-time Incident Response**: Sends structured, color-coded threat embeds to a designated Discord SOC channel via webhooks.
* **Fail-Safe Fallbacks**: Handles model timeouts and output formatting anomalies gracefully using robust JSON regex cleaning and structured safety rules.

---

## 📋 Prerequisites

Before running the SOAR agent, ensure the host machine meets the following environment requirements:

* **OS**: Ubuntu Server 22.04 LTS / 24.04 LTS
* **Python**: Python 3.10+
* **System Packages**: `iptables`, `sudo` privileges for active network manipulation
* **Local LLM Engine**: [Ollama](https://ollama.com/) installed and serving `llama3.2`

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Shaufy/honeywire-soar.git
cd honeywire-soar

```

### 2. Configure Python Environment & Dependencies

Install required Python modules:

```bash
pip install -r src/requirements.txt --break-system-packages

```

### 3. Pull the Local LLM Model

Ensure Ollama is active and pull the lightweight Llama 3.2 model:

```bash
ollama pull llama3.2

```

### 4. Configure Environment Variables

Create a `.env` configuration file in the project root to store sensitive environment secrets securely:

```bash
cat << 'EOF' > .env
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
EOF

```

> **Security Note**: Ensure `.env` is listed inside `.gitignore` to prevent secret leaks to public repositories.

---

## 🚀 Execution & Usage

### Interactive Telemetry Stream Test

Pipe real-time log stream data into the engine:

```bash
echo "203.0.113.45 - login attempt failed for root" | python3 src/soar_agent.py

```

### Simulated Output Stream

```text
[🤖] Agentic AI Threat Engine active. Awaiting sensor telemetry...

[⚡ INTEL EVENT] Threat signature captured from 203.0.113.45
[🤖 AGENT CONSULTATION] Querying local Llama 3.2 model for triage...
  ├─ Severity    : HIGH
  ├─ Vector      : SSH Bruteforce
  ├─ AI Decision : BLOCK
  └─ Reason      : Multiple failed root logins indicate unauthorized access attempts.
[✔ ACTION EXECUTION] Successfully applied firewall block against 203.0.113.45

```

---

## 📂 Repository Structure

```text
honeywire-soar/
├── docker/
│   └── honeywire-compose.yml   # Multi-container sensor environment setup
├── scripts/
│   └── start_soar.sh           # System service startup launcher
├── src/
│   ├── soar_agent.py          # Primary SOAR Triage & Response Engine
│   └── requirements.txt        # Python package dependencies
├── .env                        # Local environment variables (Git ignored)
├── .gitignore                  # Git exclusions tracking file
├── LICENSE                     # Project licensing details
└── README.md                   # Project documentation

```

---

## 🔒 Security & Best Practices

1. **Environment Separation**: Secrets like Discord webhook URIs should never be hardcoded in Python source files. Always load parameters using `python-dotenv`.
2. **Git History Hygiene**: If credentials are accidentally committed, use `git-filter-repo` to scrub secrets across all historical commits and revoke the exposed API/Webhook tokens immediately at the source.
3. **Least Privilege System Rights**: Configure `sudoers` rules strictly for `iptables` execution commands if running the script under a non-root system user.
