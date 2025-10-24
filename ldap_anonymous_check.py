#!/usr/bin/env python3
"""
ldap_anonymous_check.py

Detect whether an LDAP server allows anonymous bind (login without credentials).
Outputs a JSON result with success flag and metadata.

Usage:
    python ldap_anonymous_check.py --host ldap.example.com --port 389
    python ldap_anonymous_check.py --host ldap://ldap.example.com --port 389 --starttls
    python ldap_anonymous_check.py --host ldap.example.com --use-ldaps --port 636

"""
import argparse
import json
import socket
import time
from ldap3 import Server, Connection, ALL, ANONYMOUS, BASE, ALL_ATTRIBUTES
from ldap3.core.exceptions import LDAPExceptionError, LDAPSocketOpenError

def normalize_host(host_arg):
    # Allow passing ldap:// or ldaps:// or plain hostname
    if host_arg.startswith('ldap://') or host_arg.startswith('ldaps://'):
        # strip scheme, keep hostname (and optional port)
        return host_arg.split('://', 1)[1]
    return host_arg

def try_anonymous_bind(host, port, use_ldaps=False, starttls=False, timeout=5):
    result = {
        "host": host,
        "port": port,
        "use_ldaps": use_ldaps,
        "starttls": starttls,
        "success": False,
        "error": None,
        "metadata": {},
        "timings": {}
    }

    start_time = time.time()
    try:
        # Quick TCP check for connectivity
        tcp_start = time.time()
        with socket.create_connection((host, port), timeout=timeout):
            pass
        tcp_end = time.time()
        result["timings"]["tcp_connect_s"] = round(tcp_end - tcp_start, 4)
    except Exception as e:
        result["error"] = f"TCP connection failed: {e}"
        result["timings"]["total_s"] = round(time.time() - start_time, 4)
        return result

    try:
        server = Server(host, port=port, use_ssl=use_ldaps, get_info=ALL, connect_timeout=timeout)
    except Exception as e:
        result["error"] = f"Server object creation failed: {e}"
        result["timings"]["total_s"] = round(time.time() - start_time, 4)
        return result

    conn = None
    try:
        bind_start = time.time()
        conn = Connection(server,
                          authentication=ANONYMOUS,
                          receive_timeout=timeout,
                          read_only=True)
        # open
        if not conn.open():
            raise LDAPSocketOpenError("Failed to open connection to server")

        # If StartTLS requested (and not using LDAPS)
        if starttls:
            if use_ldaps:
                # contradictory options: StartTLS over LDAPS not valid
                raise ValueError("Cannot use StartTLS when using LDAPS (use one or the other).")
            if not conn.start_tls():
                raise LDAPExceptionError(f"StartTLS failed: {conn.last_error}")

        # attempt anonymous bind
        if not conn.bind():
            # bind failed - anonymous not allowed
            result["success"] = False
            result["error"] = f"Bind failed: {conn.result}"
        else:
            # bind succeeded
            result["success"] = True
            # collect metadata
            try:
                # server info (may be empty depending on discovery)
                server_info = {}
                if server.info:
                    # Server.info may be large objects; convert to dict where possible
                    try:
                        server_info = server.info.to_dict()
                    except Exception:
                        # fallback: list available attributes
                        server_info = {
                            "schema": str(server.schema),
                            "server_name": str(server)
                        }
                result["metadata"]["server_info"] = server_info
            except Exception as e:
                result["metadata"]["server_info_error"] = str(e)

            # try to read root DSE for namingContexts and other attributes
            try:
                # base search at root DSE
                if conn.search(search_base='', search_filter='(objectClass=*)', search_scope=BASE,
                               attributes=['namingContexts', 'defaultNamingContext', 'rootDomainNamingContext']):
                    entry = conn.entries[0]
                    # Use entry.entry_attributes_as_dict for a clean mapping
                    try:
                        result["metadata"]["rootDSE"] = entry.entry_attributes_as_dict
                    except Exception:
                        result["metadata"]["rootDSE"] = str(entry)
                else:
                    result["metadata"]["rootDSE_search_result"] = conn.result
            except Exception as e:
                result["metadata"]["rootDSE_error"] = str(e)

            # optionally try a small subtree search if namingContexts found
            try:
                naming = result["metadata"].get("rootDSE", {}).get("namingContexts", [])
                if naming:
                    # query first naming context for a couple of attributes (non-intrusive)
                    base = naming[0]
                    if conn.search(search_base=base, search_filter='(objectClass=*)', search_scope=BASE,
                                   attributes=['objectClass'], size_limit=1):
                        result["metadata"]["sample_base_found"] = True
                        result["metadata"]["sample_base"] = base
                    else:
                        result["metadata"]["sample_base_found"] = False
                else:
                    result["metadata"]["namingContexts_missing"] = True
            except Exception as e:
                result["metadata"]["sample_base_error"] = str(e)

        bind_end = time.time()
        result["timings"]["bind_s"] = round(bind_end - bind_start, 4)

    except Exception as e:
        result["error"] = f"Exception during LDAP operations: {e}"
    finally:
        if conn:
            try:
                conn.unbind()
            except Exception:
                pass
        result["timings"]["total_s"] = round(time.time() - start_time, 4)

    return result

