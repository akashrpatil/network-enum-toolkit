# SNMPv1 Enumerator — snmpv1_enumerate.py

Enhanced SNMPv1 enumeration tool that tests SNMPv1 community strings and, when valid,
collects useful device information (sys*, interfaces, ARP, vendor OIDs, etc).

> **Safe by default**: read-only enumeration only — no `snmpset` or destructive actions.
> Use this tool **only** on systems you own or where you have explicit authorization.

---

## Features
- Validates SNMPv1 community strings (prefers `pysnmp`).
- Collects system info: `sysDescr`, `sysName`, `sysContact`, `sysLocation`, `sysUpTime`.
- Walks common tables (interfaces, ARP) with row limits to avoid noisy scans.
- Samples vendor enterprise OIDs (`.1.3.6.1.4.1`) to reveal device model/firmware info.
- Optional extra OIDs to query.
- Outputs JSON and optional pretty text summary.
- Raw UDP fallback if `pysnmp` is not available (heuristic detection).

---

## Installation

1. Clone your repo (or create new repo) and place `snmpv1_enumerate.py` under `scripts/` (recommended).
2. Install dependencies:
```bash
pip install -r requirements.txt
