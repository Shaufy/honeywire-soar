Agentic AI Deception & SOAR Platform
An automated threat monitoring and response architecture combining containerized network deception, SIEM log aggregation, and local AI threat analysis using Ollama and Meta Llama 3.2 3B.

🏗 Architecture Overview
Deception & SIEM: Containerized HoneyWire stack captures network interactions and streams runtime logs to stdout.

Telemetry Pipeline: A non-blocking UNIX pipe forwards log streams directly into the Python SOAR agent.

Local AI Analysis: The SOAR agent invokes a local Ollama instance running llama3.2:3b to categorize attack vectors and output standardized JSON incident logs.

Operations Dashboards: Integrated web UIs monitor system state across ports 8888, 8081, and 8080.

🚀 Prerequisites
OS: Ubuntu 22.04 LTS or newer

Containerization: Docker Engine & Docker Compose

Local AI: Ollama with llama3.2:3b pulled (ollama pull llama3.2:3b)

Python: Python 3.10+

📦 Quick Start
Clone the repository:

Bash
git clone [https://github.com/Shaufy/honeywire-soar.git](https://github.com/Shaufy/honeywire-soar.git)
cd honeywire-soar
Set up virtual environment & install dependencies:

Bash
python3 -m venv soar-venv
source soar-venv/bin/activate
pip install -r src/requirements.txt
Make startup scripts executable:

Bash
chmod +x scripts/start_soar.sh
Launch the platform:

Bash
./scripts/start_soar.sh
📜 License
MIT
