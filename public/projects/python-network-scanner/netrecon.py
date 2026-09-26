#!/usr/bin/env python3
"""
NetRecon v2 - a dependency-free network reconnaissance framework.

Capabilities
    * Target expansion: hostnames, IPs, CIDR blocks (192.168.1.0/24), octet ranges
    * Host discovery (TCP ping) across whole subnets
    * Fast threaded TCP port scanning with scan profiles
    * Protocol-aware service/version detection (HTTP, TLS, SSH, FTP, SMTP, ...)
    * HTTP security-header audit with a graded score
    * Best-effort OS fingerprint via ICMP TTL
    * Traceroute (uses system traceroute/tracepath when available)
    * Reports: JSON, CSV, and a standalone themed HTML report

Industry use: the same recon pipeline security teams run before an assessment or
asset inventory. Only scan systems you own or are authorized to test.
"""

import argparse
import concurrent.futures
import csv
import html
import ipaddress
import json
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
from datetime import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

VERSION = "2.0.0"

COMMON_PORTS = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    67: "dhcp", 69: "tftp", 80: "http", 110: "pop3", 111: "rpcbind", 123: "ntp",
    135: "msrpc", 137: "netbios-ns", 138: "netbios-dgm", 139: "netbios-ssn",
    143: "imap", 161: "snmp", 162: "snmptrap", 179: "bgp", 389: "ldap",
    443: "https", 445: "smb", 465: "smtps", 514: "syslog", 515: "lpd",
    587: "submission", 631: "ipp", 636: "ldaps", 873: "rsync", 993: "imaps",
    995: "pop3s", 1080: "socks", 1194: "openvpn", 1433: "mssql", 1434: "mssql-udp",
    1521: "oracle", 1723: "pptp", 2049: "nfs", 2082: "cpanel", 2083: "cpanel-ssl",
    2181: "zookeeper", 2375: "docker", 3000: "http-alt", 3128: "squid",
    3306: "mysql", 3389: "rdp", 3690: "svn", 4444: "metasploit", 5000: "http-alt",
    5432: "postgresql", 5601: "kibana", 5672: "amqp", 5900: "vnc", 5984: "couchdb",
    6000: "x11", 6379: "redis", 6443: "kubernetes", 7001: "weblogic",
    8000: "http-alt", 8080: "http-proxy", 8081: "http-alt", 8443: "https-alt",
    8888: "http-alt", 9000: "http-alt", 9090: "http-alt", 9200: "elasticsearch",
    9300: "elasticsearch", 11211: "memcached", 27017: "mongodb", 27018: "mongodb",
}

PORT_PROFILES = {
    "quick": [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3389, 8080],
    "web": [80, 443, 8000, 8080, 8081, 8443, 8888, 9000, 9090],
    "db": [1433, 1521, 3306, 5432, 5900, 6379, 9200, 11211, 27017],
    "top": [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 161, 389, 443, 445,
            465, 587, 636, 993, 995, 1080, 1433, 1521, 2049, 3306, 3389, 5432,
            5900, 6379, 8080, 8443, 9200, 11211, 27017],
}

RISKY_PORTS = {
    21: "FTP - often allows anonymous/plaintext login",
    23: "Telnet - credentials sent in plaintext",
    111: "rpcbind - exposes RPC services, keep internal",
    135: "MSRPC - Windows surface, restrict externally",
    139: "NetBIOS - legacy exposure",
    445: "SMB - common ransomware entry point",
    1433: "MSSQL - verify strong auth and no public exposure",
    2375: "Docker API - unauthenticated access is critical",
    3306: "MySQL - should not be internet-facing",
    3389: "RDP - frequent brute-force target",
    5432: "PostgreSQL - should not be internet-facing",
    5900: "VNC - verify password protection",
    6379: "Redis - often exposed without auth",
    9200: "Elasticsearch - often open by default",
    11211: "Memcached - amplification/exposure risk",
    27017: "MongoDB - verify authentication",
}

TLS_PORTS = {443, 465, 636, 993, 995, 2083, 2087, 2096, 8443}
HTTP_PORTS = {80, 3000, 5000, 8000, 8080, 8081, 8443, 8888, 9000, 9090}

