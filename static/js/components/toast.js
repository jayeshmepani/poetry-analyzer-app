/**
 * CustomToast - A lightweight toast notification component.
 * Usage:
 *   Toast.success('Record saved!')
 *   Toast.error('Something went wrong', { duration: 6000 })
 *   Toast.info('Loading data...')
 *   Toast.warning('Please fill required fields')
 */
class CustomToast {
    constructor() {
        this._container = null;
        this._init();
    }

    _init() {
        if (document.querySelector('.toast-container')) return;
        this._container = document.createElement('div');
        this._container.className = 'toast-container';
        this._container.id = 'toast-container';
        document.body.appendChild(this._container);
    }

    _show(message, type = 'info', options = {}) {
        const { duration = 4000, title } = options;
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
            warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
        };

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || icons.info}</span>
            <div class="toast-body">
                ${title ? `<div class="toast-title">${title}</div>` : ''}
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
            <div class="toast-progress"></div>
        `;

        this._container.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => toast.classList.add('toast-show'));

        // Progress bar + auto-dismiss
        const progress = toast.querySelector('.toast-progress');
        progress.style.setProperty('--toast-duration', `${duration}ms`);
        progress.classList.add('toast-progress-run');

        const timer = setTimeout(() => this._dismiss(toast), duration);
        toast.addEventListener('mouseenter', () => {
            clearTimeout(timer);
            progress.style.animationPlayState = 'paused';
        });
        toast.addEventListener('mouseleave', () => {
            progress.style.animationPlayState = 'running';
            setTimeout(() => this._dismiss(toast), duration * 0.2);
        });
    }

    _dismiss(toast) {
        toast.classList.remove('toast-show');
        toast.addEventListener('transitionend', () => toast.remove(), { once: true });
    }

    success(message, options = {}) { this._show(message, 'success', options); }
    error(message, options = {}) { this._show(message, 'error', options); }
    warning(message, options = {}) { this._show(message, 'warning', options); }
    info(message, options = {}) { this._show(message, 'info', options); }
}

// Singleton
window.Toast = new CustomToast();
