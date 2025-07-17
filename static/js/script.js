// static/js/script.js

document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;

    // --- Enhanced Role-Based Theming ---
    const userRole = body.getAttribute('data-user-role') || 'anonymous';
    applyRoleTheme(userRole);

    // --- Smooth Page Transitions ---
    initPageTransitions();

    // --- Interactive Elements ---
    initInteractiveElements();

    // --- Form Enhancements ---
    enhanceForms();

    // --- Accessibility Improvements ---
    improveAccessibility();
});

/**
 * Applies role-specific theme and sets up theme-related functionality
 */
function applyRoleTheme(role) {
    const body = document.body;
    const roleLower = role.toLowerCase();

    // Apply role class
    body.classList.add(`role-${roleLower}`);

    // Log theme application (remove in production)
    console.log(`Applied ${roleLower} theme`);

    // Update theme color meta tag for mobile browsers
    updateThemeColor(roleLower);

    // Add subtle animation to role-specific elements
    animateRoleElements(roleLower);
}

/**
 * Updates the theme color meta tag based on role
 */
function updateThemeColor(role) {
    const themeColors = {
        'client': '#AEC6CF',        // Cadet Blue
        'therapist': '#8FBC8F',     // Dark Sea Green
        'admin': '#B0C4DE',         // Light Steel Blue
        'anonymous': '#87CEEB'      // Sky Blue
    };

    let color = themeColors[role] || themeColors['anonymous'];

    // Find or create theme-color meta tag
    let themeColorMeta = document.querySelector('meta[name="theme-color"]');
    if (!themeColorMeta) {
        themeColorMeta = document.createElement('meta');
        themeColorMeta.name = 'theme-color';
        document.head.appendChild(themeColorMeta);
    }
    themeColorMeta.content = color;
}

/**
 * Initializes smooth page transitions
 */
function initPageTransitions() {
    const body = document.body;

    // Initial fade-in (already in your CSS)
    body.classList.add('loaded');

    // Prevent flash of unstyled content (FOUC)
    document.addEventListener('readystatechange', () => {
        if (document.readyState === 'complete') {
            body.classList.add('page-loaded');
        }
    });

    // Smooth transitions for page changes (for SPA-like behavior)
    document.querySelectorAll('a:not([href^="#"]):not([target="_blank"])').forEach(link => {
        link.addEventListener('click', function (e) {
            if (this.href && !this.href.includes('#')) {
                e.preventDefault();
                body.classList.remove('loaded');
                setTimeout(() => {
                    window.location.href = this.href;
                }, 300);
            }
        });
    });
}

/**
 * Enhances interactive elements with subtle animations
 */
function initInteractiveElements() {
    // Navbar dropdown hover effect
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', () => {
            dropdown.classList.add('hovering');
        });
        dropdown.addEventListener('mouseleave', () => {
            dropdown.classList.remove('hovering');
        });
    });

    // Button hover effects
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'translateY(-2px)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
        });
    });

    // Card hover effects
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.boxShadow = '0 8px 16px rgba(0,0,0,0.1)';
            card.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.boxShadow = '';
            card.style.transform = '';
        });
    });
}

/**
 * Enhances form interactions
 */
function enhanceForms() {
    // Add focus styles to form elements
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });
        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
        });
    });

    // Form validation feedback (general, for pages not using specific auth.js validation)
    document.querySelectorAll('form:not(.auth-form)').forEach(form => { // Exclude auth forms
        form.addEventListener('submit', function (e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();

                // Scroll to first invalid field
                const firstInvalid = this.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }
        });
    });
}

/**
 * Improves accessibility features
 */
function improveAccessibility() {
    // Add aria-labels to icons
    document.querySelectorAll('[class*="fa-"]').forEach(icon => {
        if (!icon.getAttribute('aria-label')) {
            const label = icon.className.match(/fa-([a-z-]+)/)?.[1].replace('-', ' ') || 'icon';
            icon.setAttribute('aria-label', label);
        }
    });

    // Focus management for modals (if any)
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
        trigger.addEventListener('click', function () {
            const modalId = this.getAttribute('data-bs-target');
            const modal = document.querySelector(modalId);
            if (modal) {
                setTimeout(() => {
                    const focusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                    if (focusable) focusable.focus();
                }, 100);
            }
        });
    });
}

/**
 * Adds subtle animations to role-specific elements
 */
function animateRoleElements(role) {
    const roleElements = document.querySelectorAll(`[data-role="${role}"]`);

    roleElements.forEach(el => {
        // Add animation class
        el.classList.add('role-highlight');

        // Remove after animation completes
        setTimeout(() => {
            el.classList.remove('role-highlight');
        }, 2000);
    });
}

// Export functions for potential module use (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        applyRoleTheme,
        updateThemeColor,
        initPageTransitions,
        initInteractiveElements,
        enhanceForms,
        improveAccessibility,
        animateRoleElements
    };
}

// Profile picture preview (for profile.html and potentially register.html)
document.addEventListener('DOMContentLoaded', function () {
    const profilePicture = document.getElementById('id_profile_picture'); // Changed to id_profile_picture
    const profilePreview = document.getElementById('profile-preview');

    if (profilePicture && profilePreview) {
        profilePicture.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    profilePreview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});
