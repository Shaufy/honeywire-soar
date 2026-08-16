#!/usr/bin/env python3
import sys
import json
import subprocess
import requests
import re
import ollama

# Configuration
WEBHOOK_URL = "REMOVED_SECRET"
WHITELIST_PATTERN = r"127\.0\.0\.1|10\.0\.2\.2|192\.168\."

def is_whitelisted(ip):
    return bool(re.search(WHITELIST_PATTERN, ip))

def extract_ip(log_line):
    match = re.search(r'([0-9]{1,3}\.){3}[0-9]{1,3}', log_line)
    return match.group(0) if match else None

def block_ip(ip):
    """Tool: Inserts iptables rule to drop attacker IP"""
    try:
        # Check if already blocked
        check_cmd = f"sudo iptables -C DOCKER-USER -s {ip} -j DROP"
        res = subprocess.run(check_cmd, shell=True, stderr=subprocess.DEVNULL)
        if res.returncode != 0:
            subprocess.run(f"sudo iptables -I DOCKER-USER -s {ip} -j DROP", shell=True, check=True)
            subprocess.run(f"sudo iptables -I INPUT -s {ip} -j DROP", shell=True, check=True)
            return True
        return False
    except Exception as e:
        print(f"[!] Error executing firewall block: {e}")
        return False

def analyze_with_ai(log_line, ip):
    """Sends log payload to local Ollama model for threat evaluation"""
    prompt = f"""
You are an expert Security Operations Center (SOC) AI Analyst monitoring a honeypot system.
Analyze the following sensor log entry and provide a threat analysis in strict JSON format.

Log Entry: "{log_line}"
Attacker IP: "{ip}"

Respond ONLY with valid JSON using this exact structure:
{{
    "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
    "attack_vector": "Brief classification (e.g., SSH Bruteforce, Web Probe, ICMP Sweep)",
    "action_required": "BLOCK" | "IGNORE" | "MONITOR",
    "reasoning": "One concise sentence explaining why this decision was made."
}}
"""
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1}  # Low temp for deterministic output
        )
        content = response['message']['content'].strip()
        # Clean potential markdown formatting from LLM output
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
        return json.loads(content)
    except Exception as e:
        print(f"[!] AI Analysis failed: {e}")
        # Fallback safety rule if LLM times out
        return {
            "severity": "HIGH",
            "attack_vector": "Automated Sensor Trigger (Fallback)",
            "action_required": "BLOCK",
            "reasoning": "Fallback trigger engaged due to AI processing error."
        }

def send_discord_alert(ip, analysis):
    """Sends an AI-generated SOC briefing to Discord"""
    color_map = {
        "CRITICAL": 15158332, # Red
        "HIGH": 15105570,     # Orange
        "MEDIUM": 1752220,    # Cyan
        "LOW": 3066993        # Green
    }
    
    payload = {
        "embeds": [{
            "title": "🤖 [AGENTIC SOAR ANALYSIS COMPLETE]",
            "color": color_map.get(analysis.get("severity"), 1752220),
            "fields": [
                {"name": "Attacker Origin IP", "value": f"`{ip}`", "inline": True},
                {"name": "Severity Rating", "value": f"**{analysis.get('severity')}**", "inline": True},
                {"name": "Identified Vector", "value": f"`{analysis.get('attack_vector')}`", "inline": False},
                {"name": "AI Executive Reasoning", "value": analysis.get('reasoning'), "inline": False},
                {"name": "Action Enforced", "value": f"🛡️ `iptables DROP ({analysis.get('action_required')})`", "inline": False}
            ]
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        print(f"[!] Discord alert failed: {e}")

def process_log_stream():
    """Reads stdin line by line from the sensor stream"""
    print("\033[1;35m[🤖] Agentic AI Threat Engine active. Awaiting sensor telemetry...\033[0m", flush=True)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # Check for trigger keywords
        if any(keyword in line.lower() for keyword in ["port probe", "login attempt", "icmp echo", "tamper detection"]):
            ip = extract_ip(line)
            if not ip:
                continue

            if is_whitelisted(ip):
                print(f"\033[1;33m[SKIP]\033[0m Whitelisted IP detected: {ip}")
                continue

            print(f"\n\033[1;36m[⚡ INTEL EVENT]\033[0m Threat signature captured from \033[1;31m{ip}\033[0m", flush=True)
            print("\033[1;34m[🤖 AGENT CONSULTATION]\033[0m Querying local Llama 3.2 model for triage...")

            analysis = analyze_with_ai(line, ip)

            print(f"  ├─ Severity    : {analysis.get('severity')}")
            print(f"  ├─ Vector      : {analysis.get('attack_vector')}")
            print(f"  ├─ AI Decision : {analysis.get('action_required')}")
            print(f"  └─ Reason      : {analysis.get('reasoning')}")

            if analysis.get('action_required') == "BLOCK":
                newly_blocked = block_ip(ip)
                if newly_blocked:
                    print(f"\033[1;32m[✔ ACTION EXECUTION]\033[0m Successfully applied firewall block against {ip}")
                    send_discord_alert(ip, analysis)
                else:
                    print(f"\033[1;30m[i] IP {ip} is already constrained by firewall.\033[0m")

if __name__ == "__main__":
    process_log_stream()
