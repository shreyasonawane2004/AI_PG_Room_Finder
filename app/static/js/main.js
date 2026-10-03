// AI-Powered PG & Room Finder - Global JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. User Profile Dropdown
    const userMenu = document.getElementById('user-menu-trigger');
    const dropdown = document.getElementById('user-dropdown');
    if (userMenu && dropdown) {
        userMenu.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('show');
        });
        document.addEventListener('click', () => {
            dropdown.classList.remove('show');
        });
    }

    // 2. Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle-btn');
    const navLinks = document.getElementById('nav-links-menu');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });
    }

    // 3. Auto-dismiss Toast Notifications
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach((t) => {
        setTimeout(() => {
            t.style.opacity = '0';
            t.style.transform = 'translateX(50px)';
            t.style.transition = 'all 0.4s ease';
            setTimeout(() => t.remove(), 400);
        }, 4000);
    });

    // 4. Wishlist Toggle Buttons
    const favButtons = document.querySelectorAll('.card-favorite-btn');
    favButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            const propId = btn.dataset.propertyId;
            if (!propId) return;

            try {
                const res = await fetch('/api/wishlist/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ property_id: propId })
                });

                if (res.status === 401) {
                    window.location.href = '/auth/login?next=' + encodeURIComponent(window.location.pathname);
                    return;
                }

                const data = await res.json();
                if (data.status === 'success') {
                    btn.classList.toggle('saved', data.saved);
                    const icon = btn.querySelector('i');
                    if (icon) {
                        icon.className = data.saved ? 'fas fa-heart' : 'far fa-heart';
                    }
                }
            } catch (err) {
                console.error('Failed to toggle wishlist:', err);
            }
        });
    });
});
