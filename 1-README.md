# AI Daily Digest

A small Python script that pulls the latest AI news from RSS feeds and writes a clean Markdown digest, so you can read the day's AI news in two minutes instead of opening ten tabs.

**Problem it solves:** AI news is spread across many blogs. This collects the newest posts into one page, and can optionally add a short AI-written summary.

## Quick start

```bash
git clone https://github.com/Dev8628/ai-daily-digest.git
cd ai-daily-digest
python3 digest.py
```

No installs needed (Python 3.9+, standard library only). The digest prints in your terminal and is saved to `digests/YYYY-MM-DD.md`.

## Optional: AI summary

If you set an OpenAI-compatible API key, the digest starts with a 3-bullet summary:

```bash
export OPENAI_API_KEY=your_key_here
python3 digest.py
```

Optional settings: `DIGEST_MODEL` (default `gpt-4o-mini`) and `OPENAI_BASE_URL`. Without a key, the script still works and shows headlines and excerpts. Never commit your key.

## Choose your sources

Edit `feeds.txt` and add one RSS or Atom URL per line. A feed that fails to load is skipped.

## Example output

```
# AI Daily Digest - 2026-10-05

## Hugging Face - Blog
- [Open TTS Leaderboard: ...](https://huggingface.co/blog/open-tts-leaderboard)
```

## Ideas for next steps

- Run it every morning with cron or GitHub Actions
- Send the digest to email or Telegram
- Filter by keywords

## License

MIT