PROBES = {
    22: b"",
    21: b"",
    25: b"EHLO netrecon.local\r\n",
    110: b"",
    143: b"a1 LOGIN test test\r\n",
    3306: b"",
    5432: b"",
}

OS_TTL = {64: "Linux/Unix", 128: "Windows", 255: "Network device"}


USE_COLOR = sys.stdout.isatty()


def c(text, code):
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def info(msg): print(c("[*] ", "96") + msg)
def good(msg): print(c("[+] ", "92") + msg)
def warn(msg): print(c("[!] ", "93") + msg)
def bad(msg): print(c("[-] ", "91") + msg)


def banner():
    print(c(r"""
   _   _      _ ____
  | \ | | ___| |  _ \ ___  ___ ___  _ __
  |  \| |/ _ \ | |_) / _ \/ __/ _ \| '_ \
  | |\  |  __/ |  _ <  __/ (_| (_) | | | |
  |_| \_|\___|_|_| \_\___|\___\___/|_| |_|  v""" + VERSION, "95"))
    print(c("  network reconnaissance framework\n", "90"))


# ---------------------------------------------------------------- targets
def expand_target(spec):
    spec = spec.strip()
    if not spec:
        return []
    spec = re.sub(r"^https?://", "", spec).split("/")[0] if "://" in spec else spec

    if "/" in spec:
        try:
            net = ipaddress.ip_network(spec, strict=False)
            hosts = list(net.hosts()) or [net.network_address]
            return [str(ip) for ip in hosts]
        except ValueError:
            raise SystemExit(f"[!] Invalid CIDR: {spec}")

    m = re.match(r"^(\d+\.\d+\.\d+\.)(\d+)-(\d+)$", spec)
    if m:
        return [m.group(1) + str(i) for i in range(int(m.group(2)), int(m.group(3)) + 1)]

    if "," in spec:
        out = []
        for part in spec.split(","):
            out.extend(expand_target(part))
        return out

    return [spec]


def expand_all(specs):
    seen, out = set(), []
    for spec in specs:
        for host in expand_target(spec):
            if host not in seen:
                seen.add(host)
                out.append(host)
    return out


def resolve(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None


def reverse_dns(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return ""


def parse_ports(args):
    if args.top:
        return sorted(PORT_PROFILES["top"])
    if args.profile:
        return sorted(PORT_PROFILES[args.profile])
    ports = set()
    for part in args.ports.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start, end = part.split("-", 1)
            ports.update(range(int(start), int(end) + 1))
        else:
            ports.add(int(part))
    return sorted(p for p in ports if 0 < p <= 65535)


# ---------------------------------------------------------------- discovery
DISCOVERY_PORTS = [80, 443, 22, 21, 25, 3389, 8080, 8443, 445, 53]


def host_up(ip, timeout):
    for port in DISCOVERY_PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((ip, port)) == 0:
                    return True, port
        except OSError:
            continue
    if shutil.which("ping"):
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", str(max(1, int(timeout))) , ip],
                capture_output=True, text=True, timeout=timeout + 1,
            )
            if result.returncode == 0:
                return True, None
        except (subprocess.SubprocessError, OSError):
            pass
    return False, None


def os_guess(ip):
    if not shutil.which("ping"):
        return ""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            capture_output=True, text=True, timeout=3,
        )
        m = re.search(r"ttl=(\d+)", result.stdout, re.IGNORECASE)
        if not m:
            return ""
        ttl = int(m.group(1))
        best = min(OS_TTL, key=lambda t: abs(t - ttl))
        if abs(best - ttl) <= 8:
            return f"{OS_TTL[best]} (ttl={ttl})"
        return f"unknown (ttl={ttl})"
    except (subprocess.SubprocessError, OSError):
        return ""


# ---------------------------------------------------------------- detection
def read_banner(sock, timeout, probe=b""):
    try:
        if probe:
            sock.sendall(probe)
        sock.settimeout(timeout)
        data = sock.recv(2048)
        if not data:
            return ""
        lines = [ln for ln in data.decode("utf-8", "ignore").splitlines() if ln.strip()]
        text = " | ".join(ln.strip() for ln in lines[:2])
        return text[:160]
    except (socket.timeout, OSError, ssl.SSLError):
        return ""


