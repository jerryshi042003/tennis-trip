// Offline cache for Tennis Trip. Built by src/build.py.
const VERSION = '6bca75bae2';
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "img/agstylevideos.jpg", "img/agu_tennis.jpg", "img/ajlimofficial.jpg", "img/alexdantipapa.jpg", "img/ata_association.jpg", "img/cbu_tennis.jpg", "img/cebuelitetennisclub.jpg", "img/chrispapa01.jpg", "img/chuouniv_tennis.jpg", "img/coach_czar.jpg", "img/coachlerafrancis.jpg", "img/dyancastillejo.jpg", "img/emon.vanlobensels.jpg", "img/everybodi.mnl.jpg", "img/iori_legend.jpg", "img/jeddyboy109.jpg", "img/johnnyarcilla1.jpg", "img/jrmtennis.jpg", "img/keisuke___ota.jpg", "img/kzm52tennis.jpg", "img/leone_tennis.jpg", "img/mahoutukaisally.jpg", "img/metromanilatennis.jpg", "img/mptenniscebu.jpg", "img/niegeldilemma.jpg", "img/ninotennis.jpg", "img/nodai_tennis_man.jpg", "img/pj_tierro.jpg", "img/racketoncourt.jpg", "img/rubenninogonzales.jpg", "img/shotakonishi.tennis.jpg", "img/skip.tan.jpg", "img/sng1980.jpg", "img/star_tennis_academy_official.jpg", "img/stefferoni.jpg", "img/tennislab_cebuph.jpg", "img/tennisunitedacademy.jpg", "img/thesiargaotennisclub.jpg", "img/whismaaark.jpg"];
const CACHE = 'tennis-trip-' + VERSION;
const FONTS = 'tennis-trip-fonts';

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE && k !== FONTS).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Google Fonts: cache on first use.
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    e.respondWith(caches.open(FONTS).then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      try { const res = await fetch(req); if (res.ok || res.type === 'opaque') c.put(req, res.clone()); return res; }
      catch (err) { return hit || Response.error(); }
    }));
    return;
  }
  if (url.origin !== location.origin) return;

  // Page: network first so updates land, cache when offline.
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(res => {
      const copy = res.clone(); caches.open(CACHE).then(c => c.put('./', copy)); return res;
    }).catch(() => caches.match('./').then(r => r || caches.match('index.html'))));
    return;
  }

  // Everything else: cache first.
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  })));
});
