/**
 * sidebar.js — Sidebar collapse, mobile toggle, submenu toggle
 */
(function () {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    const collapseBtn = document.getElementById('desktopCollapseBtn');
    const mobileBtn = document.getElementById('mobileMenuBtn');

    // Restore saved state
    if (localStorage.getItem('sidebarCollapsed') === '1') {
        sidebar?.classList.add('collapsed');
    }

    // Desktop collapse toggle
    collapseBtn?.addEventListener('click', () => {
        sidebar?.classList.toggle('collapsed');
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
            li?.classList.toggle('open');
        });
    });

    // User dropdown in header
    const userTrigger = document.getElementById('userDropdownTrigger');
    userTrigger?.addEventListener('click', (e) => {
        e.stopPropagation();
        userTrigger.classList.toggle('open');
    });
    document.addEventListener('click', () => {
        userTrigger?.classList.remove('open');
    });
})();
