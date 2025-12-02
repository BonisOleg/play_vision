/**
 * About Page Functionality
 * Про нас - Smooth scrolling для якорних посилань
 */

document.addEventListener('DOMContentLoaded', function () {

    // Smooth scrolling для якорних посилань
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