def detect_tls(ip, port, timeout):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((ip, port), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=ip) as tls:
                cipher = tls.cipher()
                cert = tls.getpeercert()
                subject = ""
                if cert:
                    for rdn in cert.get("subject", []):
                        for key, val in rdn:
                            if key == "commonName":
                                subject = val
                return f"TLS {tls.version()} {cipher[0] if cipher else ''} CN={subject}".strip()
    except (ssl.SSLError, socket.timeout, OSError):
        return ""


def http_probe(ip, port, use_tls, timeout):
    scheme = "https" if use_tls else "http"
    url = f"{scheme}://{ip}:{port}/"
    try:
        ctx = ssl._create_unverified_context() if use_tls else None
        req = Request(url, headers={"User-Agent": f"NetRecon/{VERSION}"})
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            server = resp.headers.get("Server", "")
            return f"HTTP {resp.status} {server}".strip()
    except URLError as exc:
        return f"HTTP probe failed ({exc.reason})"
    except (socket.timeout, OSError, ValueError):
        return ""


def scan_port(ip, port, timeout, service_detect):
    result = {"port": port, "state": "closed", "service": COMMON_PORTS.get(port, "unknown"),
              "banner": "", "latency_ms": 0.0, "risk": RISKY_PORTS.get(port, ""),
              "tls": "", "http": ""}
    start = time.perf_counter()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            if sock.connect_ex((ip, port)) != 0:
                return result
            result["state"] = "open"
            result["latency_ms"] = round((time.perf_counter() - start) * 1000, 1)

            if not service_detect:
                return result

            if port in TLS_PORTS:
                tls_info = detect_tls(ip, port, timeout)
                if tls_info:
                    result["tls"] = tls_info
                    result["service"] = "https" if port in (443, 8443) else "tls"
                    return result

            if port in HTTP_PORTS:
                http_info = http_probe(ip, port, port in TLS_PORTS, timeout)
                if http_info:
                    result["http"] = http_info
                    result["service"] = "https" if port in TLS_PORTS else "http"
                    return result

            banner = read_banner(sock, timeout, PROBES.get(port, b""))
            result["banner"] = banner
            if banner:
                low = banner.lower()
                for needle, name in (("ssh", "ssh"), ("ftp", "ftp"), ("smtp", "smtp"),
                                     ("mysql", "mysql"), ("redis", "redis"),
                                     ("apache", "http"), ("nginx", "http")):
                    if needle in low:
                        result["service"] = name
                        break
            return result
    except socket.timeout:
        result["state"] = "filtered"
        return result
    except OSError:
        return result


def http_audit(ip, port, timeout):
    use_tls = port in TLS_PORTS
    scheme = "https" if use_tls else "http"
    url = f"{scheme}://{ip}:{port}/"
    try:
        ctx = ssl._create_unverified_context()
        req = Request(url, headers={"User-Agent": f"NetRecon/{VERSION}"})
        with urlopen(req, timeout=timeout, context=ctx) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
    except (URLError, socket.timeout, OSError, ValueError) as exc:
        return {"url": url, "error": str(exc), "checks": [], "score": 0, "grade": "F"}

    checks = []

    def add(name, ok, detail):
        checks.append({"name": name, "pass": ok, "detail": detail})

    hsts = headers.get("strict-transport-security")
    add("Strict-Transport-Security", bool(hsts) if use_tls else False,
        hsts or ("missing on HTTPS" if use_tls else "n/a for HTTP"))
    csp = headers.get("content-security-policy")
    add("Content-Security-Policy", bool(csp), csp or "missing - XSS mitigation absent")
    xfo = headers.get("x-frame-options")
    ca = headers.get("content-security-policy", "")
    add("Clickjacking protection", bool(xfo) or "frame-ancestors" in ca,
        xfo or ("frame-ancestors in CSP" if "frame-ancestors" in ca else "missing"))
    add("X-Content-Type-Options", headers.get("x-content-type-options") == "nosniff",
        headers.get("x-content-type-options", "missing"))
    ref = headers.get("referrer-policy")
    add("Referrer-Policy", bool(ref), ref or "missing")
    perms = headers.get("permissions-policy")
    add("Permissions-Policy", bool(perms), perms or "missing")
    server = headers.get("server", "")
    add("Server banner hidden", not server or not re.search(r"\d", server),
        server or "not disclosed")
    xpb = headers.get("x-powered-by", "")
    add("X-Powered-By hidden", not xpb, xpb or "not disclosed")
    cookie = headers.get("set-cookie", "")
    secure = ("secure" in cookie.lower()) and ("httponly" in cookie.lower())
    add("Cookies Secure+HttpOnly", secure if cookie else True,
        cookie[:80] if cookie else "no cookies set")

    passed = sum(1 for chk in checks if chk["pass"])
    score = round(100 * passed / len(checks))
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"
    return {"url": url, "score": score, "grade": grade, "checks": checks}