def main():
    parser = argparse.ArgumentParser(description="Detect LDAP anonymous bind access")
    parser.add_argument('--host', '-H', required=True,
                        help="LDAP host (hostname or ldap://host). If you include scheme it will be stripped.")
    parser.add_argument('--port', '-p', type=int, help="TCP port (defaults: 389 for ldap, 636 for ldaps)")
    parser.add_argument('--use-ldaps', action='store_true', help="Use LDAPS (SSL) on connect (default false)")
    parser.add_argument('--starttls', action='store_true', help="Use StartTLS (upgrade connection). Mutually exclusive with --use-ldaps")
    parser.add_argument('--timeout', type=int, default=5, help="Timeout seconds for connects/operations (default 5)")
    parser.add_argument('--json', action='store_true', help="Print JSON only (machine friendly)")
    args = parser.parse_args()

    raw_host = normalize_host(args.host)
    # split host:port if user provided host:port
    target_host = raw_host
    explicit_port = args.port
    if ':' in raw_host and raw_host.count(':') == 1 and not raw_host.startswith('['):
        # naive host:port split, not handling IPv6 [] notation here
        parts = raw_host.rsplit(':', 1)
        if parts[1].isdigit():
            target_host = parts[0]
            explicit_port = int(parts[1])

    # choose port default
    port = explicit_port
    if port is None:
        port = 636 if args.use_ldaps else 389

    if args.starttls and args.use_ldaps:
        print(json.dumps({"error": "Cannot use both --starttls and --use-ldaps"}, indent=2))
        return

    out = try_anonymous_bind(target_host, port, use_ldaps=args.use_ldaps, starttls=args.starttls, timeout=args.timeout)

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        # human friendly output
        status = "ALLOWED" if out["success"] else "NOT ALLOWED"
        print(f"Anonymous LDAP bind: {status}")
        print(f"Host: {out['host']}:{out['port']}  LDAPS={out['use_ldaps']}  StartTLS={out['starttls']}")
        if out["error"]:
            print("Error / details:", out["error"])
        print("Timings (s):", out.get("timings", {}))
        print("Metadata (partial):")
        # pretty print selected metadata
        meta = out.get("metadata", {})
        for k in ("rootDSE", "server_info", "namingContexts", "sample_base", "sample_base_found"):
            if k in meta:
                print(f" - {k}: {meta[k]}")
        # dump full JSON at end for copy/paste
        print("\nFull JSON output:")
        print(json.dumps(out, indent=2))

    # exit with code 0 always; tools relying on success should parse JSON 'success' field
    return

if __name__ == "__main__":
    main()