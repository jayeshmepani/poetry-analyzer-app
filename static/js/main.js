/**
 * Main JavaScript for Ultimate Literary Master System
 */

// Global custom-select dropdowns (Flowbite/shadcn style, list-based UI)
function closeAllCustomSelects(except = null) {
    document.querySelectorAll('.cs-select[data-open="true"]').forEach((root) => {
        if (except && root === except) return;
        root.dataset.open = 'false';
        const trigger = root.querySelector('.cs-select-trigger');
        if (trigger) trigger.setAttribute('aria-expanded', 'false');
        if (typeof root.__csResetFilter === 'function') {
            root.__csResetFilter();
        }
    });
}

function buildCustomSelect(selectEl) {
    if (!selectEl || selectEl.dataset.csEnhanced === '1') return;
    if (selectEl.multiple) return;
    if (selectEl.hasAttribute('size') && Number(selectEl.getAttribute('size')) > 1) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'cs-select';
    wrapper.dataset.open = 'false';

    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'cs-select-trigger';
    trigger.setAttribute('aria-haspopup', 'listbox');
    trigger.setAttribute('aria-expanded', 'false');
    trigger.innerHTML = `
        <span class="cs-select-value"></span>
        <svg class="cs-select-caret" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path d="M6 8l4 4 4-4"></path>
        </svg>
    `;

    const menu = document.createElement('div');
    menu.className = 'cs-select-menu';
    menu.innerHTML = `<ul class="cs-select-list" role="listbox" tabindex="-1"></ul>`;
    const list = menu.querySelector('.cs-select-list');

    const optionButtons = [];
    const groupLabels = [];
    let activeGroupLabel = null;
    [...selectEl.children].forEach((node) => {
        if (node.tagName === 'OPTGROUP') {
            const groupLabel = document.createElement('li');
            groupLabel.className = 'cs-select-group-label';
            groupLabel.textContent = node.label || '';
            list.appendChild(groupLabel);
            groupLabels.push(groupLabel);
            activeGroupLabel = groupLabel;
            [...node.children].forEach((opt) => {
                if (opt.tagName !== 'OPTION') return;
                const li = document.createElement('li');
                li.setAttribute('role', 'option');
                li.dataset.value = opt.value;
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'cs-select-option';
                btn.textContent = opt.textContent || '';
                if (opt.disabled) btn.disabled = true;
                li.appendChild(btn);
                list.appendChild(li);
                optionButtons.push({ li, btn, opt, groupLabel: activeGroupLabel });
            });
            return;
        }
        if (node.tagName !== 'OPTION') return;
        const li = document.createElement('li');
        li.setAttribute('role', 'option');
        li.dataset.value = node.value;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'cs-select-option';
        btn.textContent = node.textContent || '';
        if (node.disabled) btn.disabled = true;
        li.appendChild(btn);
        list.appendChild(li);
        optionButtons.push({ li, btn, opt: node, groupLabel: null });
    });

    const SEARCH_THRESHOLD = 12;
    const shouldForceSearch = selectEl.dataset.searchable === 'true';
    const shouldEnableSearch = shouldForceSearch || optionButtons.length >= SEARCH_THRESHOLD;
    let searchInput = null;
    let emptyState = null;

    const normalize = (value) => (value || '').toString().toLowerCase().trim();
    const filterOptions = (query) => {
        const needle = normalize(query);
        let visibleCount = 0;
        const visibleByGroup = new Map();

        optionButtons.forEach(({ li, opt, groupLabel }) => {
            const haystack = normalize(opt.textContent);
            const matches = !needle || haystack.includes(needle);
            li.hidden = !matches;
            if (matches) {
                visibleCount += 1;
                if (groupLabel) {
                    visibleByGroup.set(groupLabel, (visibleByGroup.get(groupLabel) || 0) + 1);
                }
            }
        });

        groupLabels.forEach((label) => {
            label.hidden = (visibleByGroup.get(label) || 0) === 0;
        });

        if (emptyState) {
            emptyState.hidden = visibleCount > 0;
        }
    };

    const resetFilter = () => {
        if (!shouldEnableSearch) return;
        if (searchInput) searchInput.value = '';
        filterOptions('');
    };
    wrapper.__csResetFilter = resetFilter;

    if (shouldEnableSearch) {
        const searchWrap = document.createElement('div');
        searchWrap.className = 'cs-select-search-wrap';
        searchWrap.innerHTML = `
            <input
                type="text"
                class="cs-select-search"
                placeholder="Search..."
                autocomplete="off"
                spellcheck="false"
                aria-label="Search options"
            >
        `;
        searchInput = searchWrap.querySelector('.cs-select-search');
        if (searchInput) {
            searchInput.addEventListener('input', () => filterOptions(searchInput.value));
            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    e.preventDefault();
                    wrapper.dataset.open = 'false';
                    trigger.setAttribute('aria-expanded', 'false');
                    resetFilter();
                    trigger.focus();
                }
            });
        }
        menu.prepend(searchWrap);

        emptyState = document.createElement('div');
        emptyState.className = 'cs-select-empty';
        emptyState.textContent = 'No results found';
        emptyState.hidden = true;
        menu.appendChild(emptyState);
    }

    const syncFromSelect = () => {
        const selectedOption = selectEl.options[selectEl.selectedIndex];
        const selectedText = selectedOption ? selectedOption.textContent : '';
        const valueEl = trigger.querySelector('.cs-select-value');
        if (valueEl) valueEl.textContent = selectedText || 'Select...';

        optionButtons.forEach(({ li, btn, opt }) => {
            const isSelected = String(opt.value) === String(selectEl.value);
            li.setAttribute('aria-selected', isSelected ? 'true' : 'false');
            btn.classList.toggle('is-selected', isSelected);
        });

        trigger.disabled = !!selectEl.disabled;
        wrapper.classList.toggle('is-disabled', !!selectEl.disabled);
    };

    const chooseOption = (opt) => {
        if (!opt || opt.disabled) return;
        selectEl.value = opt.value;
        selectEl.dispatchEvent(new Event('input', { bubbles: true }));
        selectEl.dispatchEvent(new Event('change', { bubbles: true }));
        syncFromSelect();
        wrapper.dataset.open = 'false';
        trigger.setAttribute('aria-expanded', 'false');
        resetFilter();
        trigger.focus();
    };

    trigger.addEventListener('click', () => {
        if (selectEl.disabled) return;
        const willOpen = wrapper.dataset.open !== 'true';
        closeAllCustomSelects(wrapper);
        wrapper.dataset.open = willOpen ? 'true' : 'false';
        trigger.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        if (willOpen) {
            resetFilter();
            if (searchInput) {
                searchInput.focus();
            }
        }
    });

    trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            trigger.click();
        } else if (e.key === 'Escape') {
            wrapper.dataset.open = 'false';
            trigger.setAttribute('aria-expanded', 'false');
            resetFilter();
        }
    });

    optionButtons.forEach(({ btn, opt }) => {
        btn.addEventListener('click', () => chooseOption(opt));
    });

    selectEl.addEventListener('change', syncFromSelect);

    selectEl.dataset.csEnhanced = '1';
    selectEl.classList.add('cs-native-select');
    selectEl.insertAdjacentElement('afterend', wrapper);
    wrapper.appendChild(trigger);
    wrapper.appendChild(menu);

    syncFromSelect();
}

