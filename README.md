# Agentic AI Deception & SOAR Platform

An automated threat monitoring and response architecture combining containerized network deception, SIEM log aggregation, and local AI threat analysis using Ollama and Meta Llama 3.2 3B.

## 🏗 Architecture Overview

1. **Deception & SIEM**: Containerized HoneyWire stack captures network interactions and streams runtime logs to `stdout`.
2. **Telemetry Pipeline**: A non-blocking UNIX pipe forwards log streams directly into the Python SOAR agent.
3. **Local AI Analysis**: The SOAR agent invokes a local Ollama instance running `llama3.2:3b` to categorize attack vectors and output standardized JSON incident logs.
4. **Operations Dashboards**: Integrated web UIs monitor system state across ports `8888`, `8081`, and `8080`.

## 🚀 Prerequisites

- **OS**: Ubuntu 22.04 LTS or newer
- **Containerization**: Docker Engine & Docker Compose
- **Local AI**: Ollama with `llama3.2:3b` pulled (`ollama pull llama3.2:3b`)
- **Python**: Python 3.10+

## 📦 Quick Start

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/Shaufy/honeywire-soar.git](https://github.com/Shaufy/honeywire-soar.git)
   cd honeywire-soar
