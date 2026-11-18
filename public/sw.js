// Offline cache for Tennis Trip. Built by src/build.py.
const VERSION = '985bdd1a98';
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "img/7_7_shin.jpg", "img/agstylevideos.jpg", "img/agu_tennis.jpg", "img/ajlimofficial.jpg", "img/alexdantipapa.jpg", "img/amechan_59.jpg", "img/anotherdayanothercourt.jpg", "img/aryoncourt.jpg", "img/asmaraurbanresort.jpg", "img/ata_association.jpg", "img/austennis_.jpg", "img/avari.tennis.jpg", "img/cbu_tennis.jpg", "img/cebuelitetennisclub.jpg", "img/chikayasato.jpg", "img/chrispapa01.jpg", "img/chuouniv_tennis.jpg", "img/citigreentennisresort.jpg", "img/coach.jedaquino.jpg", "img/coach_czar.jpg", "img/coachlerafrancis.jpg", "img/coachwaldobernardo.jpg", "img/cots.jr.flores.jpg", "img/ctc.chitose_tennis_club.jpg", "img/dropshot.ph.jpg", "img/dyancastillejo.jpg", "img/emon.vanlobensels.jpg", "img/epsom_tennis.jpg", "img/erikasematennis.jpg", "img/everybodi.mnl.jpg", "img/faye_oncourt.jpg", "img/fernandezloucas.jpg", "img/g2play_tennis.jpg", "img/gamepoint.tennis.jpg", "img/gentry_open.jpg", "img/godaikameido.jpg", "img/hiroyasueh0727.jpg", "img/iori_legend.jpg", "img/jasperamorin.jpg", "img/jbxaguilar.jpg", "img/jeddyboy109.jpg", "img/jjktennis.jpg", "img/johnnyarcilla1.jpg", "img/johnreynolds___.jpg", "img/joy_tennis_tokyo.jpg", "img/jrmtennis.jpg", "img/julienmakrai.jpg", "img/keisuke___ota.jpg", "img/komae_indoor_tennis_school.jpg", "img/kzm52tennis.jpg", "img/leone_tennis.jpg", "img/mahoutukaisally.jpg", "img/metromanilatennis.jpg", "img/mieri_yao.jpg", "img/mptenniscebu.jpg", "img/nanagram_128.jpg", "img/niegeldilemma.jpg", "img/ninotennis.jpg", "img/nodai_tennis_man.jpg", "img/ogusuke0209.jpg", "img/openplayandaway.jpg", "img/otona_tennis.summer_flat.jpg", "img/ots___official.jpg", "img/philta_official.jpg", "img/pinoyprosports.jpg", "img/pj_tierro.jpg", "img/racketoncourt.jpg", "img/raimu__.4.jpg", "img/rubenninogonzales.jpg", "img/ryotatanuma_tennis.jpg", "img/ryusei__tennis.jpg", "img/salute_tennis.jpg", "img/shinn_hiramatsu.jpg", "img/shogotennisplayer.jpg", "img/shotakonishi.tennis.jpg", "img/sketch2_tennis.jpg", "img/skip.tan.jpg", "img/sng1980.jpg", "img/star_tennis_academy_official.jpg", "img/stefferoni.jpg", "img/t_socialt.jpg", "img/ta1_saito.jpg", "img/takuo_3.jpg", "img/tarapalo.ph.jpg", "img/tautenikun.jpg", "img/team_zenpukuji.jpg", "img/teniste2025.jpg", "img/tenneastacademy.jpg", "img/tennis.boys.tokyo.jpg", "img/tennishub_100.jpg", "img/tennislab_cebuph.jpg", "img/tennismnl.jpg", "img/tennisnomad.jpg", "img/tennisunitedacademy.jpg", "img/tennisupd.jpg", "img/the.tennisloft.jpg", "img/thebaselinesocietyph.jpg", "img/theqctennistriangle.jpg", "img/thesiargaotennisclub.jpg", "img/tipsytennispodcast.jpg", "img/uno_maaya.jpg", "img/utr_protennistour_japan.jpg", "img/whismaaark.jpg", "img/will.tennis25.jpg", "img/yawntennis.jpg", "img/yuya_045.jpg"];
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
