// Mobile menu functionality
document.addEventListener('DOMContentLoaded', () => {
    const menuButton = document.getElementById('menuButton');
    const closeMenu = document.getElementById('closeMenu');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileMenuLinks = document.querySelectorAll('#mobileMenu nav a');
    let isMenuOpen = false;

    const toggleMenu = (shouldOpen = null) => {
        isMenuOpen = shouldOpen !== null ? shouldOpen : !isMenuOpen;
        mobileMenu.style.transform = isMenuOpen ? 'translateX(0)' : 'translateX(100%)';
        document.body.style.overflow = isMenuOpen ? 'hidden' : '';
    };

    const closeMenuAndScroll = (target) => {
        toggleMenu(false);
        setTimeout(() => {
            const element = document.querySelector(target);
            if (element) {
                const headerOffset = 80;
                const elementPosition = element.offsetTop;
                const offsetPosition = elementPosition - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        }, 300); // Wait for menu close animation
    };

    menuButton.addEventListener('click', () => toggleMenu(true));
    closeMenu.addEventListener('click', () => toggleMenu(false));

    // Handle mobile menu link clicks
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('href');
            closeMenuAndScroll(target);
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (isMenuOpen && !mobileMenu.contains(e.target) && !menuButton.contains(e.target)) {
            toggleMenu(false);
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isMenuOpen) {
            toggleMenu(false);
        }
    });

    // Section tracking for navigation
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('nav a[href^="#"]');

    const updateActiveLink = () => {
        let found = false;
        const scrollPosition = window.scrollY + 100; // Offset for fixed header

        // Remove active state from all links first
        navLinks.forEach(link => {
            link.classList.remove('text-accent');
            link.classList.add('text-text/80');
            const span = link.querySelector('span');
            if (span) {
                span.classList.remove('text-accent');
                span.classList.add('text-text/80');
            }
        });

        // Find current section
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');

            // Check if we're in the section
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                found = true;
                
                // Add active state to current section link
                navLinks.forEach(link => {
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.remove('text-text/80');
                        link.classList.add('text-accent');
                        const span = link.querySelector('span');
                        if (span) {
                            span.classList.remove('text-text/80');
                            span.classList.add('text-accent');
                        }
                    }
                });
            }
        });

        // Handle top of page
        if (!found && window.scrollY < 100) {
            const homeLink = document.querySelector('nav a[href="#"]');
            if (homeLink) {
                homeLink.classList.remove('text-text/80');
                homeLink.classList.add('text-accent');
                const span = homeLink.querySelector('span');
                if (span) {
                    span.classList.remove('text-text/80');
                    span.classList.add('text-accent');
                }
            }
        }
    };

    // Throttle scroll event for better performance
    let ticking = false;
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                updateActiveLink();
                ticking = false;
            });
            ticking = true;
        }
    });

    // Update active link on page load
    updateActiveLink();

    // Smooth scroll with offset for fixed header
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.offsetTop;
                const offsetPosition = elementPosition - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add animation classes to elements
    document.querySelectorAll('section').forEach(section => {
        section.classList.add('animate-on-scroll');
        observer.observe(section);
    });
});

// Intersection Observer for scroll animations
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
        }
    });
}, observerOptions);
