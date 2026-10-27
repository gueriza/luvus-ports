#!/usr/bin/env python3
"""Scan listening TCP ports, group them by Luvus workspace, push dock rows.

One row per port. Clicking a row runs the module's "open" action with the
row value set to http://localhost:<port>.

Stdlib only. Runs on macOS and Linux.
"""

import json
import os
import subprocess
import sys

LUVUS = os.environ.get("LUVUS_BIN_PATH", "luvus")
DOCK_ID = "ry:ports"


def run(argv):
    return subprocess.run(argv, capture_output=True, text=True)


def listening_ports():
    """Return list of (port, pid, process_name) for TCP listeners."""
    proc = run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"])
    ports = []
    for line in proc.stdout.splitlines()[1:]:
        parts = line.split()
        # NAME column is "<addr>:<port> (LISTEN)": two tokens. Locate it by
        # the preceding "TCP"/"UDP" type token instead of a fixed index.
        name = None
        for i, tok in enumerate(parts):
            if tok in ("TCP", "UDP") and i + 1 < len(parts):
                name = parts[i + 1]
                break
        if not name or ":" not in name:
            continue
        _, _, port = name.rpartition(":")
        if not port.isdigit():
            continue
        try:
            pid = int(parts[1])
        except ValueError:
            continue
        ports.append((int(port), pid, parts[0]))
    return ports


def pid_cwd(pid):
    """Best-effort cwd of a pid. macOS: lsof. Linux: /proc."""
    if os.path.isdir("/proc"):
        try:
            return os.readlink(f"/proc/{pid}/cwd")
        except OSError:
            return None
    proc = run(["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"])
    for line in proc.stdout.splitlines():
        if line.startswith("n") and len(line) > 1:
            return line[1:]
    return None


def workspaces():
    proc = run([LUVUS, "workspace", "list"])
    try:
        data = json.loads(proc.stdout)
        return data["result"]["workspaces"]
    except (ValueError, KeyError):
        return []


def match_workspace(cwd, ws_list):
    """Longest-prefix match of a cwd against workspace folders."""
    best = None
    best_len = -1
    for ws in ws_list:
        root = ws.get("cwd") or ""
        if root and (cwd == root or cwd.startswith(root + os.sep)):
            if len(root) > best_len:
                best = ws
                best_len = len(root)
    return best


def main():
    max_ports = int(os.environ.get("LUVUS_SETTING_MAX_PORTS", "30"))
    try:
        max_ports = max(1, max_ports)
    except ValueError:
        max_ports = 30

    ws_list = workspaces()
    seen = set()
    by_ws = {}  # workspace name -> sorted list of ports (project ports only)

    for port, pid, _pname in listening_ports():
        if port in seen:
            continue
        seen.add(port)
        cwd = pid_cwd(pid)
        ws = match_workspace(cwd, ws_list) if cwd else None
        if ws is None:
            continue  # system noise: only workspace-owned ports are shown
        by_ws.setdefault(ws["name"], []).append(port)

    rows = []
    count = 0
    for name in sorted(by_ws, key=str.lower):
        if count >= max_ports:
            break
        rows.append({"text": name})
        for port in sorted(by_ws[name]):
            if count >= max_ports:
                break
            count += 1
            rows.append(
                {
                    "spans": [
                        {"text": "  ", "tone": "muted"},
                        {"text": f":{port}", "tone": "accent"},
                    ],
                    "text": f":{port}",
                    "dot": "working",
                    "action": "open",
                    "value": f"http://localhost:{port}",
                }
            )

    if not rows:
        rows = [{"text": "no project ports", "dot": "idle", "tone": "muted"}]

    payload = json.dumps(rows)
    proc = subprocess.run(
        [LUVUS, "ui", "dock", "push", "--id", DOCK_ID, "--title", "PORTS"],
        input=payload,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
