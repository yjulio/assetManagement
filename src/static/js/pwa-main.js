// Main JavaScript for PWA registration and offline support

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then((registration) => {
                console.log('ServiceWorker registered:', registration.scope);

                // Check for updates periodically
                setInterval(() => {
                    registration.update();
                }, 60000); // Check every minute
            })
            .catch((error) => {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

// Handle online/offline status
window.addEventListener('online', () => {
    console.log('Back online');
    document.body.classList.remove('offline');

    // Show notification
    showNotification('You are back online!', 'success');

    // Trigger background sync if supported
    if ('serviceWorker' in navigator && 'sync' in registration) {
        navigator.serviceWorker.ready.then((registration) => {
            registration.sync.register('sync-handovers');
            registration.sync.register('sync-photos');
        });
    }
});

window.addEventListener('offline', () => {
    console.log('Gone offline');
    document.body.classList.add('offline');

    // Show notification
    showNotification('You are offline. Changes will be synced when online.', 'warning');
});

// Show notification helper
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;

    document.body.appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Install prompt for PWA
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;

    // Show install button if it exists
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn) {
        installBtn.style.display = 'block';

        installBtn.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log(`User response to install prompt: ${outcome}`);
                deferredPrompt = null;
                installBtn.style.display = 'none';
            }
        });
    }
});

// Network status indicator
function updateNetworkStatus() {
    const statusIndicator = document.getElementById('network-status');
    if (statusIndicator) {
        if (navigator.onLine) {
            statusIndicator.innerHTML = '<i class="bi bi-wifi"></i> Online';
            statusIndicator.className = 'badge bg-success';
        } else {
            statusIndicator.innerHTML = '<i class="bi bi-wifi-off"></i> Offline';
            statusIndicator.className = 'badge bg-danger';
        }
    }
}

// Update status on load and when status changes
document.addEventListener('DOMContentLoaded', updateNetworkStatus);
window.addEventListener('online', updateNetworkStatus);
window.addEventListener('offline', updateNetworkStatus);
