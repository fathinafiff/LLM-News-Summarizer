document.addEventListener('DOMContentLoaded', function() {
  // Add event listener to form
  document.getElementById('summarizer-form').addEventListener('submit', function() {
    document.querySelector('.spinner-border').classList.add('show');
  });

  // Add event listener to clear button
  document.getElementById('clear-button').addEventListener('click', function() {
    // Clear input field
    document.getElementById('query').value = '';

    // Hide summary heading and clear summary content
    const summaryHeading = document.querySelector('h2.mt-5');
    const summaryParagraph = document.querySelector('.summary');
    if (summaryHeading) {
      summaryHeading.style.display = 'none';
    }
    if (summaryParagraph) {
      summaryParagraph.textContent = '';
    }

    // Hide sources heading and clear source list
    const sourcesHeading = document.querySelector('h3.mt-5');
    const sourceList = document.querySelector('.source-list');
    if (sourcesHeading) {
      sourcesHeading.style.display = 'none';
    }
    if (sourceList) {
      sourceList.innerHTML = '';
    }

    // Optionally, reset the form
    document.getElementById('summarizer-form').reset();

    // Hide spinner if needed
    document.querySelector('.spinner-border').classList.remove('show');
  });
});
