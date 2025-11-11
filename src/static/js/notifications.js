// ========================================
// TOAST NOTIFICATION SYSTEM
// ========================================

class ToastNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create container if it doesn't exist
        if (!document.querySelector('.toast-container')) {
            this.container = document.createElement('div');
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.toast-container');
        }
    }

    show(message, type = 'info', duration = 5000, title = null) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        const titles = {
            success: title || 'Success',
            error: title || 'Error',
            warning: title || 'Warning',
            info: title || 'Information'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-title">${titles[type]}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" aria-label="Close">&times;</button>
            ${duration > 0 ? '<div class="toast-progress"></div>' : ''}
        `;

        this.container.appendChild(toast);

        // Close button
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => this.hide(toast));

        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => this.hide(toast), duration);
        }

        // Play sound (optional)
        this.playSound(type);

        return toast;
    }

    hide(toast) {
        toast.classList.add('hiding');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    playSound(type) {
        // Optional: Add subtle sound effects
        // You can implement this with Web Audio API if desired
    }

    success(message, title = null, duration = 5000) {
        return this.show(message, 'success', duration, title);
    }

    error(message, title = null, duration = 7000) {
        return this.show(message, 'error', duration, title);
    }

    warning(message, title = null, duration = 6000) {
        return this.show(message, 'warning', duration, title);
    }

    info(message, title = null, duration = 5000) {
        return this.show(message, 'info', duration, title);
    }
}

// Global instance
const toast = new ToastNotification();

// ========================================
// LOADING OVERLAY
// ========================================

const LoadingOverlay = {
    show(message = 'Loading...') {
        // Remove existing overlay
        this.hide();

        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = `
            <div style="text-align: center; color: white;">
                <div class="loading-spinner large"></div>
                <div style="margin-top: 16px; font-size: 16px;">${message}</div>
            </div>
        `;
        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';
    },

    hide() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
            document.body.style.overflow = '';
        }
    }
};

// ========================================
// CONFIRMATION MODAL
// ========================================

class ConfirmModal {
    show(options = {}) {
        return new Promise((resolve) => {
            const {
                title = 'Confirm Action',
                message = 'Are you sure you want to proceed?',
                type = 'warning', // 'warning' or 'danger'
                confirmText = 'Confirm',
                cancelText = 'Cancel',
                icon = type === 'danger' ? '🗑️' : '⚠️'
            } = options;

            const overlay = document.createElement('div');
            overlay.className = 'modal-overlay';
            overlay.innerHTML = `
                <div class="modal">
                    <div class="modal-header ${type}">
                        <div class="modal-header-icon">${icon}</div>
                        <h3 class="modal-title">${title}</h3>
                    </div>
                    <div class="modal-body">
                        ${message}
                    </div>
                    <div class="modal-footer">
                        <button class="modal-btn modal-btn-cancel" data-action="cancel">
                            ${cancelText}
                        </button>
                        <button class="modal-btn ${type === 'danger' ? 'modal-btn-danger' : 'modal-btn-confirm'}" data-action="confirm">
                            ${confirmText}
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            const handleClick = (e) => {
                const action = e.target.dataset.action;
                if (action) {
                    overlay.remove();
                    resolve(action === 'confirm');
                }
            };

            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    overlay.remove();
                    resolve(false);
                }
            });

            overlay.querySelectorAll('.modal-btn').forEach(btn => {
                btn.addEventListener('click', handleClick);
            });

            // ESC key to cancel
            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    overlay.remove();
                    resolve(false);
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        });
    }

    confirm(message, title = 'Confirm') {
        return this.show({ message, title, type: 'warning' });
    }

    danger(message, title = 'Warning') {
        return this.show({ message, title, type: 'danger' });
    }
}

const confirmModal = new ConfirmModal();

// ========================================
// FORM VALIDATION
// ========================================

class FormValidator {
    constructor(form) {
        this.form = form;
        this.init();
    }

