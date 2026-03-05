# Recon Orchestrator

Recon Orchestrator is a lightweight automation toolkit that installs and manages commonly used reconnaissance tools for penetration testing, bug bounty hunting, and security research.

It simplifies the process of setting up a complete recon environment by automatically installing and verifying multiple tools used during the reconnaissance phase of security testing.

---

# Table of Contents

* Features
* Supported Tools
* Requirements
* Installation
* Command Line Flags
* Usage Examples
* Project Structure
* Troubleshooting
* Security Notice
* License

---

# Features

* Automated installation of reconnaissance tools
* Dependency verification after installation
* Supports tools installed via **APT**, **Go**, and **npm**
* Dry-run mode to preview installation steps
* Designed for **Kali Linux environments**
* Simplifies recon environment setup for security researchers

---

# Supported Tools

## Network & Port Scanning

* nmap
* masscan
* rustscan

## Subdomain Enumeration

* subfinder
* amass
* assetfinder

## Web Discovery

* httpx
* httprobe

## Technology Detection

* whatweb
* wafw00f
* wappalyzer

## Visual Recon

* EyeWitness

---

# Requirements

* Kali Linux (recommended)
* Python **3.9+**
* sudo privileges
* Internet connection

---

# Installation

## Clone the Repository

```
git clone https://github.com/Prometheus918/recon-orchestrator.git
cd recon-orchestrator
```

## Run Installer

```
python3 install.py
```

The installer will:

1. Update system packages
2. Install required APT packages
3. Install Go-based tools
4. Install npm-based tools
5. Verify tool installation

---


# Usage Examples

python3 recon_orchestrator.py -f domains.txt -o recon_output --parallel-domains 12

# Troubleshooting

If tools are not found:

```
export PATH=$PATH:$HOME/go/bin
```

If npm permission errors occur:

```
sudo npm install -g wappalyzer
```

Update packages:

```
sudo apt update
```

---

# Security Notice

This tool is intended **only for authorized security testing and educational purposes**.

Do not run scans against systems without permission.

---

# License

https://github.com/Prometheus918/Recon-Orchestrator/blob/main/LICENSE

---

# Author

Rohit Date
GitHub: https://github.com/Prometheus918
