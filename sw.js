const V = 'jus-v10';
const CORE = ['./', 'index.html', 'styles.css', 'app.js', 'manifest.json', 'icon.svg',
  'data/core.js', 'data/heat.js', 'data/leis_seed.js', 'data/leis_manifest.js',
  'data/jurisprudencia.js', 'data/estudo.js', 'data/principios.js', 'data/conferencia.js', 'data/treino.js', 'juris.js', 'editais.js', 'data/mapas_img.js'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(CORE))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request, { cache: 'no-cache' }).then(r => { const c = r.clone(); caches.open(V).then(ch => ch.put(e.request, c)); return r; }).catch(() => caches.match(e.request)));
});
