#!/usr/bin/env python3
"""Download the GitHub avatar to use as the ASCII portrait source."""
import sys
import requests

USERNAME = "Fog-coder"
OUT = "source-photo.png"


def main():
    urls = [
        f"https://github.com/{USERNAME}.png?size=460",
        f"https://github.com/{USERNAME}.png",
    ]
    last_err = None
    for url in urls:
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(OUT, "wb") as f:
                f.write(r.content)
            print(f"Saved {OUT} ({len(r.content)} bytes) from {url}")
            return
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"Failed {url}: {e}", file=sys.stderr)
    raise SystemExit(f"Could not fetch avatar: {last_err}")


if __name__ == "__main__":
    main()
