// Dark Mode Toggle
const toggleButton = document.getElementById("dark-mode-toggle");
toggleButton.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  toggleButton.textContent =
    document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
});

// Contact Form Validation
const form = document.getElementById("contact-form");
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const message = document.getElementById("message").value.trim();

  if (!name || !email || !message) {
    alert("Please fill out all fields!");
    return;
  }

  const emailPattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
  if (!email.match(emailPattern)) {
    alert("Please enter a valid email address!");
    return;
  }

  alert("Thank you for reaching out, " + name + "!");
  form.reset();
});

// Navbar Active Link on Scroll
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-links a");

window.addEventListener("scroll", () => {
  let current = "";
  sections.forEach((section) => {
    const sectionTop = section.offsetTop - 60;
    if (scrollY >= sectionTop) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href").includes(current)) {
      link.classList.add("active");
    }
  });
});

// Custom Animated Cursor
(function() {
  const dot = document.createElement('div');
  dot.className = 'cursor-dot';
  const ring = document.createElement('div');
  ring.className = 'cursor-ring';
  document.body.appendChild(dot);
  document.body.appendChild(ring);

  let mouseX = window.innerWidth / 2, mouseY = window.innerHeight / 2;
  let ringX = mouseX, ringY = mouseY;
  const ease = 0.18;

  function onMove(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    document.body.classList.remove('cursor-hidden');
  }

  function onLeave() {
    document.body.classList.add('cursor-hidden');
  }

  function onDown() { document.body.classList.add('cursor-down'); }
  function onUp() { document.body.classList.remove('cursor-down'); }

  function createPulse(e) {
    const pulse = document.createElement('div');
    pulse.className = 'cursor-pulse';
    pulse.style.left = e.clientX + 'px';
    pulse.style.top = e.clientY + 'px';
    document.body.appendChild(pulse);
    pulse.addEventListener('animationend', () => pulse.remove(), { once: true });
  }

  function addHoverListeners() {
    const hoverables = document.querySelectorAll('a, button, input, textarea, .gallery-item');
    hoverables.forEach(el => {
      el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
      el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
    });
  }

  function animate() {
    dot.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;
    ringX += (mouseX - ringX) * ease;
    ringY += (mouseY - ringY) * ease;
    ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0)`;
    requestAnimationFrame(animate);
  }

  window.addEventListener('mousemove', onMove);
  window.addEventListener('mouseleave', onLeave);
  window.addEventListener('mousedown', (e) => { onDown(); createPulse(e); });
  window.addEventListener('mouseup', onUp);

  addHoverListeners();
  requestAnimationFrame(animate);
})();

// Typewriter Effect
(function() {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const h2 = document.querySelector('.hero h2');
  if (!h2 || prefersReduced) return;

  const fullText = h2.textContent.trim();
  h2.textContent = '';
  h2.classList.add('typewriter');

  let i = 0;
  const speed = 40;

  function type() {
    if (i <= fullText.length) {
      h2.textContent = fullText.slice(0, i);
      i++;
      setTimeout(type, speed);
    }
  }

  setTimeout(type, 300);
})();
