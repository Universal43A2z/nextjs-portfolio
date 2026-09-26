#!/usr/bin/env python3
"""
PassAudit - password strength auditing, breach checking, and attack testing.

Features
    * check     - score strength: entropy, character classes, and pattern detection
                  (sequences, keyboard walks, repeats, dates, leetspeak, names),
                  with offline/online crack-time estimates and recommendations.
    * pwned     - check whether a password appears in known data breaches using
                  the HaveIBeenPwned k-anonymity API (no API key, password never sent).
    * generate  - create strong random passwords with configurable rules.
    * identify  - detect a hash's likely algorithm from its format/length.
    * crack     - authorized dictionary attack against MD5/SHA1/SHA256/SHA512
                  hashes using leetspeak and suffix mutation rules.
    * gui       - launch the graphical interface (passaudit_gui.py).

Use only on accounts and hashes you are authorized to audit.
"""

import argparse
import csv
import hashlib
import html
import json
import math
import os
import re
import secrets
import string
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

BREACH_API = "https://api.pwnedpasswords.com/range/"

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "monkey", "letmein",
    "dragon", "111111", "baseball", "iloveyou", "trustno1", "sunshine",
    "master", "welcome", "shadow", "ashley", "football", "jesus", "michael",
    "ninja", "mustang", "password1", "admin", "root", "toor", "passw0rd",
    "qwerty123", "1q2w3e4r", "zaq12wsx", "superman", "batman", "starwars",
}

KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm", "1234567890"]

LEET = {"a": ["a", "@", "4"], "e": ["e", "3"], "i": ["i", "1", "!"], "o": ["o", "0"],
        "s": ["s", "5", "$"], "t": ["t", "7"], "l": ["l", "1"], "g": ["g", "9"]}

SUFFIXES = ["", "1", "12", "123", "1234", "!", "!!", "2020", "2021", "2022",
            "2023", "2024", "2025", "2026", "@", "#", "01"]

ALGOS = {"md5": hashlib.md5, "sha1": hashlib.sha1, "sha256": hashlib.sha256,
         "sha512": hashlib.sha512}

AMBIGUOUS = "Il1O0o|"

CRACK_SCENARIOS = [
    ("Online, throttled", 10),
    ("Online, unthrottled", 1_000),
    ("Offline, slow hash", 10_000),
    ("Offline, fast hash", 10_000_000_000),
]


class Color:
    on = sys.stdout.isatty()

    @staticmethod
    def wrap(text, code):
        return text if not Color.on else f"\033[{code}m{text}\033[0m"

    @staticmethod
    def green(t): return Color.wrap(t, "92")
    @staticmethod
    def red(t): return Color.wrap(t, "91")
    @staticmethod
    def yellow(t): return Color.wrap(t, "93")
    @staticmethod
    def cyan(t): return Color.wrap(t, "96")
    @staticmethod
    def dim(t): return Color.wrap(t, "90")
    @staticmethod
    def bold(t): return Color.wrap(t, "1")


# --------------------------------------------------------------- strength
def charset_size(password):
    size = 0
    if re.search(r"[a-z]", password): size += 26
    if re.search(r"[A-Z]", password): size += 26
    if re.search(r"[0-9]", password): size += 10
    if re.search(r"[^A-Za-z0-9]", password): size += 33
    return max(size, 1)


def entropy_bits(password):
    return len(password) * math.log2(charset_size(password)) if password else 0.0


def has_sequence(password):
    low = password.lower()
    for i in range(len(low) - 2):
        a, b, c = low[i], low[i + 1], low[i + 2]
        if ord(a) + 1 == ord(b) and ord(b) + 1 == ord(c):
            return True
    return False


def has_keyboard_walk(password):
    low = password.lower()
    for row in KEYBOARD_ROWS:
        for i in range(len(low) - 2):
            segment = low[i:i + 3]
            if segment in row or segment[::-1] in row:
                return True
    return False


def has_repeat(password):
    return bool(re.search(r"(.)\1{2,}", password))


def has_date(password):
    return bool(re.search(r"(19|20)\d{2}", password) or re.search(r"\d{2}[/-]\d{2}[/-]\d{2,4}", password))


