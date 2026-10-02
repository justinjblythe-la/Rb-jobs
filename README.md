# RB Jobs — glasses job board

Web app for Meta Ray-Ban Display glasses (600×600, Neural Band navigation) showing open RB Cable jobs.

- `index.html` — the app (PIN keypad → summary tiles → job list → job detail)
- `data.json` — job list, AES-encrypted with the PIN (no readable job info in the repo)
- `sw.js`, `manifest.webmanifest`, `icon-*.png` — offline support and app icon
- `tools/encrypt_jobs.py` — rebuilds `data.json` from the job board export

## Controls
Swipe = move · pinch = open / next page · back gesture = go back.
After unlocking, the glasses stay unlocked for 12 hours.

## Updating the job list
```
pip install cryptography
RBJOBS_PIN=<your PIN> python3 tools/encrypt_jobs.py <jobs folder or jobs.json> [meta.json]
```
Then commit the new `data.json`. Never commit the plaintext export.

## Hosting
GitHub Pages: Settings → Pages → Deploy from branch → `main` / root.
