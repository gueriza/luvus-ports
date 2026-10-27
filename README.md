# p-luvus

A [Luvus](https://luvus.dev) module that shows open TCP ports per workspace in a
sidebar dock, the way Zentty's workspace badge does. Each port is a clickable
row that opens `http://localhost:<port>` in your browser.

## How it works

- `scripts/poll.sh` (startup hook) spawns a detached background loop.
- Every N seconds (setting `interval`, default 5s) `scripts/scan.py`:
  1. Lists listening TCP ports with `lsof`.
  2. Resolves each port's owning process cwd (macOS: `lsof`, Linux: `/proc`).
  3. Matches cwd to a workspace via longest-prefix against
     `luvus workspace list`.
  4. Pushes one dock row per port to the `Ports` dock (right sidebar).
- Clicking a row runs the `open` action, which opens the row's URL with
  `open` / `xdg-open`.

Rows for processes inside a workspace get a `working` dot and the workspace
name; unmatched system listeners get an `idle` dot and the process name.

## Install

```sh
luvus module link /path/to/p-luvus
```

The dock appears on the first poll tick. Placement is configurable in
Settings, Layout (Left / Right / Off).

## Settings

- `interval`: poll interval in seconds (default 5).
- `max_ports`: max rows shown (default 30).

## Manual control

```sh
luvus module run ry.p-luvus refresh   # rescan now
luvus module settings ry.p-luvus      # view settings
```

To stop the poller: `kill $(cat .poll.pid)` in the module directory, then
`luvus module disable ry.p-luvus`.

## Requirements

- macOS or Linux with `lsof` and `python3` (stdlib only).
- Luvus >= 0.8.3.