    init() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    this.validateField(input);
                }
            });
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        let isValid = true;
        let message = '';

        // Remove existing feedback
        this.clearFieldFeedback(field);

        if (required && !value) {
            isValid = false;
            message = `${this.getFieldLabel(field)} is required`;
        } else if (value) {
            switch (type) {
                case 'email':
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(value)) {
                        isValid = false;
                        message = 'Please enter a valid email address (e.g., user@example.com)';
                    }
                    break;
                case 'number':
                    if (isNaN(value) || value === '') {
                        isValid = false;
                        message = 'Please enter a valid number (e.g., 10 or 25.5)';
                    }
                    break;
                case 'tel':
                    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
                    if (!phoneRegex.test(value)) {
                        isValid = false;
                        message = 'Please enter a valid phone number';
                    }
                    break;
                case 'url':
                    try {
                        new URL(value);
                    } catch {
                        isValid = false;
                        message = 'Please enter a valid URL (e.g., https://example.com)';
                    }
                    break;
            }

            // Custom validation attributes
            if (field.hasAttribute('minlength')) {
                const minLength = parseInt(field.getAttribute('minlength'));
                if (value.length < minLength) {
                    isValid = false;
                    message = `Must be at least ${minLength} characters long`;
                }
            }

            if (field.hasAttribute('maxlength')) {
                const maxLength = parseInt(field.getAttribute('maxlength'));
                if (value.length > maxLength) {
                    isValid = false;
                    message = `Must be no more than ${maxLength} characters`;
                }
            }

            if (field.hasAttribute('min') && type === 'number') {
                const min = parseFloat(field.getAttribute('min'));
                if (parseFloat(value) < min) {
                    isValid = false;
                    message = `Must be at least ${min}`;
                }
            }

            if (field.hasAttribute('max') && type === 'number') {
                const max = parseFloat(field.getAttribute('max'));
                if (parseFloat(value) > max) {
                    isValid = false;
                    message = `Must be no more than ${max}`;
                }
            }
        }

        this.setFieldFeedback(field, isValid, message);
        return isValid;
    }

    validateForm() {
        const inputs = this.form.querySelectorAll('input, textarea, select');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    getFieldLabel(field) {
        const label = this.form.querySelector(`label[for="${field.id}"]`);
        return label ? label.textContent.replace('*', '').trim() : field.name || 'This field';
    }

    clearFieldFeedback(field) {
        field.classList.remove('is-valid', 'is-invalid');
        const feedback = field.parentElement.querySelector('.form-feedback');
        const icon = field.parentElement.querySelector('.field-icon');
        if (feedback) feedback.remove();
        if (icon) icon.remove();
    }

    setFieldFeedback(field, isValid, message) {
        field.classList.remove('is-valid', 'is-invalid');
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');

        if (!isValid && message) {
            const feedback = document.createElement('div');
            feedback.className = 'form-feedback invalid';
            feedback.innerHTML = `<span>⚠️</span> ${message}`;
            field.parentElement.appendChild(feedback);
        }

        // Add icon
        const icon = document.createElement('span');
        icon.className = `field-icon ${isValid ? 'valid' : 'invalid'}`;
        icon.textContent = isValid ? '✓' : '✕';
        field.parentElement.style.position = 'relative';
        field.parentElement.appendChild(icon);
    }
}

// ========================================
// KEYBOARD SHORTCUTS
// ========================================

class KeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.init();
    }

    init() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        this.registerDefaultShortcuts();
    }

    register(key, callback, description, ctrl = false, shift = false, alt = false) {
        const shortcutKey = this.getShortcutKey(key, ctrl, shift, alt);
        this.shortcuts.set(shortcutKey, { callback, description, key, ctrl, shift, alt });
    }

    getShortcutKey(key, ctrl, shift, alt) {
        return `${ctrl ? 'ctrl+' : ''}${shift ? 'shift+' : ''}${alt ? 'alt+' : ''}${key.toLowerCase()}`;
    }

    handleKeyPress(e) {
        const key = e.key.toLowerCase();
        const ctrl = e.ctrlKey || e.metaKey;
        const shift = e.shiftKey;
        const alt = e.altKey;

        const shortcutKey = this.getShortcutKey(key, ctrl, shift, alt);
        const shortcut = this.shortcuts.get(shortcutKey);

        if (shortcut) {
            // Don't trigger if user is typing in an input
            if (['input', 'textarea', 'select'].includes(e.target.tagName.toLowerCase()) && 
                !['escape', 's'].includes(key)) {
                return;
            }

            e.preventDefault();
            shortcut.callback(e);
        }
    }

    registerDefaultShortcuts() {
        // Save form (Ctrl+S)
        this.register('s', (e) => {
            const form = document.querySelector('form');
            if (form) {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                    toast.info('Form submitted', 'Shortcut Used', 2000);
                }
            }
        }, 'Save/Submit form', true);

        // Close modal/cancel (Escape)
        this.register('escape', () => {
            const modal = document.querySelector('.modal-overlay');
            if (modal) {
                modal.remove();
            }
        }, 'Close modal or cancel action');

        // Show shortcuts menu (?)
        this.register('?', () => {
            this.showShortcutsMenu();
        }, 'Show keyboard shortcuts', false, true);

        // Focus search (Ctrl+K)
        this.register('k', () => {
            const searchInput = document.querySelector('input[type="search"], input[name="search"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }, 'Focus search field', true);
    }

    showShortcutsMenu() {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        
        let shortcutsHTML = '';
        const groups = {
            'General': [],
            'Forms': [],
            'Navigation': []
        };

        this.shortcuts.forEach((shortcut) => {
            const keyDisplay = this.formatKeyDisplay(shortcut);
            const group = shortcut.key === 's' ? 'Forms' : 
                         shortcut.key === 'k' ? 'Navigation' : 'General';
            groups[group].push({ display: keyDisplay, description: shortcut.description });
        });

        Object.entries(groups).forEach(([group, shortcuts]) => {
            if (shortcuts.length > 0) {
                shortcutsHTML += `
                    <div class="shortcuts-section">
                        <div class="shortcuts-section-title">${group}</div>
                        ${shortcuts.map(s => `
                            <div class="shortcut-item">
                                <span class="shortcut-description">${s.description}</span>
                                <div class="shortcut-keys">${s.display}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
        });

        overlay.innerHTML = `
            <div class="shortcuts-menu">
                <div class="shortcuts-header">
                    <span>⌨️ Keyboard Shortcuts</span>
                    <button class="shortcuts-close">&times;</button>
                </div>
                ${shortcutsHTML}
            </div>
        `;

        document.body.appendChild(overlay);

        const closeBtn = overlay.querySelector('.shortcuts-close');
        closeBtn.addEventListener('click', () => overlay.remove());
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });
    }

    formatKeyDisplay(shortcut) {
        let keys = [];
        if (shortcut.ctrl) keys.push('<span class="key">Ctrl</span>');
        if (shortcut.shift) keys.push('<span class="key">Shift</span>');
        if (shortcut.alt) keys.push('<span class="key">Alt</span>');
        keys.push(`<span class="key">${shortcut.key.toUpperCase()}</span>`);
        return keys.join(' + ');
    }
}

