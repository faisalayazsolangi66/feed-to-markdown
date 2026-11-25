# Feed to Markdown

Convert an RSS or Atom feed into a Markdown file.

## Requirements

- Python 3 (standard library only — no extra packages)

## Usage

```bash
python3 main.py https://example.com/feed.xml -o feed.md
python3 main.py --file feed.xml --limit 5
```

Options:

- `url` — feed URL (omit when using `--file`)
- `--file, -f FILE` — local feed XML file to read
- `-o, --output FILE` — output Markdown file (default: `feed.md`)
- `--limit N` — maximum entries to include (0 = all)
- `--timeout SECONDS` — request timeout (default: 10)

## Example

```bash
$ python3 main.py https://example.com/feed.xml -o feed.md
Wrote 3 entries from 'Example Blog' to feed.md
```

`feed.md` then looks like:

```markdown
# Example Blog

## First Post
[https://example.com/first](https://example.com/first)
*Mon, 24 Nov 2026 10:00:00 GMT*

The opening paragraph of the first post...
```

Unparseable XML, HTTP errors, and network failures are reported as
`ERROR` instead of crashing.