def traceroute(host, max_hops=15):
    tool = shutil.which("traceroute") or shutil.which("tracepath")
    if not tool:
        return []
    cmd = [tool, "-n", "-m", str(max_hops), "-w", "1", host] if tool.endswith("traceroute") \
        else [tool, "-m", str(max_hops), host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=max_hops + 5)
        hops = []
        for line in result.stdout.splitlines()[1:]:
            line = line.strip()
            if not line:
                continue
            hop = re.match(r"^(\d+)\s", line)
            addr = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
            hops.append({"hop": int(hop.group(1)) if hop else len(hops) + 1,
                         "host": addr.group(1) if addr else "*"})
        return hops
    except (subprocess.SubprocessError, OSError):
        return []


# ---------------------------------------------------------------- scanning
def scan_host(host, ports, timeout, workers, args):
    ip = resolve(host)
    if ip is None:
        bad(f"Could not resolve {host} - skipping")
        return None

    record = {"host": host, "ip": ip, "ptr": reverse_dns(ip), "open_ports": [],
              "os": "", "http_audit": None, "traceroute": []}
    ptr = f" ptr={record['ptr']}" if record["ptr"] else ""
    info(f"Target {c(host, '97')} ({ip}){ptr}")

    if args.ping_only:
        up, via = host_up(ip, timeout)
        if up:
            record["up"] = True
            good(f"  host is up{'' if via is None else f' (port {via} responded)'}")
        else:
            warn("  host did not respond")
        return record

    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(scan_port, ip, p, timeout, not args.no_service): p for p in ports}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res["state"] == "open":
                open_ports.append(res)

    open_ports.sort(key=lambda r: r["port"])
    record["open_ports"] = open_ports

    for res in open_ports:
        extra = res["tls"] or res["http"] or res["banner"]
        line = f"  {c('[+]', '92')} {res['port']:<5} {c(res['service'], '97'):<21}{res['latency_ms']:>7} ms"
        if extra:
            line += f"  {c(extra, '90')}"
        print(line)
        if res["risk"]:
            print(f"        {c('risk:', '93')} {res['risk']}")

    if open_ports and args.os:
        record["os"] = os_guess(ip)
        if record["os"]:
            info(f"  OS guess: {record['os']}")

    if args.http_audit:
        for res in open_ports:
            if res["port"] in HTTP_PORTS or res["tls"]:
                audit = http_audit(ip, res["port"], timeout)
                record["http_audit"] = audit
                grade = audit.get("grade", "?")
                url = audit.get("url", "")
                if "error" in audit:
                    warn(f"  HTTP audit {url}: {audit['error']}")
                else:
                    good(f"  HTTP audit {url}: grade {c(grade, '93')} ({audit['score']}/100)")
                    for chk in audit["checks"]:
                        mark = c("PASS", "92") if chk["pass"] else c("FAIL", "91")
                        print(f"        [{mark}] {chk['name']}: {chk['detail']}")
                break

    if args.traceroute:
        info("  traceroute...")
        record["traceroute"] = traceroute(host)
        for hop in record["traceroute"]:
            print(f"        {hop['hop']:>2}  {hop['host']}")

    return record


# ---------------------------------------------------------------- reports
def write_json(records, path, meta):
    with open(path, "w") as fh:
        json.dump({**meta, "results": records}, fh, indent=2)
    good(f"JSON report  -> {path}")