def detect_patterns(password):
    low = password.lower()
    found = []
    if low in COMMON_PASSWORDS:
        found.append("exact common password")
    if any(word in low for word in COMMON_PASSWORDS if len(word) >= 5):
        found.append("contains a common word")
    if has_sequence(password):
        found.append("sequential characters (abc / 123)")
    if has_keyboard_walk(password):
        found.append("keyboard walk (qwe / asd)")
    if has_repeat(password):
        found.append("repeated characters")
    if has_date(password):
        found.append("looks like a year or date")
    if re.sub(r"[^A-Za-z]", "", low) in {"khent", "amorl", "khentvincent", "khentamorl"}:
        found.append("contains a personal name")
    return found


def human_time(seconds):
    if seconds is None:
        return "unknown"
    if seconds < 1: return "instant"
    units = [("century", 3155760000), ("year", 31557600), ("day", 86400),
             ("hour", 3600), ("minute", 60), ("second", 1)]
    for name, secs in units:
        if seconds >= secs:
            value = seconds / secs
            if value < 2:
                unit = name
            elif name == "century":
                unit = "centuries"
            else:
                unit = name + "s"
            return f"{value:,.0f} {unit}"
    return "instant"


def crack_times(password):
    combinations = charset_size(password) ** len(password) if password else 0
    return {name: human_time(combinations / (2 * rate)) for name, rate in CRACK_SCENARIOS}


def recommendations(result):
    tips = []
    password_length = result["password_length"]
    if password_length < 12:
        tips.append("Use at least 12-16 characters.")
    if not result["has_upper"] or not result["has_lower"]:
        tips.append("Mix uppercase and lowercase letters.")
    if not result["has_digit"]:
        tips.append("Add numbers (avoid obvious ones like 1234 or years).")
    if not result["has_symbol"]:
        tips.append("Include symbols such as ! @ # $ %")
    for pattern in result["patterns"]:
        if "common" in pattern:
            tips.append("Avoid dictionary words and known passwords.")
        elif "sequence" in pattern or "keyboard" in pattern:
            tips.append("Avoid keyboard patterns and sequences (qwerty, abc123).")
        elif "date" in pattern:
            tips.append("Avoid years, birthdays, and dates.")
        elif "repeat" in pattern:
            tips.append("Avoid repeated characters (aaa, 111).")
        elif "name" in pattern:
            tips.append("Avoid your own name or personal details.")
    if result.get("breach_count"):
        tips.append("This password appears in known breaches - never reuse it.")
    if not tips:
        tips.append("Strong password. Use a unique one per account and a password manager.")
    return tips


def score_password(password):
    bits = entropy_bits(password)
    patterns = detect_patterns(password)
    penalty = min(len(patterns) * 12, 50)
    length_score = min(len(password) * 4, 40)
    variety = 0
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_symbol = bool(re.search(r"[^A-Za-z0-9]", password))
    if has_lower: variety += 10
    if has_upper: variety += 10
    if has_digit: variety += 10
    if has_symbol: variety += 20
    entropy_score = min(bits / 4, 30)
    score = max(0, min(100, round(length_score + variety + entropy_score - penalty)))

    if score >= 85: rating = "Very Strong"
    elif score >= 70: rating = "Strong"
    elif score >= 50: rating = "Moderate"
    elif score >= 30: rating = "Weak"
    else: rating = "Very Weak"

    return {
        "password_length": len(password),
        "entropy_bits": round(bits, 1),
        "charset_size": charset_size(password),
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "patterns": patterns,
        "score": score,
        "rating": rating,
        "crack_times": crack_times(password),
    }


