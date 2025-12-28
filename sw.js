// SNT Automation Tools - Service Worker   
// Works with GitHub Pages (root or /docs folder)

const CACHE_NAME = 'snt-tools-v1';

// Files to cache (relative paths)
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json',
  './offline.html',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

// Install event - cache core files
self.addEventListener('install', event => {
  console.log('[ServiceWorker] Install');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('[ServiceWorker] Pre-caching offline page');
        // Cache files relative to the service worker location
        const urlsToCache = PRECACHE_URLS.map(url => new URL(url, self.location.href).href);
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        return self.skipWaiting();
      })
      .catch(err => {
        console.log('[ServiceWorker] Pre-cache failed:', err);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[ServiceWorker] Activate');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  const requestURL = new URL(event.request.url);
  
  // Skip cross-origin requests except for allowed CDNs
  const allowedOrigins = [
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'flagcdn.com',
    'cdnjs.cloudflare.com'
  ];
  
  const isAllowedExternal = allowedOrigins.some(origin => requestURL.hostname.includes(origin));
  
  if (requestURL.origin !== self.location.origin && !isAllowedExternal) {
    return;
  }

  // Don't cache external tool iframes (GitHub Pages tools, Streamlit)
  if (requestURL.hostname.includes('github.io') && requestURL.origin !== self.location.origin) {
    return;
  }
  if (requestURL.hostname.includes('streamlit.app')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }

        const fetchRequest = event.request.clone();

        return fetch(fetchRequest)
          .then(response => {
            // Check if valid response
            if (!response || response.status !== 200) {
              return response;
            }

            // Only cache same-origin GET requests
            if (event.request.method === 'GET' && requestURL.origin === self.location.origin) {
              const responseToCache = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => {
                  cache.put(event.request, responseToCache);
                });
            }

            return response;
          })
          .catch(() => {
            // Network failed, show offline page for navigation requests
            if (event.request.mode === 'navigate') {
              return caches.match(new URL('./offline.html', self.location.href).href);
            }
            return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
          });
      })
  );
});

// Background sync (for future use)
self.addEventListener('sync', event => {
  if (event.tag === 'sync-data') {
    console.log('[ServiceWorker] Background sync triggered');
  }
});

// Push notifications (for future use)
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'New update available',
    icon: './icons/icon-192.png',
    badge: './icons/icon-72.png',
    vibrate: [100, 50, 100]
  };

  event.waitUntil(
    self.registration.showNotification('SNT Tools', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('./')
  );
});

// Message handler for updates
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    caches.delete(CACHE_NAME);
  }
});
