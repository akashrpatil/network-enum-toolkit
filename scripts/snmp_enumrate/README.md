# SNMPv1 Enumerator - snmpv1_enumerate.py

Enhanced SNMPv1 enumeration tool that tests SNMPv1 community strings and, when valid,
collects useful device information (sys*, interfaces, ARP, vendor OIDs, etc).

> **Safe by default**: read-only enumeration only - no `snmpset` or destructive actions.
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
```
---

## Usage

**Basic check and pretty output:**
```
python3 snmpv1_enumerate.py -t 10.0.0.5 -c public --pretty
```

**Write full JSON output to a file:**
```
python3 snmpv1_enumerate.py -t 10.0.0.5 -c public --json-out artifacts/10.0.0.5-snmp.json
```

**Get extra OIDs (comma-separated):**
```
python3 snmpv1_enumerate.py -t 10.0.0.5 -c public --oids 1.3.6.1.2.1.1.1.0,1.3.6.1.2.1.1.5.0 --pretty
```

**Walk tables (may be noisy) and limit rows:**
```
python3 snmpv1_enumerate.py -t 10.0.0.5 -c public --walk --max-rows 100 --pretty
```
---

## Help / all options:
```
python3 snmpv1_enumerate.py -h

Example workflow (authorized testing)
- Test candidate community string(s) with this tool.
- If valid, save the JSON output as evidence.
- Correlate sysName/sysDescr with inventory and prioritize high-impact devices (core routers, firewalls).
- Do not perform snmpset (write) unless explicitly authorized; get written permission first.
- Output / Evidence
- JSON output contains:
- target, port, community, detection_method
- sys (sysDescr, sysName, sysContact, sysLocation, sysUpTime)
- interfaces (index, ifDescr, ifOperStatus)
- arp (ipNetToMediaTable samples)
- vendor_oids (sample under .1.3.6.1.4.1)
- extra_oids (user requested OIDs)
- Use the JSON for reporting and remediation recommendations.
```
---

## Remediation (recommended)
```
- Disable SNMPv1/v2c where possible; migrate to SNMPv3 (authPriv).
- Replace default community strings (public/private) with unique values.
- Restrict SNMP access to management hosts (collector IPs) via ACLs/firewall.
- Use read-only communities unless write is strictly required.
- Log and monitor SNMP activity for unexpected sources/rate.
```
