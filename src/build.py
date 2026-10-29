#!/usr/bin/env python3
"""Transform the captured server-rendered HTML into a standalone static clone.

Reads the pristine single-line capture (src/source-capture.min.html) so the
output is independent of any reformatting done to the readable reference
(src/source-capture.html). Run from the repo root: python3 src/build.py
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
raw = open(os.path.join(HERE, 'source-capture.min.html'), encoding='utf-8').read()

# --- 1. Rewrite /__l5e/assets-v1/<uuid>/<file> -> local path ---
L5E = {
    'monogram.png': '/assets/monogram.jpg',
    'story-bike.jpeg': '/story/story-bike.jpeg',
    'story-mirror.jpeg': '/story/story-mirror.jpeg',
    'story-dominos.jpeg': '/story/story-dominos.jpeg',
    'story-saree.jpeg': '/story/story-saree.jpeg',
    'story-sunset.png': '/story/story-sunset.png',
    'evil-eye.png': '/story/evil-eye.png',
    'couple-dance.jpg': '/story/couple-dance.jpg',
    'event-sangeeth-v2.png': '/story/event-sangeeth.png',
    'event-haldi-groom-v2.png': '/story/event-haldi-groom.png',
    'event-haldi-bride.jpg': '/story/event-haldi-bride.jpg',
    'event-reception-photo.png': '/story/event-reception.jpg',
    'event-wedding.png': '/story/event-wedding.jpg',
    'letter-inside.jpg': '/story/letter-inside.jpg',
}

def l5e_sub(m):
    fname = m.group(1)
    return L5E.get(fname, '/story/' + fname)

raw = re.sub(r'/__l5e/assets-v1/[0-9a-f-]+/([A-Za-z0-9._-]+)', l5e_sub, raw)

# --- 2. Rewrite hashed /assets/ files -> clean local names ---
HASHED = {
    '/assets/styles-DmCjOVcG.css': '/assets/styles.css',
    '/assets/mandala-DYhy1LQT.png': '/assets/mandala.png',
    '/assets/bapu-bride-DWZ7ntw3.png': '/assets/bapu-bride.jpg',
    '/assets/bapu-groom-CyjNVYxk.png': '/assets/bapu-groom.jpg',
    '/assets/hero-bg-BxJA4MsN.jpg': '/assets/hero-bg.jpg',
}
for a, b in HASHED.items():
    raw = raw.replace(a, b)

# --- 2b. Point the social-preview image (og:image / twitter:image) at a local asset
#         instead of the original project's remote upload. ---
raw = raw.replace(
    'https://storage.googleapis.com/gpt-engineer-file-uploads/p258ALT5WGc0WCe3ETF9MArESbx1/social-images/social-1784056272518-IMG_1626.webp',
    '/assets/monogram.jpg')

# --- 3. Strip framework / analytics scripts & preloads ---
# injected analytics + events scripts
raw = re.sub(r'<script defer src="/~flock\.js"[^>]*></script>', '', raw)
raw = re.sub(r'<script defer src="/__l5e/events[^>]*></script>', '', raw)
# modulepreloads for the React bundle
raw = re.sub(r'<link rel="modulepreload"[^>]*/>', '', raw)
# TanStack scroll-restoration inline script
raw = re.sub(r'<script>\(function\(a,f\).*?document\.currentScript\.remove\(\)</script>', '', raw, flags=re.S)
# TSR stream barrier inline script
raw = re.sub(r'<script class="\$tsr"[^>]*>.*?</script>', '', raw, flags=re.S)
# the module entry script
raw = re.sub(r'<script type="module" async="" src="/assets/index-BuZuJ4br\.js">\s*</script>', '', raw)

# --- 4. Inject our own CSS + interactivity JS before </body> ---
INJECT = r'''
<style>
  html { scroll-behavior: smooth; }
  /* hero reveal after the invitation is opened */
  .reveal-ready { opacity: 0; }
  .reveal-in { animation: fade-up 1200ms cubic-bezier(0.22,1,0.36,1) forwards; }
  /* generic scroll reveal for in-view sections */
  .sr { opacity: 0; transform: translateY(26px); transition: opacity 900ms ease, transform 900ms cubic-bezier(0.22,1,0.36,1); }
  .sr.visible { opacity: 1; transform: none; }
</style>
<script>
(function () {
  "use strict";

  /* ---------- 0. Background music (looping, starts when invitation opens) ---------- */
  var audio = document.createElement('audio');
  audio.src = '/assets/wedding-music.mp3';
  audio.loop = true;
  audio.preload = 'auto';
  audio.volume = 0.5;
  document.body.appendChild(audio);

  var musicStarted = false;   // has playback ever begun
  var isMuted = false;        // user toggled mute

  var SPK = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M16.5 8.5a5 5 0 0 1 0 7"/><path d="M19 6a8 8 0 0 1 0 12"/></svg>';
  var MUTE = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9v6h4l5 4V5L8 9H4z"/><path d="M22 9l-6 6"/><path d="M16 9l6 6"/></svg>';

  var musicBtn = document.createElement('button');
  musicBtn.className = 'fixed bottom-5 right-5 z-[80] w-12 h-12 rounded-full flex items-center justify-center border border-gold/60 bg-background/85 backdrop-blur-sm shadow-elegant text-maroon transition-transform hover:scale-110';
  musicBtn.style.opacity = '0';
  musicBtn.style.pointerEvents = 'none';
  musicBtn.style.transition = 'opacity 600ms ease';
  musicBtn.setAttribute('aria-label', 'Mute music');
  musicBtn.innerHTML = SPK;
  document.body.appendChild(musicBtn);

  function reflectBtn() {
    musicBtn.innerHTML = isMuted ? MUTE : SPK;
    musicBtn.setAttribute('aria-label', isMuted ? 'Unmute music' : 'Mute music');
  }
  function showMusicBtn() {
    musicBtn.style.opacity = '1';
    musicBtn.style.pointerEvents = 'auto';
  }
  function startMusic() {
    if (musicStarted) return;
    audio.muted = false;
    audio.play().then(function () { musicStarted = true; isMuted = false; reflectBtn(); showMusicBtn(); })
                .catch(function () { showMusicBtn(); });  // show toggle even if autoplay was blocked
  }
  musicBtn.addEventListener('click', function () {
    if (!musicStarted) { audio.muted = false; audio.play().then(function () { musicStarted = true; isMuted = false; reflectBtn(); }).catch(function () {}); return; }
    isMuted = !isMuted;
    audio.muted = isMuted;
    reflectBtn();
  });
  // pause when the tab is hidden; resume when visible (unless user muted)
  document.addEventListener('visibilitychange', function () {
    if (!musicStarted) return;
    if (document.hidden) audio.pause();
    else if (!isMuted) audio.play().catch(function () {});
  });

  /* ---------- 1. Envelope / seal intro ---------- */
  var overlay  = document.querySelector('div[style*="perspective:1600px"]');
  var openBtn  = document.querySelector('button[aria-label="Open invitation"]');
  var letter   = document.querySelector('div[style*="letter-inside"]');
  var flap     = document.querySelector('div[style*="rotateX(0deg)"]');
  var tapText  = overlay ? overlay.querySelector('p.animate-pulse') : null;
  var hero     = document.querySelector('section.min-h-screen .opacity-0') ||
                 document.querySelector('.opacity-0.max-w-3xl');

  if (hero) { hero.classList.remove('opacity-0'); hero.classList.add('reveal-ready'); }
  document.body.style.overflow = 'hidden';

  var opened = false;
  function openInvitation() {
    if (opened || !overlay) return;
    opened = true;
    startMusic();
    if (flap)   flap.style.transform = 'rotateX(-180deg)';
    if (letter) {
      letter.style.opacity = '1';
      letter.style.transform = 'translate3d(0,0,0) scale(1)';
    }
    if (tapText) tapText.style.opacity = '0';
    if (openBtn) { openBtn.style.opacity = '0'; openBtn.style.transform = 'translate(-50%,-50%) scale(0.6)'; }

    setTimeout(function () {
      overlay.style.opacity = '0';
      overlay.style.pointerEvents = 'none';
    }, 1250);
    setTimeout(function () {
      if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
      document.body.style.overflow = '';
      if (hero) { hero.classList.remove('reveal-ready'); hero.classList.add('reveal-in'); }
    }, 2450);
  }
  if (openBtn)  openBtn.addEventListener('click', openInvitation);
  if (overlay)  overlay.addEventListener('click', function (e) {
    if (e.target === overlay) openInvitation();
  });
  // optional skip-intro: open the invitation straight away via /?open or #open
  if (/\bopen\b/.test(location.search) || location.hash === '#open') {
    if (overlay) { overlay.style.transition = 'none'; overlay.style.display = 'none'; }
    document.body.style.overflow = '';
    if (hero) { hero.classList.remove('opacity-0', 'reveal-ready'); hero.classList.add('reveal-in'); }
    opened = true;
    startMusic();
  }
  // screenshot aid only: relax min-h-screen + show all scroll-reveal content at once
  if (/\bflat\b/.test(location.search)) {
    var st = document.createElement('style');
    st.textContent = '.min-h-screen{min-height:auto !important;padding-top:4rem;padding-bottom:4rem}.sr{opacity:1 !important;transform:none !important}';
    document.head.appendChild(st);
  }

  /* ---------- 2. Countdown to 20 Nov 2026, 8:30 AM IST (Muhurtha) ---------- */
  // 8:30 IST (+05:30) == 03:00 UTC
  var target = Date.UTC(2026, 10, 20, 3, 0, 0);
  var boxes = document.querySelectorAll('.tabular-nums');
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function tick() {
    if (boxes.length < 4) return;
    var diff = target - Date.now();
    if (diff < 0) diff = 0;
    var s = Math.floor(diff / 1000);
    var d = Math.floor(s / 86400);
    var h = Math.floor((s % 86400) / 3600);
    var m = Math.floor((s % 3600) / 60);
    var sec = s % 60;
    boxes[0].textContent = d;
    boxes[1].textContent = pad(h);
    boxes[2].textContent = pad(m);
    boxes[3].textContent = pad(sec);
  }
  tick();
  setInterval(tick, 1000);

  /* ---------- 3. Scratch-to-reveal "Save the Date" ---------- */
  var canvas = document.querySelector('canvas');
  if (canvas) {
    var ctx = canvas.getContext('2d');
    var ratio = window.devicePixelRatio || 1;
    var drawing = false, cleared = false;

    function paintCover() {
      var r = canvas.getBoundingClientRect();
      canvas.width  = Math.max(1, Math.floor(r.width  * ratio));
      canvas.height = Math.max(1, Math.floor(r.height * ratio));
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      var w = r.width, h = r.height;
      var g = ctx.createLinearGradient(0, 0, w, h);
      g.addColorStop(0,   '#d9a94e');
      g.addColorStop(0.5, '#c6873a');
      g.addColorStop(1,   '#a85f2b');
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, w, h);
      // subtle sheen specks
      ctx.fillStyle = 'rgba(255,240,200,0.14)';
      for (var i = 0; i < 90; i++) {
        ctx.beginPath();
        ctx.arc(Math.random() * w, Math.random() * h, Math.random() * 1.6, 0, 6.3);
        ctx.fill();
      }
      ctx.fillStyle = 'rgba(255,248,230,0.95)';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.font = '600 ' + Math.round(Math.min(w, h) * 0.07) + 'px "Cormorant Garamond", serif';
      ctx.fillText('✧  Scratch here to reveal  ✧', w / 2, h / 2);
      ctx.font = '400 ' + Math.round(Math.min(w, h) * 0.045) + 'px "Cormorant Garamond", serif';
      ctx.fillText('our big day', w / 2, h / 2 + Math.min(w, h) * 0.085);
    }
    paintCover();

    function pos(e) {
      var r = canvas.getBoundingClientRect();
      var p = e.touches ? e.touches[0] : e;
      return { x: p.clientX - r.left, y: p.clientY - r.top };
    }
    function scratch(e) {
      if (!drawing || cleared) return;
      var p = pos(e);
      ctx.globalCompositeOperation = 'destination-out';
      ctx.beginPath();
      ctx.arc(p.x, p.y, 38, 0, 6.3);
      ctx.fill();
      ctx.globalCompositeOperation = 'source-over';
      maybeClear();
    }
    var checkTick = 0;
    function maybeClear() {
      if (cleared || (checkTick++ % 4)) return;
      var img = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      var clear = 0;
      for (var i = 3; i < img.length; i += 4 * 40) { if (img[i] === 0) clear++; }
      var total = img.length / (4 * 40);
      if (clear / total > 0.15) {
        cleared = true;
        canvas.style.transition = 'opacity 700ms ease';
        canvas.style.opacity = '0';
        setTimeout(function () { canvas.style.display = 'none'; }, 750);
      }
    }
    canvas.addEventListener('mousedown', function (e) { drawing = true; scratch(e); });
    window.addEventListener('mouseup',   function () { drawing = false; });
    canvas.addEventListener('mousemove', scratch);
    canvas.addEventListener('touchstart', function (e) { drawing = true; scratch(e); e.preventDefault(); }, { passive: false });
    window.addEventListener('touchend',   function () { drawing = false; });
    canvas.addEventListener('touchmove',  function (e) { scratch(e); e.preventDefault(); }, { passive: false });
    window.addEventListener('resize', function () { if (!cleared) paintCover(); });
  }

  /* ---------- 4. Scroll-reveal for story / event / venue sections ---------- */
  var reveals = [];
  document.querySelectorAll('section').forEach(function (sec, idx) {
    if (idx === 0) return; // hero handled separately
    sec.querySelectorAll(':scope > div > *, article').forEach(function (el) {
      el.classList.add('sr');
      reveals.push(el);
    });
  });
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('visible'); });
  }
})();
</script>
'''

raw = raw.replace('</body>', INJECT + '\n</body>')

out = os.path.join(HERE, '..', 'public', 'index.html')
open(out, 'w', encoding='utf-8').write(raw)
print('Wrote %s  (%d bytes)' % (os.path.normpath(out), len(raw)))
