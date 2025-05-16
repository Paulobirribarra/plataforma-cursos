document.addEventListener("DOMContentLoaded", function () {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.2
  });

  document.querySelectorAll(".animate-left, .animate-right").forEach(el => {
    observer.observe(el);
  });

  const counters = document.querySelectorAll('.counter');
  let started = false;

  const animateCounters = () => {
    counters.forEach(counter => {
      counter.innerText = '0';
      const target = +counter.getAttribute('data-target');
      const updateCounter = () => {
        const current = +counter.innerText;
        const increment = target / 100;
        if (current < target) {
          counter.innerText = Math.ceil(current + increment);
          setTimeout(updateCounter, 15);
        } else {
          counter.innerText = target;
        }
      };
      updateCounter();
    });
  };

  window.addEventListener('scroll', () => {
    const section = document.querySelector('.counter-section');
    if (section && !started && window.scrollY + window.innerHeight > section.offsetTop) {
      animateCounters();
      started = true;
    }
  });
});
