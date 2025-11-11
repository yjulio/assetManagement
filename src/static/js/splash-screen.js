// ========================================
// SPLASH SCREEN CONTROLLER
// ========================================

class SplashScreen {
    constructor(options = {}) {
        this.minDisplayTime = options.minDisplayTime || 2000; // Minimum 2 seconds
        this.fadeOutDuration = options.fadeOutDuration || 500; // 0.5 second fade
        this.startTime = Date.now();
        this.isReady = false;
        this.contentLoaded = false;
        
        this.init();
    }
    
    init() {
        // Prevent scrolling while splash is visible
        document.body.classList.add('preload-hidden');
        
        // Check if this is a fresh page load (not from cache)
        const sessionSplashShown = sessionStorage.getItem('splashShown');
        
        if (sessionSplashShown === 'true') {
            // Skip splash for same session
            this.hideSplash(0);
            return;
        }
        
        // Mark splash as shown for this session
        sessionStorage.setItem('splashShown', 'true');
        
        // Wait for DOM content to load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.contentLoaded = true;
                this.checkAndHide();
            });
        } else {
            this.contentLoaded = true;
            this.checkAndHide();
        }
        
        // Also wait for all resources to load
        window.addEventListener('load', () => {
            this.isReady = true;
            this.checkAndHide();
        });
        
        // Fallback: force hide after max time
        setTimeout(() => {
            this.hideSplash();
        }, 5000); // Maximum 5 seconds
    }
    
    checkAndHide() {
        // Wait for both content loaded and minimum display time
        const elapsedTime = Date.now() - this.startTime;
        
        if (this.contentLoaded && elapsedTime >= this.minDisplayTime) {
            this.hideSplash();
        } else if (this.contentLoaded) {
            // Content loaded but minimum time not met, wait remaining time
            const remainingTime = this.minDisplayTime - elapsedTime;
            setTimeout(() => this.hideSplash(), remainingTime);
        }
    }
    
    hideSplash(delay = 0) {
        setTimeout(() => {
            const splashElement = document.getElementById('splashScreen');
            if (splashElement) {
                // Add fade-out class
                splashElement.classList.add('fade-out');
                
                // Remove splash screen after fade animation
                setTimeout(() => {
                    splashElement.remove();
                    document.body.classList.remove('preload-hidden');
                    
                    // Trigger custom event for when splash is hidden
                    window.dispatchEvent(new CustomEvent('splashHidden'));
                }, this.fadeOutDuration);
            } else {
                document.body.classList.remove('preload-hidden');
            }
        }, delay);
    }
    
    // Method to manually hide splash (if needed)
    forceHide() {
        this.hideSplash();
    }
}

// Initialize splash screen when script loads
let splashScreen;

// Check if we're on a page that should show splash
// Skip splash for certain pages if needed
const skipSplashPages = ['/login', '/logout']; // Add pages to skip
const currentPath = window.location.pathname;
const shouldShowSplash = !skipSplashPages.includes(currentPath);

if (shouldShowSplash) {
    splashScreen = new SplashScreen({
        minDisplayTime: 2000,  // Show for at least 2 seconds
        fadeOutDuration: 500   // Fade out in 0.5 seconds
    });
}

// Export for manual control if needed
window.splashScreen = splashScreen;

// Optional: Skip splash on subsequent navigation in same session
// This is already handled by sessionStorage in the class
