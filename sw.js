const CACHE = "nalnaal-v19";
const ASSETS = [
  "./","./index.html","./styles.css","./app.js","./emblems.js",
  "./data.json","./manifest.json","./icons/icon-96.png","./icons/icon-144.png","./icons/icon-152.png","./icons/icon-180.png","./icons/icon-192.png","./icons/icon-512.png",
  "./images/new-surya.jpg","./images/new-naga.jpg","./images/new-deepam.jpg","./images/new-deepavali.jpg","./images/new-pongal.jpg","./images/new-karthigai-deepam.jpg","./images/new-vishnu.jpg","./images/new-shiva-nandi.jpg","./images/new-bairava.jpg","./images/new-durga.jpg","./images/new-aandaal.jpg","./images/new-murugan.jpg","./images/new-ganesha.jpg","./images/new-lakshmi.jpg","./images/new-krishna.jpg","./images/new-rama.jpg","./images/new-hanuman.jpg","./images/new-saraswati.jpg","./images/new-pournami.jpg","./images/new-periyava.jpg"
];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

// Strategy:
// - data.json  -> network-first (always freshest panchangam; falls back to cache offline)
// - app shell (HTML/CSS/JS/manifest) -> stale-while-revalidate: serve cached instantly,
//   fetch fresh in background and update cache, so the NEXT open is current.
//   Code changes reach users automatically without a version bump.
// - images/icons -> cache-first (rarely change; fast & offline-friendly)
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const path = new URL(e.request.url).pathname;

  if (path.endsWith("data.json")) {
    e.respondWith(
      fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return res;
      }).catch(() => caches.match(e.request))
    );
    return;
  }

  const isShell = path.endsWith("/") || path.endsWith(".html") ||
                  path.endsWith(".css") || path.endsWith(".js") ||
                  path.endsWith("manifest.json");
  if (isShell) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        const network = fetch(e.request).then(res => {
          if (res && res.status === 200) {
            const copy = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, copy));
          }
          return res;
        }).catch(() => cached);
        return cached || network;
      })
    );
    return;
  }

  e.respondWith(
    caches.match(e.request).then(c => c || fetch(e.request).then(res => {
      if (res && res.status === 200) {
        const copy = res.clone();
        caches.open(CACHE).then(cc => cc.put(e.request, copy));
      }
      return res;
    }))
  );
});
