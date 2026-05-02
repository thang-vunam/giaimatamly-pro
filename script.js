/* ================================================
   GIẢI MÃ TÂM LÝ — script.js
   Neural network background + Scroll animations
   ================================================ */

// ========== YEAR ==========
document.getElementById('year').textContent = new Date().getFullYear();

// ========== MOBILE MENU ==========
const menuToggle = document.getElementById('menuToggle');
const navLinks = document.getElementById('navLinks');

if (menuToggle && navLinks) {
  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    menuToggle.textContent = navLinks.classList.contains('open') ? '✕' : '☰';
  });

  // Close menu on link click
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      menuToggle.textContent = '☰';
    });
  });
}

// ========== HEADER SCROLL EFFECT ==========
const header = document.getElementById('header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 50) {
    header.style.background = 'rgba(10, 10, 26, 0.95)';
    header.style.boxShadow = '0 4px 30px rgba(0,0,0,0.3)';
  } else {
    header.style.background = 'rgba(10, 10, 26, 0.85)';
    header.style.boxShadow = 'none';
  }

  lastScroll = currentScroll;
}, { passive: true });

// ========== ACTIVE NAV LINK ==========
const sections = document.querySelectorAll('section[id]');
const navItems = document.querySelectorAll('.nav-links a');

function updateActiveNav() {
  const scrollPos = window.scrollY + 100;

  sections.forEach(section => {
    const top = section.offsetTop;
    const height = section.offsetHeight;
    const id = section.getAttribute('id');

    if (scrollPos >= top && scrollPos < top + height) {
      navItems.forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === '#' + id ||
            (id === 'hero' && item.getAttribute('href') === '/')) {
          item.classList.add('active');
        }
      });
    }
  });
}

window.addEventListener('scroll', updateActiveNav, { passive: true });

// ========== FADE-IN ON SCROLL ==========
const fadeElements = document.querySelectorAll('.fade-in');

const fadeObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      fadeObserver.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.15,
  rootMargin: '0px 0px -40px 0px'
});

fadeElements.forEach(el => fadeObserver.observe(el));

// ========== NEURAL NETWORK BACKGROUND ==========
const canvas = document.getElementById('neuralCanvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];
  let animationId;
  const PARTICLE_COUNT = 80;
  const CONNECTION_DISTANCE = 150;
  const MOUSE_RADIUS = 200;
  let mouse = { x: -1000, y: -1000 };

  function resize() {
    const heroSection = canvas.closest('.hero');
    width = canvas.width = heroSection.offsetWidth;
    height = canvas.height = heroSection.offsetHeight;
  }

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.5;
      this.vy = (Math.random() - 0.5) * 0.5;
      this.radius = Math.random() * 2 + 1;
      // Random between purple and cyan
      this.hue = Math.random() > 0.5 ? 270 : 185;
      this.opacity = Math.random() * 0.5 + 0.3;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      // Mouse interaction
      const dx = mouse.x - this.x;
      const dy = mouse.y - this.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < MOUSE_RADIUS) {
        const force = (MOUSE_RADIUS - dist) / MOUSE_RADIUS;
        this.vx -= dx * force * 0.003;
        this.vy -= dy * force * 0.003;
      }

      // Damping
      this.vx *= 0.999;
      this.vy *= 0.999;

      // Bounds
      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;
      this.x = Math.max(0, Math.min(width, this.x));
      this.y = Math.max(0, Math.min(height, this.y));
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${this.hue}, 80%, 65%, ${this.opacity})`;
      ctx.fill();

      // Glow
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius * 3, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${this.hue}, 80%, 65%, ${this.opacity * 0.1})`;
      ctx.fill();
    }
  }

  function init() {
    resize();
    particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(new Particle());
    }
  }

  function drawConnections() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONNECTION_DISTANCE) {
          const opacity = (1 - dist / CONNECTION_DISTANCE) * 0.15;
          const gradient = ctx.createLinearGradient(
            particles[i].x, particles[i].y,
            particles[j].x, particles[j].y
          );
          gradient.addColorStop(0, `hsla(${particles[i].hue}, 80%, 65%, ${opacity})`);
          gradient.addColorStop(1, `hsla(${particles[j].hue}, 80%, 65%, ${opacity})`);

          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = gradient;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    drawConnections();
    animationId = requestAnimationFrame(animate);
  }

  // Mouse tracking
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });

  canvas.addEventListener('mouseleave', () => {
    mouse.x = -1000;
    mouse.y = -1000;
  });

  window.addEventListener('resize', () => {
    resize();
    // Reposition particles
    particles.forEach(p => {
      if (p.x > width) p.x = width * Math.random();
      if (p.y > height) p.y = height * Math.random();
    });
  });

  // Reduce animation when not visible
  const heroObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        if (!animationId) animate();
      } else {
        if (animationId) {
          cancelAnimationFrame(animationId);
          animationId = null;
        }
      }
    });
  }, { threshold: 0.1 });

  heroObserver.observe(document.getElementById('hero'));

  init();
  animate();
}

// ========== SMOOTH SCROLL FOR ANCHOR LINKS ==========
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const targetId = this.getAttribute('href');
    if (targetId === '#') return;

    const target = document.querySelector(targetId);
    if (target) {
      e.preventDefault();
      const headerH = document.querySelector('.top-bar').offsetHeight;
      const top = target.offsetTop - headerH - 10;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});
