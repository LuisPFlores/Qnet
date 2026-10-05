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

function runResearchDiscovery(event) {
    event.preventDefault();

    const area = document.getElementById('research-area').value;
    const query = document.getElementById('discovery-query').value.trim();
    const button = document.getElementById('btn-run-discovery');
    const overlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');

    button.disabled = true;
    loadingText.textContent = 'Searching live research and organization sources...';
    overlay.classList.remove('d-none');
    overlay.style.display = 'flex';

    fetch('/api/research-discovery', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ research_area: area, search_query: query }),
    })
        .then(async response => {
            const data = await response.json();
            if (!response.ok || !data.success) {
                throw new Error(data.error || 'Research discovery failed');
            }
            const params = new URLSearchParams({ area });
            if (query) {
                params.set('search', query);
            }
            window.location.href = `/research-discovery?${params.toString()}`;
        })
        .catch(error => {
            console.error('Research discovery error:', error);
            alert(error.message);
            overlay.classList.add('d-none');
            button.disabled = false;
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
