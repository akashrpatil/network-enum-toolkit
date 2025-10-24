# Protocol Enum Toolkit

A collection of small Python scripts to detect service misconfigurations and exposures (LDAP, SNMP, SMB, etc.).  
Each script performs lightweight enumeration and outputs JSON/human-readable results.

---

## 🧰 Installation

```bash
git clone https://github.com/akashrpatil/protocol-enum-toolkit.git
cd protocol-enum-toolkit
pip install -r requirements.txt
```

🧑‍💻 Usage

Run the script against a target LDAP host:
```
Basic LDAP (default port 389)
python ldap_anonymous_check.py --host ldap.example.com
```
```
LDAPS (SSL, port 636)
python ldap_anonymous_check.py --host ldap.example.com --use-ldaps
```
```
StartTLS upgrade (port 389)
python ldap_anonymous_check.py --host ldap.example.com --starttls
```
```
Machine-friendly JSON output
python ldap_anonymous_check.py --host ldap.example.com --json
```
🧾 Example Output
✅ Anonymous Bind Allowed
```
Anonymous LDAP bind: ALLOWED
Host: ldap.example.com:389  LDAPS=False  StartTLS=False
Timings (s): {'tcp_connect_s': 0.045, 'bind_s': 0.12, 'total_s': 0.17}
Metadata (partial):
 - rootDSE: {'namingContexts': ['dc=example,dc=com']}
```

❌ Anonymous Bind Not Allowed
```
Anonymous LDAP bind: NOT ALLOWED
Error / details: Bind failed: {'result': 49, 'description': 'invalidCredentials'}
```

⚙️ Command Options

```
Option	Description
--host / -H	Target hostname or IP (supports ldap:// or ldaps://)
--port / -p	Custom port (default 389 or 636 for LDAPS)
--use-ldaps	Use LDAPS (connect via SSL)
--starttls	Use StartTLS (upgrade plain LDAP connection to TLS)
--timeout	Connection timeout in seconds (default: 5)
--json	Output JSON format (for automation)
```

🔍 Example Automation

```
Run against multiple hosts:

while read host; do
  python ldap_anonymous_check.py --host "$host" --json | jq '. | {host, success}'
done < targets.txt
```

📦 Output Fields (JSON)

```
Field	Description
success	true if anonymous bind succeeded
error	LDAP error message (if any)
metadata.rootDSE	Root DSE information from the server
metadata.server_info	Server capabilities/info (if available)
timings	Connection and bind times (in seconds)
```

⚠️ Disclaimer

```
Use this tool only on systems you own or have explicit authorization to test.
Unauthorized testing of LDAP servers is illegal and unethical.
```

👨‍💻 Author

```
Developed by Akash Rajendra Patil

Cyber Security Professional — Red Teaming | Cloud | Infrastructure | Application
```

🤝 Contributing

```
Pull requests and suggestions are welcome!
If you find issues, open a GitHub issue with the command and output snippet.
```

🪪 License

```
MIT License — see LICENSE
 for details.
```
