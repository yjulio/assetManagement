/**
 * Bootstrap Enhancements & Modern UI Interactions
 * Enhanced user experience for Asset Management System
 */

(function () {
    'use strict';

    // ============================================
    // TOOLTIP INITIALIZATION
    // ============================================
    function initTooltips() {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
            return new bootstrap.Tooltip(tooltipTriggerEl, {
                boundary: 'window',
                animation: true
            });
        });
    }

    // ============================================
    // POPOVER INITIALIZATION
    // ============================================
    function initPopovers() {
        const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
        const popoverList = [...popoverTriggerList].map(popoverTriggerEl => {
            return new bootstrap.Popover(popoverTriggerEl, {
                trigger: 'hover focus',
                animation: true,
                html: true
            });
        });
    }

    // ============================================
    // TOAST NOTIFICATIONS
    // ============================================
    function showToast(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const toastId = 'toast-' + Date.now();
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info',
            'primary': 'bg-primary'
        }[type] || 'bg-info';

        const toastHTML = `
      <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="d-flex">
          <div class="toast-body">
            <i class="bi bi-${getToastIcon(type)} me-2"></i>
            ${message}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    `;

        const container = document.getElementById('toast-container');
        container.insertAdjacentHTML('beforeend', toastHTML);

        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();

        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    function getToastIcon(type) {
        const icons = {
            'success': 'check-circle-fill',
            'error': 'exclamation-triangle-fill',
            'warning': 'exclamation-circle-fill',
            'info': 'info-circle-fill',
            'primary': 'star-fill'
        };
        return icons[type] || 'info-circle-fill';
    }

    // Expose toast function globally
    window.showToast = showToast;

    // ============================================
    // SMOOTH SCROLL
    // ============================================
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const targetId = this.getAttribute('href');
                if (targetId !== '#' && targetId.length > 1) {
                    const target = document.querySelector(targetId);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }

    // ============================================
    // FORM VALIDATION ENHANCEMENT
    // ============================================
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');

        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();

                    // Show error toast
                    showToast('Please fill in all required fields correctly.', 'error');

                    // Focus first invalid field
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                }

                form.classList.add('was-validated');
            }, false);
        });
    }

    // ============================================
    // CARD ANIMATIONS
    // ============================================
    function initCardAnimations() {
        const cards = document.querySelectorAll('.card:not(.no-animation)');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-slideInUp');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        cards.forEach(card => {
            observer.observe(card);
        });
    }

    // ============================================
    // COPY TO CLIPBOARD
    // ============================================
    function initCopyButtons() {
        document.querySelectorAll('[data-copy-text]').forEach(button => {
            button.addEventListener('click', function () {
                const textToCopy = this.getAttribute('data-copy-text');
                navigator.clipboard.writeText(textToCopy).then(() => {
                    showToast('Copied to clipboard!', 'success', 2000);

                    // Visual feedback
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="bi bi-check2"></i> Copied!';
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                }).catch(err => {
                    showToast('Failed to copy text', 'error');
                });
            });
        });
    }

    // ============================================
    // LOADING BUTTON STATE
    // ============================================
    function initLoadingButtons() {
        document.querySelectorAll('[data-loading-text]').forEach(button => {
            button.addEventListener('click', function () {
                const loadingText = this.getAttribute('data-loading-text');
                const originalText = this.innerHTML;

                this.disabled = true;
                this.innerHTML = `
          <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          ${loadingText}
        `;

                // Store original text for later restoration
                this.setAttribute('data-original-text', originalText);
            });
        });
    }

    // Function to restore button state
    window.resetLoadingButton = function (button) {
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    };

    // ============================================
    // CONFIRM DIALOGS
    // ============================================
    function initConfirmDialogs() {
        document.querySelectorAll('[data-confirm]').forEach(element => {
            element.addEventListener('click', function (e) {
                const message = this.getAttribute('data-confirm');
                if (!confirm(message)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            });
        });
    }

    // ============================================
    // AUTO-DISMISS ALERTS
    // ============================================
    function initAutoDismissAlerts() {
        document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
            const delay = parseInt(alert.getAttribute('data-auto-dismiss')) || 5000;

            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, delay);
        });
    }

    // ============================================
    // TABLE ENHANCEMENTS
    // ============================================
    function initTableEnhancements() {
        // Add row hover highlight
        document.querySelectorAll('.table tbody tr').forEach(row => {
            row.addEventListener('mouseenter', function () {
                this.style.backgroundColor = 'rgba(102, 126, 234, 0.05)';
            });

            row.addEventListener('mouseleave', function () {
                this.style.backgroundColor = '';
            });
        });

        // Make rows clickable if they have data-href
        document.querySelectorAll('tr[data-href]').forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function () {
                window.location.href = this.getAttribute('data-href');
            });
        });
    }

    // ============================================
    // SEARCH INPUT ENHANCEMENT
    // ============================================
    function initSearchInputs() {
        document.querySelectorAll('input[type="search"], .search-input').forEach(input => {
            const clearBtn = document.createElement('button');
            clearBtn.type = 'button';
            clearBtn.className = 'btn btn-sm btn-link position-absolute end-0 top-50 translate-middle-y';
            clearBtn.innerHTML = '<i class="bi bi-x-circle"></i>';
            clearBtn.style.display = 'none';
            clearBtn.style.right = '10px';

            input.parentElement.style.position = 'relative';
            input.parentElement.appendChild(clearBtn);

            input.addEventListener('input', function () {
                clearBtn.style.display = this.value ? 'block' : 'none';
            });

            clearBtn.addEventListener('click', function () {
                input.value = '';
                input.dispatchEvent(new Event('input'));
                clearBtn.style.display = 'none';
                input.focus();
            });
        });
    }

    // ============================================
    // NUMBER INPUT INCREMENT/DECREMENT
    // ============================================
    function initNumberInputs() {
        document.querySelectorAll('input[type="number"].enhanced-number').forEach(input => {
            const wrapper = document.createElement('div');
            wrapper.className = 'input-group';

            const decrementBtn = document.createElement('button');
            decrementBtn.className = 'btn btn-outline-secondary';
            decrementBtn.type = 'button';
            decrementBtn.innerHTML = '<i class="bi bi-dash"></i>';

            const incrementBtn = document.createElement('button');
            incrementBtn.className = 'btn btn-outline-secondary';
            incrementBtn.type = 'button';
            incrementBtn.innerHTML = '<i class="bi bi-plus"></i>';

            input.parentNode.insertBefore(wrapper, input);
            wrapper.appendChild(decrementBtn);
            wrapper.appendChild(input);
            wrapper.appendChild(incrementBtn);

            decrementBtn.addEventListener('click', () => {
                const step = parseFloat(input.step) || 1;
                const min = parseFloat(input.min);
                const currentValue = parseFloat(input.value) || 0;
                const newValue = currentValue - step;
                if (isNaN(min) || newValue >= min) {
                    input.value = newValue;
                    input.dispatchEvent(new Event('change'));
                }
            });

            incrementBtn.addEventListener('click', () => {
                const step = parseFloat(input.step) || 1;
                const max = parseFloat(input.max);
                const currentValue = parseFloat(input.value) || 0;
                const newValue = currentValue + step;
                if (isNaN(max) || newValue <= max) {
                    input.value = newValue;
                    input.dispatchEvent(new Event('change'));
                }
            });
        });
    }

    // ============================================
    // PROGRESS BAR ANIMATION
    // ============================================
    function animateProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar[data-animate="true"]');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const progressBar = entry.target;
                    const targetWidth = progressBar.getAttribute('aria-valuenow');
                    progressBar.style.width = '0%';

                    setTimeout(() => {
                        progressBar.style.width = targetWidth + '%';
                    }, 100);

                    observer.unobserve(progressBar);
                }
            });
        }, { threshold: 0.5 });

        progressBars.forEach(bar => observer.observe(bar));
    }

    // ============================================
    // BADGE COUNTER ANIMATION
    // ============================================
    function animateCounters() {
        document.querySelectorAll('[data-count-up]').forEach(element => {
            const target = parseInt(element.getAttribute('data-count-up'));
            const duration = parseInt(element.getAttribute('data-duration')) || 2000;
            const start = 0;
            const increment = target / (duration / 16);
            let current = start;

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const timer = setInterval(() => {
                            current += increment;
                            if (current >= target) {
                                current = target;
                                clearInterval(timer);
                            }
                            element.textContent = Math.floor(current);
                        }, 16);

                        observer.unobserve(element);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(element);
        });
    }

    // ============================================
    // INITIALIZE ALL FEATURES
    // ============================================
    function init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        console.log('🚀 Initializing Bootstrap Enhancements...');

        // Initialize all features
        initTooltips();
        initPopovers();
        initSmoothScroll();
        initFormValidation();
        initCardAnimations();
        initCopyButtons();
        initLoadingButtons();
        initConfirmDialogs();
        initAutoDismissAlerts();
        initTableEnhancements();
        initSearchInputs();
        initNumberInputs();
        animateProgressBars();
        animateCounters();

        console.log('✅ Bootstrap Enhancements initialized successfully!');
    }

    // Start initialization
    init();

})();
