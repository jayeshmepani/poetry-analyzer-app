/**
 * theme.js — Dark / light mode toggle with localStorage persistence
 */
(function () {
    const html = document.documentElement;
    const THEME_KEY = 'theme';

    function normalizeTheme(theme) {
        return theme === 'dark' ? 'dark' : 'light';
    }

    function applyTheme(theme, persist = true) {
        const resolved = normalizeTheme(theme);
        html.setAttribute('data-theme', resolved);
        html.style.colorScheme = resolved;
        if (document.body) {
            document.body.setAttribute('data-theme', resolved);
        }
        if (persist) {
            localStorage.setItem(THEME_KEY, resolved);
        }
        document.dispatchEvent(new CustomEvent('theme:changed', { detail: { theme: resolved } }));
    }

    function getInitialTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved === 'dark' || saved === 'light') return saved;
        return normalizeTheme(html.getAttribute('data-theme') || 'light');
    }

    function toggleTheme() {
        const current = normalizeTheme(html.getAttribute('data-theme') || 'light');
        applyTheme(current === 'dark' ? 'light' : 'dark');
    }

    document.addEventListener('DOMContentLoaded', () => {
        applyTheme(getInitialTheme(), false);

        const btn = document.getElementById('themeToggleBtn');
        if (btn) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                toggleTheme();
            });
        }
    });

    // fallback if DOMContentLoaded already fired
    if (document.readyState !== 'loading') {
        applyTheme(getInitialTheme(), false);
    }
})();
