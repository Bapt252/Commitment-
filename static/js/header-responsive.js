// Header responsiveness and enhanced interactions
document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle functionality
  const menuToggle = document.querySelector('.menu-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', function() {
      navLinks.classList.toggle('show');
    });
  }
  
  // Set active nav link based on current page
  const currentPage = window.location.pathname;
  const navLinksItems = document.querySelectorAll('.nav-link');
  
  navLinksItems.forEach(link => {
    if (link.getAttribute('href') && currentPage.includes(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });
  
  // Add smooth scroll behavior
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId !== '#') {
        e.preventDefault();
        document.querySelector(targetId).scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });
  
  // Check for dark mode preference changes
  const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  darkModeMediaQuery.addEventListener('change', function() {
    // Update UI elements that need special handling in dark mode
    document.body.classList.toggle('dark-mode', darkModeMediaQuery.matches);
  });
  
  // Initial dark mode setup
  document.body.classList.toggle('dark-mode', darkModeMediaQuery.matches);
  
  // Add responsive design detection for UI adjustments
  function handleResponsiveChanges() {
    const isMobile = window.innerWidth < 768;
    
    // Adjust header for mobile
    const header = document.querySelector('.app-header');
    if (header) {
      if (isMobile) {
        header.classList.add('mobile-view');
      } else {
        header.classList.remove('mobile-view');
      }
    }
  }
  
  // Run on load
  handleResponsiveChanges();
  
  // Re-run on window resize
  window.addEventListener('resize', handleResponsiveChanges);
});