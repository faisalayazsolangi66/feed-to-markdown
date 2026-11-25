#!/usr/bin/env python3
"""Convert an RSS/Atom feed into a Markdown file.

Usage:
    python3 main.py https://example.com/feed.xml -o feed.md
    python3 main.py --file feed.xml --limit 5
"""
import argparse
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(text):
    return " ".join(TAG_RE.sub("", text or "").split())


def local(tag):
    return tag.rsplit("}", 1)[-1]


def find_text(item, names):
    for child in item:
        if local(child.tag) in names and child.text:
            return child.text.strip()
    return ""


def find_link(item):
    for child in item:
        if local(child.tag) == "link":
            if child.text and child.text.strip():
                return child.text.strip()
            if child.get("href"):
                return child.get("href")
    return ""


def parse_feed(raw):
    root = ET.fromstring(raw)
    title = ""
    items = []
    if local(root.tag) == "feed":  # Atom
        title = find_text(root, ["title"])
        items = [c for c in root if local(c.tag) == "entry"]
    else:  # RSS: channel > item
        channel = next((c for c in root if local(c.tag) == "channel"), root)
        title = find_text(channel, ["title"])
        items = [c for c in channel if local(c.tag) == "item"]
    entries = []
    for item in items:
        entries.append({
            "title": strip_tags(find_text(item, ["title"])),
            "link": find_link(item),
            "date": find_text(item, ["pubDate", "published", "updated"]),
            "summary": strip_tags(find_text(
                item, ["description", "summary", "content"])),
        })
    return title, entries


def to_markdown(feed_title, entries):
    lines = [f"# {feed_title or 'Feed'}", ""]
    for entry in entries:
        lines.append(f"## {entry['title'] or '(no title)'}")
        if entry["link"]:
            lines.append(f"[{entry['link']}]({entry['link']})")
        if entry["date"]:
            lines.append(f"*{entry['date']}*")
        if entry["summary"]:
            lines.append("")
            lines.append(entry["summary"])
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert an RSS/Atom feed into a Markdown file.")
    parser.add_argument("url", nargs="?",
                        help="feed URL (omit with --file)")
    parser.add_argument("--file", "-f", help="local feed XML file to read")
    parser.add_argument("-o", "--output", default="feed.md",
                        help="output Markdown file (default: feed.md)")
    parser.add_argument("--limit", type=int, default=0,
                        help="max entries to include (0 = all)")
    parser.add_argument("--timeout", type=float, default=10,
                        help="request timeout in seconds (default: 10)")
    args = parser.parse_args(argv)

    if args.file:
        with open(args.file, "rb") as handle:
            raw = handle.read()
    elif args.url:
        request = urllib.request.Request(
            args.url, headers={"User-Agent": "feed-to-markdown/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=args.timeout) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            print(f"ERROR: HTTP {exc.code} {exc.reason}", file=sys.stderr)
            return 1
        except urllib.error.URLError as exc:
            print(f"ERROR: {exc.reason}", file=sys.stderr)
            return 1
        except (TimeoutError, ValueError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    else:
        parser.error("give a feed URL or --file")

    try:
        feed_title, entries = parse_feed(raw)
    except ET.ParseError as exc:
        print(f"ERROR: could not parse feed XML: {exc}", file=sys.stderr)
        return 1
    if args.limit > 0:
        entries = entries[: args.limit]
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(to_markdown(feed_title, entries))
    print(f"Wrote {len(entries)} entr{'y' if len(entries) == 1 else 'ies'} "
          f"from '{feed_title or 'feed'}' to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
