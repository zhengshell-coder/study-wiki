// 我的图书馆（）Service Worker —— 只缓存页面程序本身；书的内容由页面读取，另存在 library-docs-v1
const CACHE = "library-shell-v1";
const CORE = ["./", "./index.html", "./reader.html", "./manifest.webmanifest", "./icon-180.png", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => Promise.all(CORE.map((u) => c.add(u).catch(() => {})))).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k.startsWith("library-shell-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;          // GitHub API 等跨域请求直接放行
  if (url.pathname.includes("/__doc/") || url.pathname.endsWith(".json")) return;   // 目录/索引由页面自己管理（带时间戳，别缓存）             // 书的离线副本由页面自己管理

  const isPage = req.mode === "navigate" || url.pathname.endsWith(".html") || url.pathname.endsWith("/") || url.pathname.endsWith(".webmanifest");
  if (isPage) {                                             // 页面：优先联网拿最新，失败用缓存
    e.respondWith(
      fetch(req).then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res; })
        .catch(() => caches.match(req, { ignoreSearch: true }).then((m) => m || caches.match("./index.html")))
    );
    return;
  }
  e.respondWith(                                            // 图标等静态资源：缓存优先
    caches.match(req).then((hit) => hit || fetch(req).then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); return res; }))
  );
});