def write_csv(records, path):
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["host", "ip", "port", "state", "service", "banner", "tls", "risk"])
        for record in records:
            for p in record["open_ports"]:
                writer.writerow([record["host"], record["ip"], p["port"], p["state"],
                                 p["service"], p["banner"], p["tls"], p["risk"]])
    good(f"CSV report   -> {path}")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>NetRecon Report</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{{--bg:#0a0e17;--card:#141b2e;--border:#232c44;--text:#e6e9f2;--muted:#8b93a7;--accent:#38e1b0;--red:#ff6b6b;--yellow:#feca57}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;line-height:1.5}}
header{{padding:32px 24px;border-bottom:1px solid var(--border);background:#101627}}
h1{{margin:0 0 6px;font-size:1.6rem}} h1 span{{color:var(--accent)}}
.meta{{color:var(--muted);font-size:.85rem;font-family:monospace}}
.wrap{{max-width:1000px;margin:0 auto;padding:24px}}
.host{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:20px}}
.host h2{{margin:0 0 4px;font-size:1.15rem}} .host .ip{{color:var(--muted);font-family:monospace;font-size:.85rem;margin-bottom:14px}}
table{{width:100%;border-collapse:collapse;font-size:.88rem}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border)}}
th{{color:var(--accent);font-family:monospace;font-size:.78rem;text-transform:uppercase}}
.risk{{color:var(--yellow);font-size:.8rem}}
.grade{{display:inline-block;padding:2px 10px;border-radius:999px;font-weight:700;font-family:monospace}}
.A{{background:#123d2e;color:#38e1b0}}.B{{background:#31401a;color:#b7e14b}}.C{{background:#4a3a12;color:#feca57}}.D{{background:#4a2412;color:#ff9f43}}.F{{background:#4a1212;color:#ff6b6b}}
.chk{{font-size:.85rem;padding:3px 0}} .pass{{color:#38e1b0}} .fail{{color:#ff6b6b}}
footer{{text-align:center;padding:24px;color:var(--muted);font-size:.8rem;font-family:monospace}}
</style></head><body>
<header><div class="wrap"><h1>Net<span>Recon</span> Report</h1>
<div class="meta">{meta}</div></div></header>
<div class="wrap">{body}</div>
<footer>Generated by NetRecon v{version} - authorized testing only</footer>
</body></html>"""


def render_host(record):
    parts = [f'<div class="host"><h2>{html.escape(record["host"])}</h2>',
             f'<div class="ip">{record["ip"]}'
             + (f' &middot; {html.escape(record["ptr"])}' if record.get("ptr") else "")
             + (f' &middot; OS: {html.escape(record["os"])}' if record.get("os") else "")
             + '</div>']
    if record["open_ports"]:
        parts.append("<table><tr><th>Port</th><th>Service</th><th>Latency</th><th>Details</th><th>Risk</th></tr>")
        for p in record["open_ports"]:
            detail = html.escape(p["tls"] or p["http"] or p["banner"] or "-")
            risk = f'<span class="risk">{html.escape(p["risk"])}</span>' if p["risk"] else "-"
            parts.append(f'<tr><td>{p["port"]}</td><td>{html.escape(p["service"])}</td>'
                         f'<td>{p["latency_ms"]} ms</td><td>{detail}</td><td>{risk}</td></tr>')
        parts.append("</table>")
    else:
        parts.append('<p style="color:#8b93a7">No open ports found.</p>')

    audit = record.get("http_audit")
    if audit and "checks" in audit:
        parts.append(f'<h3 style="margin:16px 0 8px;font-size:1rem">HTTP Security Audit '
                     f'<span class="grade {audit["grade"]}">{audit["grade"]} {audit["score"]}/100</span></h3>')
        for chk in audit["checks"]:
            cls = "pass" if chk["pass"] else "fail"
            mark = "PASS" if chk["pass"] else "FAIL"
            parts.append(f'<div class="chk"><span class="{cls}">[{mark}]</span> '
                         f'{html.escape(chk["name"])}: {html.escape(str(chk["detail"]))}</div>')

    if record.get("traceroute"):
        parts.append('<h3 style="margin:16px 0 8px;font-size:1rem">Traceroute</h3><table>')
        for hop in record["traceroute"]:
            parts.append(f'<tr><td>{hop["hop"]}</td><td colspan="4">{html.escape(hop["host"])}</td></tr>')
        parts.append("</table>")

    parts.append("</div>")
    return "".join(parts)


def write_html(records, path, meta):
    body = "".join(render_host(r) for r in records)
    doc = HTML_TEMPLATE.format(meta=html.escape(meta), body=body, version=VERSION)
    with open(path, "w") as fh:
        fh.write(doc)
    good(f"HTML report  -> {path}")


# ---------------------------------------------------------------- CLI
def build_parser():
    p = argparse.ArgumentParser(
        prog="netrecon",
        description="NetRecon - network reconnaissance: discovery, port scanning, "
                    "service/OS detection, HTTP security audit, traceroute.",
    )
    p.add_argument("targets", nargs="*", help="hosts, IPs, CIDR (192.168.1.0/24), or ranges (192.168.1.1-50)")
    p.add_argument("-iL", "--input", metavar="FILE", help="read targets from a file (one per line)")
    p.add_argument("-p", "--ports", default="1-1024", help="ports: '22,80,443' or '1-1024'")
    p.add_argument("--profile", choices=sorted(PORT_PROFILES), help="scan a preset port profile")
    p.add_argument("--top", action="store_true", help="scan the top common ports")
    p.add_argument("-t", "--timeout", type=float, default=0.6, help="per-port timeout (s)")
    p.add_argument("-w", "--workers", type=int, default=200, help="concurrent threads")
    p.add_argument("-sn", "--ping-only", action="store_true", help="host discovery only (no port scan)")
    p.add_argument("-sV", "--no-service", dest="no_service", action="store_true",
                   help="disable service/version detection")
    p.add_argument("--os", action="store_true", help="attempt OS fingerprinting via ICMP TTL")
    p.add_argument("--http-audit", action="store_true", help="audit HTTP security headers")
    p.add_argument("--traceroute", action="store_true", help="run a traceroute to each host")
    p.add_argument("--json", metavar="FILE", help="write JSON report")
    p.add_argument("--csv", metavar="FILE", help="write CSV report")
    p.add_argument("--html", metavar="FILE", help="write HTML report")
    p.add_argument("--no-color", action="store_true", help="disable colored output")
    p.add_argument("--version", action="version", version=f"NetRecon {VERSION}")
    return p


def main(argv=None):
    global USE_COLOR
    args = build_parser().parse_args(argv)
    if args.no_color:
        USE_COLOR = False

    targets = list(args.targets or [])
    if args.input:
        try:
            with open(args.input) as fh:
                targets += [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
        except OSError as exc:
            sys.exit(f"[!] Cannot read target file: {exc}")
    if not targets:
        targets = ["127.0.0.1"]
        warn("No targets given, defaulting to 127.0.0.1")

    hosts = expand_all(targets)
    ports = parse_ports(args)

    banner()
    info(f"Targets : {len(hosts)} host(s)")
    info(f"Ports   : {len(ports)} ({'profile:' + args.profile if args.profile else 'custom'})")
    if args.ping_only:
        info("Mode    : host discovery only")
    print()

    meta = {"scanned_at": datetime.now().isoformat(), "version": VERSION,
            "targets": len(hosts), "ports": len(ports), "tool": "NetRecon"}

    records, started = [], time.perf_counter()
    for host in hosts:
        record = scan_host(host, ports, args.timeout, args.workers, args)
        if record:
            records.append(record)
    elapsed = time.perf_counter() - started

    total_open = sum(len(r["open_ports"]) for r in records)
    print()
    good(f"Scan complete: {total_open} open port(s) across {len(records)} host(s) in {elapsed:.2f}s")

    if args.json:
        write_json(records, args.json, meta)
    if args.csv:
        write_csv(records, args.csv)
    if args.html:
        write_html(records, args.html, f"Scanned {meta['scanned_at']} - {len(records)} host(s), {len(ports)} port(s)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\n[!] Interrupted by user")
