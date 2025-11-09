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

## 📁 Project Structure

```text
fortigate-cis-audit/
│
├── README.md
├── LICENSE
│
├── scripts/
│   ├── run_full_fortigate_audit_wsl.sh       # Main automation runner (multi-config + HTML)
│   └── fortigate_cis_audit.sh                # Core CIS audit logic (from Priyam001)
│
├── configs/
│   ├── example.conf                          # Sample FortiGate config (for demo)
│   ├── example.cfg
│   └── (place all your .conf / .cfg files here)
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
│   │   └── fortigate_audit_summary.html      # ✅ Combined compliance report
│   └── (this folder is created automatically when the script runs)
│
└── .gitignore
```
---


**🧰 Requirements**
Linux / WSL environment

Utilities: bash, grep, awk, sed, find, dos2unix
Executable fortigate_cis_audit.sh script

Optional: Google Chrome or Firefox to view HTML reports

---

**🧩 Example Combined Dashboard**
```
Benchmark           	HQ-FW	  DC-FW	   SiteA
DNS Server Configured	✅ PASS	✅ PASS	❌ FAIL
Pre-Login Banner Set	✅ PASS	❌ FAIL	✅ PASS
NTP Timezone Set	    ❌ FAIL	✅ PASS	✅ PASS
```
---
## 🧠 Credits

This project builds upon the open-source work from  
**[Priyam001 – Fortigate_CIS_check](https://github.com/priyam001/Fortigate_CIS_check)**  

Original audit logic © Priyam001 (MIT License).  
Automation framework, HTML reporting, and multi-file support developed by **Akash Rajendra Patil**.  

Benchmark Reference:  
Based on the [CIS FortiGate Benchmark](https://www.cisecurity.org/benchmark/fortinet_fortigate).

Portions of this project are derived from:
"Fortigate_CIS_check" by Priyam001 (https://github.com/priyam001/Fortigate_CIS_check)
Licensed under the MIT License.

---

Modifications and extensions:
© 2025 Akash Rajendra Patil
- Added multi-file automation and reporting
- WSL compatibility and combined HTML dashboard
