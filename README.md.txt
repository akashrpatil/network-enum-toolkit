# LDAP Anonymous Login Detector

A simple Python script to detect whether an **LDAP server allows anonymous bind** (login without credentials).  
Anonymous binds can expose sensitive directory information and should be disabled unless explicitly intended.

---

## 🚀 Features
- Detects anonymous LDAP binds (plain LDAP / LDAPS / StartTLS)
- Collects basic metadata such as naming contexts and root DSE info
- Supports human-readable or JSON output for automation
- Reports timings and error details for debugging
- Compatible with Python 3.8+

---

## 🧰 Installation

Clone the repository and install dependencies:
```bash
git clone https://github.com/akashrpatil/ldap-anonymous-login-detect.git
cd ldap-anonymous-login-detect
pip install -r requirements.txt