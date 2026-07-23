# Deploying to Render

This repo is already set up for a one-click [Render](https://render.com) Blueprint deployment on Render's **free** plan - the Dockerfile and `render.yaml` are all in place. You just need to click through the setup and provide your own secrets.

## Steps

1. Push this repo to GitHub if it isn't already (public or private both work - Render just needs read access).
2. Go to the [Render dashboard](https://dashboard.render.com) → **New +** → **Blueprint**.
3. Select this repository. Render will read `render.yaml` automatically and propose one free web service (`bautraeger-crawler`).
4. Before the first deploy, Render will ask for the environment variables marked `sync: false` in `render.yaml`:
   - `ANTHROPIC_API_KEY` - your Claude API key
   - `PORTAL_PASSWORT` - the shared login password for the web dashboard
   - `FLASK_SECRET_KEY` - a random secret for Flask sessions, e.g. generate one locally with:
     ```bash
     python3 -c "import secrets; print(secrets.token_hex(32))"
     ```
5. Click **Apply** / **Deploy**. The first build takes a few minutes (the Playwright base image is large).
6. Once live, Render gives you a URL like `https://bautraeger-crawler.onrender.com`. Open it, log in with `PORTAL_PASSWORT`, and trigger a crawl from the dashboard.

## Notes

- **No persistent storage on the free plan**: the SQLite database and Excel export live only inside the container and reset on every restart or redeploy. Fine for this portfolio version (fictional placeholder data anyway); for real, durable data, add a `disk:` block back to `render.yaml` and switch to a paid plan (check [render.com/pricing](https://render.com/pricing) for current rates).
- Render's free web services **spin down after inactivity** and take maybe 30-60 seconds to wake back up on the next visit - the first request after a while looks slow, not broken.
- `autoDeploy: true` means every push to the connected branch redeploys automatically - fine for a portfolio demo, worth turning off if you don't want that.

<!-- TODO(Lennard): Live-URL nach Deployment oben ins README eintragen -->
