/**
 * sidebar.js — Sidebar collapse, mobile toggle, submenu toggle
 */
(function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const collapseBtn = document.getElementById('desktopCollapseBtn');
    const mobileBtn = document.getElementById('mobileMenuBtn');

    function syncCollapseButtonState() {
        if (!sidebar || !collapseBtn) return;
        const isCollapsed = sidebar.classList.contains('collapsed');
        const label = isCollapsed ? 'Expand sidebar' : 'Collapse sidebar';
        collapseBtn.setAttribute('title', label);
        collapseBtn.setAttribute('aria-label', label);
        collapseBtn.classList.toggle('is-collapsed', isCollapsed);
    }

    // Restore saved state
    if (localStorage.getItem('sidebarCollapsed') === '1') {
        sidebar?.classList.add('collapsed');
    }
    syncCollapseButtonState();

    // Desktop collapse toggle
    collapseBtn?.addEventListener('click', () => {
        sidebar?.classList.toggle('collapsed');
        syncCollapseButtonState();
        localStorage.setItem('sidebarCollapsed', sidebar?.classList.contains('collapsed') ? '1' : '0');
    });

    // Mobile open/close
    function openMobile() {
        sidebar?.classList.add('mobile-open');
        overlay?.classList.add('active');
    }
    function closeMobile() {
        sidebar?.classList.remove('mobile-open');
        overlay?.classList.remove('active');
    }

    mobileBtn?.addEventListener('click', openMobile);
    overlay?.addEventListener('click', closeMobile);

    // Submenu toggles
    document.querySelectorAll('.sidebar-toggle-sub').forEach(trigger => {
        const li = trigger.closest('.sidebar-has-sub');
        // Auto-open if active
        if (li?.classList.contains('active')) li.classList.add('open');

        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            if (sidebar?.classList.contains('collapsed')) {
                document.querySelectorAll('.sidebar-has-sub.open').forEach((openLi) => {
                    if (openLi !== li) openLi.classList.remove('open');
                });
            }
            li?.classList.toggle('open');
        });

        li?.addEventListener('mouseenter', () => {
            if (!sidebar?.classList.contains('collapsed')) return;
            li.classList.add('open');
        });

        li?.addEventListener('mouseleave', () => {
            if (!sidebar?.classList.contains('collapsed')) return;
            li.classList.remove('open');
        });
    });


})();
