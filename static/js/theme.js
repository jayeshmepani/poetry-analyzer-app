/**
 * theme.js — Dark / light mode toggle with localStorage persistence
 */
(function () {
    const btn = document.getElementById('themeToggleBtn');
    const html = document.documentElement;

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }

    btn?.addEventListener('click', () => {
        const current = html.getAttribute('data-theme') || 'light';
        applyTheme(current === 'dark' ? 'light' : 'dark');
    });
})();