def print_check(password, result, breach_count=None):
    bar_len = 30
    filled = round(bar_len * result["score"] / 100)
    color = Color.red if result["score"] < 50 else Color.yellow if result["score"] < 70 else Color.green
    bar = color("#" * filled) + Color.dim("-" * (bar_len - filled))
    masked = password[0] + "*" * (len(password) - 1) if password else ""
    print()
    print(f"  Password  : {masked}")
    print(f"  Strength  : [{bar}] {result['score']}/100  {Color.bold(result['rating'])}")
    print(f"  Entropy   : {result['entropy_bits']} bits (charset {result['charset_size']})")
    if breach_count is None:
        print(f"  Breaches  : {Color.dim('not checked (use --online)')}")
    elif breach_count and breach_count > 0:
        print(f"  Breaches  : {Color.red(f'FOUND in {breach_count:,} known breaches!')}")
    else:
        print(f"  Breaches  : {Color.green('no known breach matches')}")
    print("  Crack time:")
    for name, value in result["crack_times"].items():
        print(f"      {name:<24} {value}")
    if result["patterns"]:
        print(f"  Weaknesses: {Color.yellow(', '.join(result['patterns']))}")
    else:
        print(f"  Weaknesses: {Color.green('none detected')}")
    print(f"  Advice    :")
    for tip in recommendations({**result, "breach_count": breach_count}):
        print(f"      - {tip}")
    print()


# --------------------------------------------------------------- breach
def pwned_count(password, timeout=6):
    """Return number of known breaches for a password, or None if the lookup failed."""
    if not password:
        return 0
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    try:
        req = Request(BREACH_API + prefix, headers={"User-Agent": "PassAudit"})
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", "ignore")
    except (URLError, OSError, ValueError):
        return None
    for line in body.splitlines():
        digest, _, count = line.partition(":")
        if digest.strip() == suffix:
            return int(count)
    return 0


# --------------------------------------------------------------- generator
def generate_password(length=16, upper=True, lower=True, digits=True, symbols=True,
                      avoid_ambiguous=False):
    pools = []
    if lower: pools.append(string.ascii_lowercase)
    if upper: pools.append(string.ascii_uppercase)
    if digits: pools.append(string.digits)
    if symbols: pools.append("!@#$%^&*()-_=+[]{};:,.<>?")
    if not pools:
        pools = [string.ascii_letters]
    if avoid_ambiguous:
        pools = ["".join(ch for ch in pool if ch not in AMBIGUOUS) for pool in pools]
        pools = [pool for pool in pools if pool]

    alphabet = "".join(pools)
    length = max(length, len(pools))
    chars = [secrets.choice(pool) for pool in pools]
    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
    rand = secrets.SystemRandom()
    rand.shuffle(chars)
    return "".join(chars)


# --------------------------------------------------------------- identify
HEX_RE = re.compile(r"^[a-fA-F0-9]+$")
HASH_BY_LENGTH = {
    32: ["MD5", "NTLM"],
    40: ["SHA-1"],
    56: ["SHA-224"],
    64: ["SHA-256"],
    96: ["SHA-384"],
    128: ["SHA-512"],
}


def identify_hash(value):
    v = value.strip()
    if v.startswith(("$2a$", "$2b$", "$2y$")): return ["bcrypt"]
    if v.startswith("$argon2"): return ["Argon2"]
    if v.startswith("$pbkdf2"): return ["PBKDF2"]
    if v.startswith("$1$"): return ["MD5 crypt"]
    if v.startswith("$5$"): return ["SHA-256 crypt"]
    if v.startswith("$6$"): return ["SHA-512 crypt"]
    if v.startswith("$y$") or v.startswith("$7$"): return ["yescrypt"]
    if re.match(r"^\{?[A-Z0-9]+\}?", v) and ":" in v: return ["unknown (salted format)"]
    if HEX_RE.match(v):
        return HASH_BY_LENGTH.get(len(v), [f"unknown hex ({len(v)} chars)"])
    return ["unknown"]


# --------------------------------------------------------------- cracking
def mutate(word, fast=False):
    base = word.strip()
    if not base:
        return
    cores = {base, base.lower(), base.upper(), base.capitalize(), base[::-1]}
    if not fast and len(base) <= 12:
        variants = [""]
        for ch in base.lower():
            options = LEET.get(ch, [ch])
            variants = [v + o for v in variants for o in options[:2]]
        cores.update(variants[:128])
    for core in cores:
        yield core
        yield core.capitalize()
        for suffix in SUFFIXES:
            if suffix:
                yield core + suffix
                yield core.capitalize() + suffix


def hash_password(text, algo):
    return ALGOS[algo](text.encode()).hexdigest()