function initCustomSelects(root = document) {
    const selects = root.querySelectorAll('select:not([data-native-select])');
    selects.forEach((selectEl) => buildCustomSelect(selectEl));
}

function setupCustomSelectAutoEnhance() {
    if (window.__csObserverInitialized) return;
    window.__csObserverInitialized = true;

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (!(node instanceof Element)) return;
                if (node.matches?.('select:not([data-native-select])')) {
                    buildCustomSelect(node);
                }
                node.querySelectorAll?.('select:not([data-native-select])').forEach((selectEl) => {
                    buildCustomSelect(selectEl);
                });
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });
}

function initMainUi() {
    if (window.__mainUiInitialized) return;
    window.__mainUiInitialized = true;

    initCustomSelects();
    setupCustomSelectAutoEnhance();

    document.addEventListener('click', (e) => {
        const root = e.target.closest('.cs-select');
        if (!root) closeAllCustomSelects();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeAllCustomSelects();
    });

    const strictnessSlider = document.getElementById('strictness');
    const strictnessValue = document.getElementById('strictnessValue');

    if (strictnessSlider && strictnessValue) {
        strictnessSlider.addEventListener('input', function () {
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
}

// Strictness slider value display + global UI init
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMainUi);
} else {
    initMainUi();
}

// Loading overlay functions
function ensureLoadingOverlay() {
    let overlay = document.getElementById('loadingOverlay');
    if (overlay) return overlay;

    overlay = document.createElement('dialog');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay-dialog';
    overlay.setAttribute('aria-live', 'polite');
    overlay.innerHTML = `
        <div class="loading-overlay-panel">
            <svg class="icon fa-spin text-primary text-3xl" aria-hidden="true"><use href="#icon-circle-notch"></use></svg>
            <div id="loadingMessage" class="loading-overlay-message">Loading...</div>
        </div>
    `;

    // Prevent dismissing with Escape key during load
    overlay.addEventListener('cancel', (e) => e.preventDefault());

    document.body.appendChild(overlay);
    return overlay;
}

function showLoading(message = 'Loading...') {
    const overlay = ensureLoadingOverlay();
    const messageEl = overlay.querySelector('#loadingMessage');
    if (messageEl) messageEl.textContent = message;
    if (!overlay.open) {
        overlay.showModal();
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay && overlay.open) {
        overlay.close();
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
