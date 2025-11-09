# 🛡️ FortiGate CIS Configuration Audit Automation

Automated auditing of FortiGate firewall configuration files (`.conf` / `.cfg`) against CIS security benchmarks — generates individual HTML reports and a unified compliance dashboard.

---

## 🚀 Features

- ✅ Runs `fortigate_cis_audit.sh` automatically on all configs in a folder  
- ✅ Parses PASS / FAIL / Manual results from CIS checks  
- ✅ Creates clean **individual HTML reports** per device  
- ✅ Builds a **combined HTML compliance dashboard** across all configs  
- ✅ Handles WSL / Windows line endings (CRLF → LF)  
- ✅ Handles file names with spaces or parentheses  
- ✅ Logs missing / invalid configs as “No Data”

---

## 🧰 Requirements

- **WSL / Linux environment**
- `bash`, `grep`, `awk`, `sed`, `find`, `dos2unix`
- Executable copy of `fortigate_cis_audit.sh`

> Tested on WSL2 (Ubuntu 22.04) running on Windows 10/11.

---

## 📂 Folder Structure
fortigate-cis-audit/
│
├── README.md
├── LICENSE
│
├── scripts/
│   ├── run_full_fortigate_audit_wsl.sh       # Main automation runner (the one we built)
│   └── fortigate_cis_audit.sh                # Your CIS audit logic
│
├── configs/
│   ├── example.conf                          # Sample FortiGate config (for demo)
│   ├── example.cfg
│   └── (place all .conf / .cfg files here)
│
├── reports/
│   ├── combined_outputs/                     # Auto-generated folder (per device)
│   │   ├── DC-FW/
│   │   │   ├── DC-FW_output.txt
│   │   │   └── DC-FW_output.html
│   │   ├── HQ-FW/
│   │   │   ├── HQ-FW_output.txt
│   │   │   └── HQ-FW_output.html
│   │   ├── SiteA/
│   │   │   ├── SiteA_output.txt
│   │   │   └── SiteA_output.html
│   │   └── fortigate_audit_summary.html      # ✅ Combined report
│   └── (this folder is created automatically when script runs)
│
└── .gitignore
