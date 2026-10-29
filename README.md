# Sushma & Mohith — Wedding Invitation (clone)

A faithful static clone of https://mohith-weds-sushma.lovable.app/

## Run

```bash
cd public
python3 -m http.server 8777
# open http://localhost:8777/
```

Any static file server works (the site is pure HTML/CSS/JS — no build step, no backend).

## What's here

```
public/
  index.html           # the page (self-contained; links CSS + local images)
  assets/              # styles.css (compiled Tailwind), monogram, mandala,
                       # hero bg, bride/groom illustrations. Fonts load from Google Fonts.
  story/               # couple photo, event photos, envelope letter, evil-eye
src/
  build.py                 # regenerates index.html from the captured source
  source-capture.min.html  # pristine captured HTML — the build input
```

## How it was built

The original is a Lovable (React/Vite) app that server-renders its full markup.
`src/build.py` takes that captured HTML and:

1. rewrites all remote/hashed asset URLs to the local copies in `public/`,
2. strips the React/analytics bundles and framework hydration scripts,
3. injects vanilla JS reproducing the interactivity the React app provided:
   - **Envelope intro** — tap the wax-seal monogram to flip the flap open, raise the
     letter, and fade the overlay away to reveal the page.
   - **Background music** — `assets/wedding-music.mp3` loops from the moment the
     invitation opens (the seal tap is the user gesture browsers require for audio);
     a floating speaker button (bottom-right) mutes/unmutes, and playback pauses
     while the tab is hidden.
   - **Countdown** — live days/hrs/min/sec to 20 Nov 2026, 8:30 AM IST (Muhurtha).
   - **Scratch-to-reveal** — canvas "Save the Date" card you scratch with mouse/touch.
   - **Scroll reveals** — sections fade/rise in as they enter the viewport.

The falling-petal animations, floating motion, gradients, fonts and all layout come
straight from the original compiled CSS (`assets/styles.css`), so the look matches exactly.

To rebuild after editing: `python3 src/build.py` (run from the repo root).

## Handy URL flags (clone-only conveniences)

- `/?open` or `#open` — skip the envelope intro and go straight to the invitation.
- `/?open&flat` — also relax `min-height:100vh` / reveal everything (used for screenshots).
