/**
 * Main JavaScript for Ultimate Literary Master System
 */

// Strictness slider value display
document.addEventListener('DOMContentLoaded', function() {
    const strictnessSlider = document.getElementById('strictness');
    const strictnessValue = document.getElementById('strictnessValue');

    if (strictnessSlider && strictnessValue) {
        strictnessSlider.addEventListener('input', function() {
            strictnessValue.textContent = this.value;
        });
    }

    const toggleButtons = document.querySelectorAll('[data-toggle-password]');
    toggleButtons.forEach((btn) => {
        const targetId = btn.getAttribute('data-toggle-password');
        const input = targetId
            ? document.getElementById(targetId)
            : btn.closest('.input-with-toggle')?.querySelector('input');

        if (!input) {
            return;
        }

        const showIcon = btn.querySelector('[data-icon="show"]');
        const hideIcon = btn.querySelector('[data-icon="hide"]');

        const setState = (isVisible) => {
            btn.setAttribute('aria-pressed', String(isVisible));
            btn.setAttribute('aria-label', isVisible ? 'Hide password' : 'Show password');
            if (showIcon && hideIcon) {
                showIcon.classList.toggle('d-none', isVisible);
                hideIcon.classList.toggle('d-none', !isVisible);
            }
        };

        setState(false);

        btn.addEventListener('click', () => {
            const isVisible = input.type === 'text';
            input.type = isVisible ? 'password' : 'text';
            setState(!isVisible);
        });
    });
});

// Loading overlay functions
function ensureLoadingOverlay() {
    let overlay = document.getElementById('loadingOverlay');
    if (overlay) return overlay;

    overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'd-none fixed inset-0 z-100 align-center justify-center p-4 overlay-dark';
    overlay.innerHTML = `
        <div class="card card-sm d-flex flex-col align-center gap-3 shadow-xl">
            <svg class="icon fa-spin text-primary text-3xl" aria-hidden="true"><use href="#icon-circle-notch"></use></svg>
            <div id="loadingMessage" class="text-sm font-medium text-soft">Loading...</div>
        </div>
    `;
    document.body.appendChild(overlay);
    return overlay;
}

function showLoading(message = 'Loading...') {
    const overlay = ensureLoadingOverlay();
    const messageEl = overlay.querySelector('#loadingMessage');
    if (messageEl) messageEl.textContent = message;
    overlay.classList.remove('hidden', 'd-none');
    overlay.classList.add('flex', 'd-flex');
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden', 'd-none');
        overlay.classList.remove('flex', 'd-flex');
    }
}

// Format numbers with proper decimals
function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

// Create rating badge
function createRatingBadge(score) {
    let colorClass = 'bg-red-500';
    if (score >= 8) colorClass = 'bg-green-500';
    else if (score >= 6) colorClass = 'bg-yellow-500';
    else if (score >= 4) colorClass = 'bg-orange-500';
    
    return `
        <span class="${colorClass} text-white px-3 py-1 rounded-full font-bold text-sm">
            ${formatNumber(score)}/10
        </span>
    `;
}

// Toast helpers (global shortcuts)
window.showToast = (message, type = 'info', options = {}) => {
    if (!window.Toast || typeof window.Toast[type] !== 'function') return;
    const normalized = typeof options === 'number' ? { duration: options } : options;
    window.Toast[type](message, normalized);
};
window.showSuccess = (message, options = {}) => window.showToast(message, 'success', options);
window.showError = (message, options = {}) => window.showToast(message, 'error', options);
window.showWarning = (message, options = {}) => window.showToast(message, 'warning', options);
window.showInfo = (message, options = {}) => window.showToast(message, 'info', options);