def load_words(wordlist):
    if os.path.isfile(wordlist):
        with open(wordlist, errors="ignore") as fh:
            return [ln.strip() for ln in fh if ln.strip()]
    return list(COMMON_PASSWORDS) + [w for w in wordlist.split(",") if w]


def crack_hashes(hashes, words, algo, fast=False, on_crack=None, should_stop=None):
    targets = {h.lower(): h for h in hashes}
    found = {}
    attempts = 0
    started = time.perf_counter()
    for word in words:
        if should_stop and should_stop():
            break
        for candidate in mutate(word, fast=fast):
            attempts += 1
            digest = hash_password(candidate, algo)
            if digest in targets:
                original = targets.pop(digest)
                found[original] = candidate
                if on_crack:
                    on_crack(original, candidate)
                if not targets:
                    return found, attempts, time.perf_counter() - started
    return found, attempts, time.perf_counter() - started


def crack(hashes, wordlist, algo, fast=False):
    words = load_words(wordlist)
    if not os.path.isfile(wordlist):
        print(Color.dim(f"[i] Wordlist file not found - using {len(words)} built-in common words"))

    rules = "simple" if fast else "full (leet + suffixes + case)"
    print(f"\n[*] {len(hashes)} hash(es) | {len(words)} base words | algorithm: {algo} | rules: {rules}")
    print(f"[*] Testing with mutation rules...\n")

    def on_crack(original, candidate):
        print(f"  {Color.green('[CRACKED]')} {original[:16]}...  ->  {Color.bold(candidate)}")

    found, attempts, elapsed = crack_hashes(hashes, words, algo, fast=fast, on_crack=on_crack)
    rate = attempts / elapsed if elapsed else 0
    print()
    print(f"[*] Attempts   : {attempts:,} ({rate:,.0f}/s)")
    print(f"[*] Elapsed    : {elapsed:.2f}s")
    print(f"[*] Cracked    : {Color.green(str(len(found)))} / {len(hashes)}")
    if len(found) < len(hashes):
        print(f"[*] Survived   : {Color.green(str(len(hashes) - len(found)))} (not in wordlist - likely strong)")
    return found


