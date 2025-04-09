// Enhanced animations for home page
document.addEventListener('DOMContentLoaded', function() {
  // Add page enter animation class
  document.body.classList.add('page-enter');
  
  // Add floating decoration elements
  addFloatingElements();
  
  // Initialize scroll reveal animations
  initScrollReveal();
  
  // Initialize navbar scroll effect
  initNavbarScroll();
  
  // Add cursor trail effect
  initCursorTrail();
  
  // Add preloader
  initPreloader();
  
  // Add card hover interaction sound
  initHoverSounds();
});

// Add floating decoration elements to hero section
function addFloatingElements() {
  const heroSection = document.querySelector('.hero-section');
  if (!heroSection) return;
  
  // Create shapes
  const shapes = [
    { class: 'floating-element float-1', shape: 'circle', size: '30px', color: 'rgba(244, 114, 182, 0.2)' },
    { class: 'floating-element float-2', shape: 'square', size: '25px', color: 'rgba(99, 102, 241, 0.15)' },
    { class: 'floating-element float-3', shape: 'triangle', size: '35px', color: 'rgba(245, 158, 11, 0.15)' },
    { class: 'floating-element float-4', shape: 'circle', size: '20px', color: 'rgba(156, 163, 175, 0.15)' }
  ];
  
  shapes.forEach(item => {
    const element = document.createElement('div');
    element.className = item.class;
    
    // Set styles based on shape
    element.style.width = item.size;
    element.style.height = item.size;
    element.style.backgroundColor = item.color;
    
    if (item.shape === 'circle') {
      element.style.borderRadius = '50%';
    } else if (item.shape === 'triangle') {
      element.style.width = '0';
      element.style.height = '0';
      element.style.backgroundColor = 'transparent';
      element.style.borderLeft = `${parseInt(item.size)/2}px solid transparent`;
      element.style.borderRight = `${parseInt(item.size)/2}px solid transparent`;
      element.style.borderBottom = `${item.size} solid ${item.color}`;
    }
    
    heroSection.appendChild(element);
  });
}

// Initialize scroll reveal animations
function initScrollReveal() {
  const revealElements = document.querySelectorAll('.feature-card, .statistics-card, .about-section, h2, .cta-section');
  
  revealElements.forEach(el => {
    el.classList.add('reveal');
  });
  
  // Check which elements are in viewport
  function checkReveal() {
    const windowHeight = window.innerHeight;
    const revealOffset = 150;
    
    revealElements.forEach(el => {
      const revealTop = el.getBoundingClientRect().top;
      
      if (revealTop < windowHeight - revealOffset) {
        el.classList.add('active');
      }
    });
  }
  
  // Initial check
  checkReveal();
  
  // Check on scroll
  window.addEventListener('scroll', checkReveal);
}

// Navbar scroll effect
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  
  window.addEventListener('scroll', function() {
    if (window.scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });
}

// Cursor trail effect
function initCursorTrail() {
  const numTrails = 10;
  const trails = [];
  
  // Create trail elements
  for (let i = 0; i < numTrails; i++) {
    const trail = document.createElement('div');
    trail.className = 'cursor-trail';
    document.body.appendChild(trail);
    
    trails.push({
      element: trail,
      x: 0,
      y: 0,
      age: i * 2
    });
  }
  
  // Update trail positions
  window.addEventListener('mousemove', function(e) {
    trails.forEach(trail => {
      // Only update position of older trails
      if (trail.age > 5) {
        trail.x = e.clientX;
        trail.y = e.clientY;
        trail.age = 0;
        
        trail.element.style.opacity = '0.6';
      }
      
      trail.element.style.left = trail.x + 'px';
      trail.element.style.top = trail.y + 'px';
    });
  });
  
  // Animation loop
  function animateTrails() {
    trails.forEach(trail => {
      trail.age += 0.3;
      
      if (trail.age < 10) {
        const scale = Math.max(0, 1 - trail.age / 10);
        const opacity = Math.max(0, 0.5 - trail.age / 10);
        
        trail.element.style.transform = `scale(${scale})`;
        trail.element.style.opacity = opacity;
      } else {
        trail.element.style.opacity = '0';
      }
    });
    
    requestAnimationFrame(animateTrails);
  }
  
  animateTrails();
}

// Page preloader
function initPreloader() {
  const preloader = document.createElement('div');
  preloader.className = 'preloader';
  preloader.innerHTML = '<div class="loader"></div>';
  document.body.appendChild(preloader);
  
  // Hide preloader after page loads
  window.addEventListener('load', function() {
    setTimeout(() => {
      preloader.style.opacity = '0';
      preloader.style.visibility = 'hidden';
      
      // Remove from DOM after transition
      setTimeout(() => {
        preloader.remove();
      }, 800);
    }, 500);
  });
}

// Add subtle hover sounds to interactive elements
function initHoverSounds() {
  // Check if Web Audio API is supported
  if (!window.AudioContext && !window.webkitAudioContext) return;
  
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  const audioCtx = new AudioContext();
  
  const hoverElements = document.querySelectorAll('.btn, .feature-card, .statistics-card');
  
  // Create hover sound
  function createHoverSound(frequency) {
    // Don't play if context is not running (user hasn't interacted yet)
    if (audioCtx.state !== 'running') return;
    
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.type = 'sine';
    oscillator.frequency.value = frequency;
    gainNode.gain.value = 0.05; // Very subtle volume
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    oscillator.start();
    
    // Short duration
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
    setTimeout(() => oscillator.stop(), 200);
  }
  
  // Add hover sound to elements
  hoverElements.forEach((el, index) => {
    // Different frequency for different element types
    let frequency;
    if (el.classList.contains('btn')) {
      frequency = 440 + (index % 3) * 20; // A4 + variation
    } else if (el.classList.contains('feature-card')) {
      frequency = 330 + (index % 4) * 30; // E4 + variation
    } else {
      frequency = 392 + (index % 5) * 15; // G4 + variation
    }
    
    el.addEventListener('mouseenter', () => {
      createHoverSound(frequency);
    });
    
    // Start audio context on first user interaction with the page
    el.addEventListener('click', () => {
      if (audioCtx.state !== 'running') {
        audioCtx.resume();
      }
    }, { once: true });
  });
  
  // Also start audio context on any user interaction
  document.addEventListener('click', () => {
    if (audioCtx.state !== 'running') {
      audioCtx.resume();
    }
  }, { once: true });
}