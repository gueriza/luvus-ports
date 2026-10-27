#!/bin/sh
# Open the clicked row's URL (value) in the default browser.

url="$LUVUS_MODULE_ROW_VALUE"
case "$url" in
  http://*|https://*) ;;
  *) echo "not a URL: $url" >&2; exit 1 ;;
esac

if command -v open >/dev/null 2>&1; then
  exec open "$url"
elif command -v xdg-open >/dev/null 2>&1; then
  exec xdg-open "$url"
else
  echo "no browser opener found (open/xdg-open)" >&2
  exit 1
fi
