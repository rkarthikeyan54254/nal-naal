const CACHE = "nalnaal-v18";
const ASSETS = [
  "./","./index.html","./styles.css","./app.js","./emblems.js",
  "./data.json","./manifest.json","./icons/icon-96.png","./icons/icon-144.png","./icons/icon-152.png","./icons/icon-180.png","./icons/icon-192.png","./icons/icon-512.png",
  "./images/new-surya.jpg","./images/new-naga.jpg","./images/new-deepam.jpg","./images/new-deepavali.jpg","./images/new-pongal.jpg","./images/new-karthigai-deepam.jpg","./images/new-vishnu.jpg","./images/new-shiva-nandi.jpg","./images/new-bairava.jpg","./images/new-durga.jpg","./images/new-aandaal.jpg","./images/new-murugan.jpg","./images/new-ganesha.jpg","./images/new-lakshmi.jpg","./images/new-krishna.jpg","./images/new-rama.jpg","./images/new-hanuman.jpg","./images/new-saraswati.jpg","./images/new-pournami.jpg","./images/new-periyava.jpg"
];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (url.pathname.endsWith("data.json")) {
    e.respondWith(fetch(e.request).then(res => { const c = res.clone(); caches.open(CACHE).then(cc => cc.put(e.request, c)); return res; }).catch(() => caches.match(e.request)));
  } else {
    e.respondWith(caches.match(e.request).then(c => c || fetch(e.request)));
  }
});
