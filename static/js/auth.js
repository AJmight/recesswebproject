// static/js/auth.js

document.addEventListener('DOMContentLoaded', function () {
    // Toggle password visibility for login page
    const togglePasswordLogin = document.getElementById('togglePassword');
    if (togglePasswordLogin) {
        togglePasswordLogin.addEventListener('click', function () {
            const passwordInput = document.getElementById('id_password');
            const toggleIcon = this.querySelector('i');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.classList.remove('fa-eye');
                toggleIcon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                toggleIcon.classList.remove('fa-eye-slash');
                toggleIcon.classList.add('fa-eye');
            }
        });
    }

    // Toggle password visibility for register page
    const togglePasswordRegister = document.getElementById('togglePasswordRegister');
    if (togglePasswordRegister) {
        togglePasswordRegister.addEventListener('click', function () {
            const passwordInput = document.getElementById('id_password'); // Assuming same ID for password field
            const toggleIcon = this.querySelector('i');

            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                toggleIcon.classList.remove('fa-eye');
                toggleIcon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                toggleIcon.classList.remove('fa-eye-slash');
                toggleIcon.classList.add('fa-eye');
            }
        });
    }

    // Handle logout button animation
    const logoutForm = document.querySelector('form button[type="submit"]');
    if (logoutForm && logoutForm.closest('.auth-card')) { // Ensure it's the logout form
        logoutForm.addEventListener('click', function (e) {
            const button = this;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Signing out...';
            button.disabled = true;
        });
    }

    // Smooth fade-in animation for auth cards on load
    const authCard = document.querySelector('.auth-card');
    if (authCard) {
        authCard.style.opacity = '0';
        authCard.style.transform = 'translateY(20px)';

        setTimeout(() => {
            authCard.style.transition = 'all 0.6s ease';
            authCard.style.opacity = '1';
            authCard.style.transform = 'translateY(0)';
        }, 100);
    }
});
