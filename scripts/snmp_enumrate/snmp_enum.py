#!/usr/bin/env python3
"""
snmpv1_enum.py

Enhanced SNMPv1 community string checker and enumerator.
Tries multiple standard OIDs to extract system info once a valid community is found.

Usage:
    python3 snmpv1_enum.py -t 192.168.5.28 -c public -p 161 -T 2
"""

import argparse
import socket
import sys
import re

def try_pysnmp_enum(target, port, community, timeout):
    try:
        from pysnmp.hlapi import (
            SnmpEngine, CommunityData, UdpTransportTarget,
            ContextData, ObjectType, ObjectIdentity, getCmd
        )
    except Exception:
        return None, "pysnmp not installed"

    # Common OIDs for system information (SNMPv1 MIB-II)
    oids = {
        "sysDescr": "1.3.6.1.2.1.1.1.0",
        "sysObjectID": "1.3.6.1.2.1.1.2.0",
        "sysUpTime": "1.3.6.1.2.1.1.3.0",
        "sysContact": "1.3.6.1.2.1.1.4.0",
        "sysName": "1.3.6.1.2.1.1.5.0",
        "sysLocation": "1.3.6.1.2.1.1.6.0",
    }

    results = {}
    success = False

    for name, oid in oids.items():
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(community, mpModel=0),  # SNMPv1
                UdpTransportTarget((target, port), timeout=timeout, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

            if errorIndication:
                continue
            if errorStatus:
                continue
            for o, v in varBinds:
                results[name] = str(v.prettyPrint())
                success = True
        except Exception:
            continue

    if success:
        formatted = "\n".join([f"{k}: {v}" for k, v in results.items()])
        return True, f"SNMPv1 enumeration succeeded:\n{formatted}"
    else:
        return False, "no valid responses for standard OIDs"

def raw_udp_check(target, port, community, timeout):
    """Fallback SNMPv1 GetRequest test via raw UDP."""
    import binascii

    suffix_hex = "a01c02040eb376f4020100020100300e300c06082b060102010105000500"
    community_bytes = community.encode('utf-8')
    comm_len = len(community_bytes)
    rest = bytes.fromhex(suffix_hex)

    # Build SNMPv1 packet
    inner = bytearray()
    inner += b'\x02\x01\x00'                 # version = 0
    inner += b'\x04' + bytes([comm_len])     # community string length
    inner += community_bytes
    inner += rest
    total_len = len(inner)
    payload = b'\x30' + bytes([total_len]) + bytes(inner)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(payload, (target, port))
        data, addr = sock.recvfrom(4096)
    except socket.timeout:
        return False, "no response (timeout)"
    except Exception as e:
        return False, f"socket error: {e}"
    finally:
        sock.close()

    printable = ''.join(ch if 32 <= ch < 127 else '.' for ch in data)
    runs = re.findall(r'[ -~]{4,}', printable)
    snippet = runs[0] if runs else printable[:200]

    if community.encode() in data:
        return True, f"response contains community '{community}'. Printable snippet: {snippet}"
    elif runs:
        return True, f"response received (no community string visible): {snippet}"
    else:
        return False, f"received {len(data)} bytes but no printable content"

def main():
    parser = argparse.ArgumentParser(description="Enumerate SNMPv1 community string (public by default).")
    parser.add_argument('-t', '--target', required=True, help='Target IP or hostname')
    parser.add_argument('-p', '--port', type=int, default=161, help='UDP port (default 161)')
    parser.add_argument('-c', '--community', default='public', help='Community string (default: public)')
    parser.add_argument('-T', '--timeout', type=int, default=2, help='Timeout seconds (default: 2)')
    args = parser.parse_args()

    print(f"[+] Testing SNMPv1 community '{args.community}' on {args.target}:{args.port}")

    ok, info = try_pysnmp_enum(args.target, args.port, args.community, args.timeout)
    if ok is True:
        print(f"[+] Valid community string detected.\n{info}")
        sys.exit(0)
    elif ok is None:
        print(f"[!] pysnmp not available, falling back to raw UDP check.")
    else:
        print(f"[-] pysnmp attempt failed: {info}. Falling back to raw UDP.")

    ok2, info2 = raw_udp_check(args.target, args.port, args.community, args.timeout)
    if ok2:
        print(f"[+] Raw UDP response received. {info2}")
        sys.exit(0)
    else:
        print(f"[-] No valid response. {info2}")
        sys.exit(2)

if __name__ == "__main__":
    main()
