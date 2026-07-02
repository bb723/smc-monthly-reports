# SMC Monthly Reports

Password-protected static site for Standard Management Company's internal monthly
cash / operations reports, served via GitHub Pages.

**How the protection works:** each report's markdown is encrypted with
AES-256-GCM (key derived from the shared password via PBKDF2-SHA256, 600k
iterations) before it is committed. The repo contains only ciphertext;
decryption happens in the reader's browser (WebCrypto). Ask Brett for the
password out-of-band — it is never committed here.

## Adding a month

```bash
python tools/encrypt_report.py "<path to report.md>" 2026-07 "July 2026 — Cash Report" --password "<pw>"
git add reports/ manifest.json
git commit -m "Add July 2026 report"
git push
```

The site picks up new entries from `manifest.json` automatically (newest first).

Source reports live in the SMC workspace at `Finance/Reports/` (not in this repo).
