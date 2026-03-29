/**
 * QNet Agent – Frontend JavaScript
 */

/**
 * Trigger "Give me the last content" – fetch from all sources
 */
function fetchLatest() {
    const overlay = document.getElementById('loading-overlay');
    const btn = document.getElementById('btn-fetch-latest');
    const loadingText = document.getElementById('loading-text');

    // Show loading overlay
    overlay.classList.remove('d-none');
    overlay.style.display = 'flex';
    btn.disabled = true;

    // Cycle through status messages
    const messages = [
        'Connecting to arXiv...',
        'Searching Google Scholar...',
        'Querying IEEE Xplore...',
        'Scraping company websites...',
        'Checking university research pages...',
        'Running AI analysis on new content...',
        'Extracting topics and trends...',
        'Generating intelligence briefing...',
        'Almost done...',
    ];
    let msgIndex = 0;
    const msgInterval = setInterval(() => {
        if (msgIndex < messages.length) {
            loadingText.textContent = messages[msgIndex];
            msgIndex++;
        }
    }, 3000);

    // Make the request
    fetch('/api/fetch-latest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
        .then(response => response.json())
        .then(data => {
            clearInterval(msgInterval);
            if (data.success) {
                // Redirect to latest page with results
                window.location.href = '/latest';
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
                overlay.classList.add('d-none');
                btn.disabled = false;
            }
        })
        .catch(error => {
            clearInterval(msgInterval);
            console.error('Fetch error:', error);
            alert('Failed to fetch latest content. Check console for details.');
            overlay.classList.add('d-none');
            btn.disabled = false;
        });
}

/**
 * Auto-dismiss flash alerts after 5 seconds
 */
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});
