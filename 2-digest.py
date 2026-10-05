#!/usr/bin/env python3
"""AI Daily Digest: pull AI news from RSS feeds and write a short Markdown digest.

Works with no API key (headlines + short excerpts). If OPENAI_API_KEY is set,
it also asks an AI model for a 2-3 line summary of the day.
"""
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

MAX_PER_FEED = 5
UA = {"User-Agent": "Mozilla/5.0 (ai-daily-digest)"}


def read_feeds(path="feeds.txt"):
    with open(path, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]


def clean(text, limit=220):
    text = re.sub(r"<[^>]+>", " ", html.unescape(text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()


def parse(xml_bytes):
    """Return (feed_title, [items]) for RSS or Atom."""
    root = ET.fromstring(xml_bytes)
    strip = lambda tag: tag.split("}")[-1]
    title = ""
    items = []
    for el in root.iter():
        t = strip(el.tag)
        if t == "title" and not title:
            title = (el.text or "").strip()
        if t in ("item", "entry"):
            d = {"title": "", "link": "", "summary": ""}
            for c in el:
                ct = strip(c.tag)
                if ct == "title":
                    d["title"] = clean(c.text, 140)
                elif ct == "link":
                    d["link"] = (c.text or "").strip() or c.attrib.get("href", "")
                elif ct in ("description", "summary", "content") and not d["summary"]:
                    d["summary"] = clean(c.text)
            if d["title"]:
                items.append(d)
    return title, items


def ai_summary(items):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    model = os.environ.get("DIGEST_MODEL", "gpt-4o-mini")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    lines = "\n".join(f"- {i['title']}: {i['summary']}" for i in items[:30])
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You summarise AI news. Use only the items given. Be factual, no hype."},
            {"role": "user", "content": "Write a 3-bullet summary of today's most important items:\n" + lines},
        ],
    }
    req = urllib.request.Request(
        base + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()
    except Exception as e:  # keep the digest useful even if the AI call fails
        print(f"AI summary skipped: {e}", file=sys.stderr)
        return None


def main():
    sections, all_items = [], []
    for url in read_feeds():
        try:
            title, items = parse(fetch(url))
        except Exception as e:
            print(f"Skipped {url}: {e}", file=sys.stderr)
            continue
        items = items[:MAX_PER_FEED]
        all_items += items
        lines = [f"## {title or url}"]
        for i in items:
            lines.append(f"- [{i['title']}]({i['link']})" + (f"\n  {i['summary']}" if i["summary"] else ""))
        sections.append("\n".join(lines))
    today = dt.date.today().isoformat()
    out = [f"# AI Daily Digest - {today}", ""]
    summary = ai_summary(all_items)
    if summary:
        out += ["## Summary", summary, ""]
    out += sections
    text = "\n\n".join(out) + "\n"
    os.makedirs("digests", exist_ok=True)
    path = f"digests/{today}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()
