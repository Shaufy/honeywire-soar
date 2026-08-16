#!/bin/bash

# 1. Start honeypot core
honey start > /dev/null 2>&1

# 2. Start SIEM containers
sudo docker start honeywire-siem siem-dashboard > /dev/null 2>&1

# 3. Open Web UI Dashboards in Browser
(sleep 2 && xdg-open http://localhost:8888/container/ && xdg-open http://localhost:8081/ && xdg-open http://localhost:8080/dashboard) &

# 4. Stream logs into SOAR agent (foreground)
sudo docker compose -f ../docker/honeywire-compose.yml -p honeywire logs -f --tail 0 | ~/soar-venv/bin/python3 ../src/soar_agent.py

exec bash
