document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector('.whatsapp-fijo');
  if (btn) {
    btn.addEventListener('mouseover', function () {
      this.style.transform = 'scale(1.1)';
    });
    btn.addEventListener('mouseout', function () {
      this.style.transform = 'scale(1)';
    });
  }
});