def load_hashes(value):
    if os.path.isfile(value):
        with open(value) as fh:
            return [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    return [h.strip() for h in value.split(",") if h.strip()]


# --------------------------------------------------------------- batch report
def batch_report_html(results, path):
    rows = []
    for password, result in results.items():
        color = "#ff6b6b" if result["score"] < 50 else "#feca57" if result["score"] < 70 else "#38e1b0"
        rows.append(
            f"<tr><td>{html.escape(password[:40])}</td>"
            f"<td style='color:{color};font-weight:700'>{result['score']}</td>"
            f"<td>{result['rating']}</td>"
            f"<td>{result['entropy_bits']}</td>"
            f"<td>{html.escape(', '.join(result['patterns']) or 'none')}</td>"
            f"<td>{html.escape(result['crack_times']['Offline, fast hash'])}</td></tr>")
    doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>PassAudit Report</title><style>
body{{background:#0a0e17;color:#e6e9f2;font-family:system-ui,sans-serif;padding:32px}}
h1 span{{color:#38e1b0}} table{{width:100%;border-collapse:collapse;font-size:.9rem}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid #232c44}}
th{{color:#38e1b0;font-size:.75rem;text-transform:uppercase}}
</style></head><body><h1>Pass<span>Audit</span> Report</h1>
<p style="color:#8b93a7">{len(results)} password(s) analyzed</p>
<table><tr><th>Password</th><th>Score</th><th>Rating</th><th>Entropy</th><th>Weaknesses</th><th>Crack time (fast hash)</th></tr>
{''.join(rows)}</table></body></html>"""
    with open(path, "w") as fh:
        fh.write(doc)
    print(f"[+] HTML report written to {path}")


# --------------------------------------------------------------- CLI
def build_parser():
    parser = argparse.ArgumentParser(
        prog="passaudit",
        description="PassAudit - password strength auditing, breach checking, and attack testing.",
    )
    parser.add_argument("--no-color", action="store_true", help="disable colored output")
    sub = parser.add_subparsers(dest="command")

    check = sub.add_parser("check", help="analyze password strength")
    check.add_argument("password", nargs="?", help="password to analyze")
    check.add_argument("--file", help="analyze every line in a file")
    check.add_argument("--online", action="store_true", help="check against known breaches (HaveIBeenPwned)")
    check.add_argument("--json", metavar="FILE", help="write results to JSON")
    check.add_argument("--html", metavar="FILE", help="write a batch HTML report")

    gen = sub.add_parser("generate", help="generate strong random passwords")
    gen.add_argument("-l", "--length", type=int, default=16)
    gen.add_argument("-n", "--count", type=int, default=5)
    gen.add_argument("--no-upper", action="store_true")
    gen.add_argument("--no-lower", action="store_true")
    gen.add_argument("--no-digits", action="store_true")
    gen.add_argument("--no-symbols", action="store_true")
    gen.add_argument("--avoid-ambiguous", action="store_true")

    ident = sub.add_parser("identify", help="detect a hash's likely algorithm")
    ident.add_argument("hash")

    pwn = sub.add_parser("pwned", help="check a password against known breaches")
    pwn.add_argument("password")

    crack_p = sub.add_parser("crack", help="dictionary attack against hashes")
    crack_p.add_argument("--hash", dest="hashes", required=True,
                         help="hash or comma-separated hashes, or a file of hashes")
    crack_p.add_argument("--wordlist", default="rockyou.txt",
                         help="wordlist file or comma-separated words")
    crack_p.add_argument("--algo", choices=sorted(ALGOS), default="md5")
    crack_p.add_argument("--fast", action="store_true", help="skip leet mutations (faster)")

    sub.add_parser("gui", help="launch the graphical interface")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "no_color", False):
        Color.on = False

    if args.command == "gui":
        try:
            import passaudit_gui
            passaudit_gui.launch()
        except ImportError:
            sys.exit("[!] GUI needs passaudit_gui.py in the same folder and tkinter installed.")
        return

    if args.command == "generate":
        for _ in range(args.count):
            print(generate_password(args.length, upper=not args.no_upper, lower=not args.no_lower,
                                    digits=not args.no_digits, symbols=not args.no_symbols,
                                    avoid_ambiguous=args.avoid_ambiguous))
        return

    if args.command == "identify":
        types = identify_hash(args.hash)
        print(f"  Hash      : {args.hash[:60]}{'...' if len(args.hash) > 60 else ''}")
        print(f"  Likely    : {', '.join(types)}")
        return

    if args.command == "pwned":
        count = pwned_count(args.password)
        if count is None:
            print("[!] Could not reach the breach service (offline?)")
        elif count > 0:
            print(Color.red(f"[!] FOUND in {count:,} known breaches - do not use this password."))
        else:
            print(Color.green("[+] No known breach matches found."))
        return

    if args.command == "check" or args.command is None:
        if args.command is None:
            parser.print_help()
            return
        if args.file:
            results = {}
            for line in open(args.file):
                pw = line.rstrip("\n")
                if pw:
                    results[pw] = score_password(pw)
                    breach = pwned_count(pw) if args.online else None
                    print_check(pw, results[pw], breach)
                    results[pw]["breach_count"] = breach
            if args.json:
                with open(args.json, "w") as fh:
                    json.dump(results, fh, indent=2)
                print(f"[+] JSON written to {args.json}")
            if args.html:
                batch_report_html(results, args.html)
            weak = [pw for pw, r in results.items() if r["score"] < 50]
            print(f"[*] {len(weak)} of {len(results)} passwords rated Weak or worse")
            return
        if not args.password:
            parser.error("provide a password, --file, or use a subcommand")
        result = score_password(args.password)
        breach = pwned_count(args.password) if args.online else None
        print_check(args.password, result, breach)
        result["breach_count"] = breach
        if args.json:
            with open(args.json, "w") as fh:
                json.dump(result, fh, indent=2)
            print(f"[+] JSON written to {args.json}")
        return

    if args.command == "crack":
        hashes = load_hashes(args.hashes)
        crack(hashes, args.wordlist, args.algo, fast=args.fast)
        return

    parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\n[!] Interrupted")
