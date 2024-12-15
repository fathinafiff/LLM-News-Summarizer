// Add this to your existing script.js
document.addEventListener('DOMContentLoaded', function () {
  // Existing form submission handler
  document.getElementById('summarizer-form').addEventListener('submit', function () {
    document.querySelector('.spinner-border').classList.add('show');
  });

  // Collapse icon rotation
  document.querySelectorAll('[data-toggle="collapse"]').forEach(button => {
    button.addEventListener('click', function () {
      const icon = this.querySelector('.collapse-icon');
      if (this.classList.contains('collapsed')) {
        icon.style.transform = 'rotate(-90deg)';
      } else {
        icon.style.transform = 'rotate(0deg)';
      }
    });
  });
});