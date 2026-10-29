# Roopa & Mohan — Wedding Invitation

A self-contained static wedding invitation site: an animated envelope/seal intro,
background music, a live countdown, a scratch "Save the Date", event details, and a
venue map. Pure HTML/CSS/JS — no build step or backend required to serve it.

## Run locally

```bash
cd public
python3 -m http.server 8777
# open http://localhost:8777/
```

Any static file server works.

## What's here

```
public/                    # the deployable site (this folder is what gets hosted)
  index.html               # the page (self-contained; links CSS + local images)
  assets/                  # styles.css, monogram, mandala, hero bg,
                           # bride/groom illustrations, wedding-music.mp3
  story/                   # couple photo, event photos, envelope letter, evil-eye
src/
  build.py                 # regenerates public/index.html from the source
  source-capture.min.html  # HTML source — the build input
```

## Features

- **Envelope intro** — tap the wax-seal monogram to flip it open, raise the letter,
  and reveal the invitation.
- **Background music** — `assets/wedding-music.mp3` loops from the moment the
  invitation opens (the seal tap satisfies the browser gesture required for audio);
  a floating speaker button (bottom-right) mutes/unmutes, and playback pauses while
  the tab is hidden.
- **Countdown** — live days/hrs/min/sec to the Muhurtha (20 Nov 2026, 8:30 AM IST).
- **Scratch-to-reveal** — a canvas "Save the Date" card you scratch (mouse or touch).
- **Scroll reveals** — sections fade and rise in as they enter the viewport.
- **Mobile-friendly** — fully responsive, no horizontal overflow.

## Editing

Content lives in `src/source-capture.min.html`; the interactive scripts are injected
by `src/build.py`. After editing either, regenerate the page:

```bash
python3 src/build.py
```

### Handy URL flags

- `/?open` or `#open` — skip the envelope intro and go straight to the invitation.
- `/?open&flat` — also relax full-height sections / reveal everything at once.

## Deploy

The `public/` folder is a plain static site. On Vercel: import the repo, set
**Output Directory** to `public`, and deploy. Any static host (Netlify, Cloudflare
Pages, GitHub Pages) works the same way.
