// Service Worker for Offline Support
const CACHE_NAME = 'vbos-assets-v1';
const OFFLINE_URL = '/offline';

// Assets to cache on install
const PRECACHE_ASSETS = [
    '/',
    '/offline',
    '/static/css/styles.css',
    '/static/asset.png',
    '/static/js/main.js'
];

// Install event - cache essential assets
self.addEventListener('install', (event) => {
    console.log('[ServiceWorker] Install');

    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Caching app shell');
            return cache.addAll(PRECACHE_ASSETS).catch(err => {
                console.error('[ServiceWorker] Cache failed:', err);
            });
        })
    );

    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[ServiceWorker] Activate');

    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[ServiceWorker] Removing old cache:', cacheName);
                        return cache.delete(cacheName);
                    }
                })
            );
        })
    );

    return self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    // Handle navigation requests
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(OFFLINE_URL);
            })
        );
        return;
    }

    // Handle other requests with cache-first strategy
    event.respondWith(
        caches.match(event.request).then((response) => {
            if (response) {
                // Return cached version
                return response;
            }

            // Fetch from network and cache
            return fetch(event.request).then((response) => {
                // Don't cache non-successful responses
                if (!response || response.status !== 200 || response.type === 'error') {
                    return response;
                }

                // Clone the response
                const responseToCache = response.clone();

                caches.open(CACHE_NAME).then((cache) => {
                    // Cache GET requests only
                    if (event.request.method === 'GET') {
                        cache.put(event.request, responseToCache);
                    }
                });

                return response;
            }).catch(() => {
                // If both cache and network fail, show offline page
                return caches.match(OFFLINE_URL);
            });
        })
    );
});

// Background sync for handovers (when online)
self.addEventListener('sync', (event) => {
    console.log('[ServiceWorker] Background sync:', event.tag);

    if (event.tag === 'sync-handovers') {
        event.waitUntil(syncHandovers());
    }

    if (event.tag === 'sync-photos') {
        event.waitUntil(syncPhotos());
    }
});

// Sync pending handovers
async function syncHandovers() {
    try {
        const db = await openDB();
        const pendingHandovers = await getAllPendingHandovers(db);

        for (const handover of pendingHandovers) {
            try {
                const response = await fetch(handover.url, {
                    method: 'POST',
                    body: handover.data
                });

                if (response.ok) {
                    await deletePendingHandover(db, handover.id);
                    console.log('[ServiceWorker] Handover synced:', handover.id);
                }
            } catch (err) {
                console.error('[ServiceWorker] Failed to sync handover:', err);
            }
        }
    } catch (err) {
        console.error('[ServiceWorker] Sync handovers failed:', err);
    }
}

// Sync pending photos
async function syncPhotos() {
    try {
        const db = await openDB();
        const pendingPhotos = await getAllPendingPhotos(db);

        for (const photo of pendingPhotos) {
            try {
                const response = await fetch(photo.url, {
                    method: 'POST',
                    body: photo.data
                });

                if (response.ok) {
                    await deletePendingPhoto(db, photo.id);
                    console.log('[ServiceWorker] Photo synced:', photo.id);
                }
            } catch (err) {
                console.error('[ServiceWorker] Failed to sync photo:', err);
            }
        }
    } catch (err) {
        console.error('[ServiceWorker] Sync photos failed:', err);
    }
}

// IndexedDB helpers for offline data
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('vbos-offline-db', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            if (!db.objectStoreNames.contains('pendingHandovers')) {
                db.createObjectStore('pendingHandovers', { keyPath: 'id', autoIncrement: true });
            }

            if (!db.objectStoreNames.contains('pendingPhotos')) {
                db.createObjectStore('pendingPhotos', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

function getAllPendingHandovers(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pendingHandovers'], 'readonly');
        const store = transaction.objectStore('pendingHandovers');
        const request = store.getAll();

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function getAllPendingPhotos(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pendingPhotos'], 'readonly');
        const store = transaction.objectStore('pendingPhotos');
        const request = store.getAll();

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
    });
}

function deletePendingHandover(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pendingHandovers'], 'readwrite');
        const store = transaction.objectStore('pendingHandovers');
        const request = store.delete(id);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

function deletePendingPhoto(db, id) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(['pendingPhotos'], 'readwrite');
        const store = transaction.objectStore('pendingPhotos');
        const request = store.delete(id);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve();
    });
}

console.log('[ServiceWorker] Loaded');
