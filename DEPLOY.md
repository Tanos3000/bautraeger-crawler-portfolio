# Deploying to Render

This repo is already set up for a one-click [Render](https://render.com) Blueprint deployment - the Dockerfile, `render.yaml`, and persistent disk config are all in place. You just need to click through the setup and provide your own secrets.

## Steps

1. Push this repo to GitHub if it isn't already (public or private both work - Render just needs read access).
2. Go to the [Render dashboard](https://dashboard.render.com) → **New +** → **Blueprint**.
3. Select this repository. Render will read `render.yaml` automatically and propose one web service (`bautraeger-crawler`) with a 1 GB persistent disk mounted at `/var/data`.
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

- `DATEN_ORDNER` is already set to the persistent disk path (`/var/data`) via `render.yaml`, so the SQLite database and Excel export survive restarts and redeploys.
- The `starter` plan in `render.yaml` is Render's smallest paid tier (needed for the persistent disk); adjust if you want a different plan.
- `autoDeploy: true` means every push to the connected branch redeploys automatically - fine for a portfolio demo, worth turning off if you don't want that.

<!-- TODO(Lennard): Live-URL nach Deployment oben ins README eintragen -->