const keyboard = new KeyboardShortcuts();

// ========================================
// BUTTON LOADING STATE
// ========================================

function setButtonLoading(button, loading = true) {
    if (loading) {
        button.classList.add('btn-loading');
        button.disabled = true;
        button.dataset.originalText = button.textContent;
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
        }
    }
}

// ========================================
// FORM HELPERS
// ========================================

// Auto-save form data to localStorage
function enableAutoSave(form, key) {
    const inputs = form.querySelectorAll('input, textarea, select');
    
    // Load saved data
    const savedData = localStorage.getItem(key);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            Object.entries(data).forEach(([name, value]) => {
                const input = form.querySelector(`[name="${name}"]`);
                if (input && !input.value) {
                    input.value = value;
                }
            });
        } catch (e) {
            console.error('Error loading saved form data:', e);
        }
    }

    // Save on input
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            const formData = {};
            inputs.forEach(inp => {
                if (inp.name) formData[inp.name] = inp.value;
            });
            localStorage.setItem(key, JSON.stringify(formData));
        });
    });

    // Clear on submit
    form.addEventListener('submit', () => {
        localStorage.removeItem(key);
    });
}

// ========================================
// INITIALIZE ON LOAD
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize form validators
    document.querySelectorAll('form').forEach(form => {
        if (!form.hasAttribute('novalidate')) {
            new FormValidator(form);
        }
    });

    // Add help badge
    if (!document.querySelector('.help-badge')) {
        const helpBadge = document.createElement('div');
        helpBadge.className = 'help-badge';
        helpBadge.innerHTML = '?';
        helpBadge.title = 'Keyboard Shortcuts (Shift + ?)';
        helpBadge.addEventListener('click', () => keyboard.showShortcutsMenu());
        document.body.appendChild(helpBadge);
    }

    // Show flash messages as toasts
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        const category = msg.dataset.category || 'info';
        const message = msg.textContent.trim();
        toast[category](message);
        msg.remove();
    });

    // Enhance delete buttons with confirmation
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', async (e) => {
            e.preventDefault();
            const message = element.dataset.confirm || 'Are you sure you want to delete this item?';
            const confirmed = await confirmModal.danger(message, 'Confirm Deletion');
            if (confirmed) {
                if (element.tagName === 'A') {
                    window.location.href = element.href;
                } else if (element.tagName === 'BUTTON' && element.form) {
                    element.form.submit();
                }
            }
        });
    });

    // Add loading state to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !form.hasAttribute('data-no-loading')) {
                setButtonLoading(submitBtn, true);
            }
        });
    });
});

// Export for global use
window.toast = toast;
window.LoadingOverlay = LoadingOverlay;
window.confirmModal = confirmModal;
window.FormValidator = FormValidator;
window.setButtonLoading = setButtonLoading;
window.enableAutoSave = enableAutoSave;
