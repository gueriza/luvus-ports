#!/bin/sh
# Right-click a WORKSPACES row: open the lowest-numbered port owned by that
# workspace. LUVUS_WORKSPACE_CWD is the clicked row's folder.
# Usage: luvus module run ry.luvus-ports open-workspace-port

set -u

cwd="$LUVUS_WORKSPACE_CWD"
[ -n "$cwd" ] || { echo "no workspace cwd in context" >&2; exit 1; }

port="$(python3 - "$cwd" <<'EOF'
import sys
sys.path.insert(0, ".")
from scan import listening_ports, pid_cwd, match_workspace, workspaces

target = sys.argv[1]
ws_list = workspaces()
ports = []
for port, pid, _p in listening_ports():
    c = pid_cwd(pid)
    ws = match_workspace(c, ws_list) if c else None
    if ws and ws["cwd"] == target:
        ports.append(port)
print(min(ports) if ports else "")
EOF
)"

if [ -z "$port" ]; then
  "${LUVUS_BIN_PATH:-luvus}" ui toast "no open port in $(basename "$cwd")"
  exit 0
fi

"${LUVUS_BIN_PATH:-luvus}" ui toast "opening :$port ($(basename "$cwd"))"
if command -v open >/dev/null 2>&1; then
  exec open "http://localhost:$port"
elif command -v xdg-open >/dev/null 2>&1; then
  exec xdg-open "http://localhost:$port"
fi
