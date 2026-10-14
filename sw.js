// Service worker de ChaskiBoom Battle Chess (generado por tools/build.py; editar src/sw.js).
// Estrategia "red primero": siempre se baja la última versión del juego y la copia en caché
// solo se usa si no hay conexión. Así una publicación nueva se ve en la próxima apertura.
const CACHE = 'chaskiboom-v1.37';
const CDN = ['cdn.jsdelivr.net', 'fonts.googleapis.com', 'fonts.gstatic.com', 'www.gstatic.com'];

// El service worker nuevo NO reemplaza al viejo apenas se instala: en iPhone eso cortaba las descargas
// que la página tenía en curso (los modelos) y la carga quedaba trabada. Espera a que la página se lo pida
// justo antes de recargar (o a que se cierre la app).
self.addEventListener('install', () => {});
self.addEventListener('message', e => { if (e.data === 'skipWaiting') self.skipWaiting(); });

self.addEventListener('activate', e => e.waitUntil((async () => {
  for (const k of await caches.keys()) if (k.startsWith('chaskiboom-') && k !== CACHE) await caches.delete(k);
  await self.clients.claim();
})()));

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || req.headers.has('range')) return;          // audio por rangos y POST: directo a la red
  const url = new URL(req.url);
  const propio = url.origin === location.origin;
  if (!propio && !CDN.includes(url.hostname)) return;                    // Firebase (base de datos, auth), etc.: sin tocar
  e.respondWith((async () => {
    try {
      // lo propio se pide con no-cache: el navegador revalida con el servidor en vez de usar su caché HTTP
      // (GitHub Pages permite guardar 10 min; sin esto una versión nueva podía tardar en verse)
      const res = await (!propio ? fetch(req)
        : req.mode === 'navigate' ? fetch(req.url, { cache: 'no-cache', credentials: 'same-origin' })
        : fetch(new Request(req, { cache: 'no-cache' })));
      if (res.ok || res.type === 'opaque') {
        const copia = res.clone();
        caches.open(CACHE).then(c => c.put(req, copia)).catch(() => {});
      }
      return res;
    } catch (err) {
      const hit = await caches.match(req, { ignoreSearch: req.mode === 'navigate' });
      if (hit) return hit;
      throw err;
    }
  })());
});
