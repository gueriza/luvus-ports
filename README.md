# luvus-ports

A [Luvus](https://luvus.dev) module that shows open TCP ports per workspace in
the Workspaces sidebar, the way Zentty's workspace badge does. Each port is a
clickable row that opens `http://localhost:<port>` in your browser.

Only ports owned by a process inside an open workspace are shown. System and
background listeners (AirPlay, browsers, archived projects) are filtered out.

## How it works

- `scripts/poll.sh` (startup hook) spawns a detached background loop.
- Workspace and tab events also trigger an immediate rescan, the same
  event-driven pattern as the `branch-dock` example module.
- Every N seconds (setting `interval`, default 5s) `scripts/scan.py`:
  1. Lists listening TCP ports with `lsof`.
  2. Resolves each port's owning process cwd (macOS: `lsof`, Linux: `/proc`).
  3. Keeps only ports whose cwd matches an open workspace (longest prefix).
  4. Pushes grouped rows to the `Ports` dock (left sidebar, under
     Workspaces): one muted header row per workspace, one clickable port row
     each.
- Clicking a port row runs the `open` action: opens the row's URL with
  `open` / `xdg-open`.
- Right-click any WORKSPACES row and pick "Open project port" to open that
  workspace's lowest-numbered port (toast if it has none).

## Install

```sh
luvus module link /path/to/luvus-ports
```

## Settings

- `interval`: poll interval in seconds (default 5).
- `max_ports`: max port rows shown (default 30).

## Manual control

```sh
luvus module run ry.luvus-ports refresh   # rescan now
luvus module settings ry.luvus-ports      # view settings
luvus ui dock move --id ry:ports --side right   # relocate the dock
```

To stop the poller: `kill $(cat .poll.pid)` in the module directory, then
`luvus module disable ry.luvus-ports`.

## Requirements

- macOS or Linux with `lsof` and `python3` (stdlib only).
- Luvus >= 0.8.3.

## Note

Luvus has no API for annotating the built-in WORKSPACES rows themselves, so
the ports live in a module dock placed directly under the Workspaces list,
plus a right-click action on workspace rows.
