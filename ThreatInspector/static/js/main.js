document.addEventListener('DOMContentLoaded', function() {
    // Check API keys on page load
    checkApiKeys();

    // Add event listener for the search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            // Show loading spinner
            const submitBtn = document.getElementById('search-button');
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...';
            submitBtn.disabled = true;
        });
    }

    // Setup tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Setup popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Setup collapsible elements
    var collapsibleEls = document.querySelectorAll('.collapse-toggle');
    collapsibleEls.forEach(function(el) {
        el.addEventListener('click', function() {
            var target = document.getElementById(this.getAttribute('data-bs-target').substring(1));
            if (target) {
                if (target.classList.contains('show')) {
                    this.innerHTML = '<i class="bi bi-chevron-down"></i> Show Details';
                } else {
                    this.innerHTML = '<i class="bi bi-chevron-up"></i> Hide Details';
                }
            }
        });
    });

    // Function to toggle between tabs
    const resultsTabs = document.querySelectorAll('[data-bs-toggle="tab"]');
    if (resultsTabs) {
        resultsTabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', function(event) {
                // Update URL hash to keep tab state on page reload
                const hash = event.target.getAttribute('href');
                if (history.pushState) {
                    history.pushState(null, null, hash);
                } else {
                    location.hash = hash;
                }
                
                // If tab contains a chart, trigger resize to properly render
                const tabContent = document.querySelector(hash);
                if (tabContent) {
                    const charts = tabContent.querySelectorAll('.chart-container');
                    if (charts.length > 0) {
                        window.dispatchEvent(new Event('resize'));
                    }
                }
            });
        });

        // Activate tab based on URL hash
        const hash = window.location.hash;
        if (hash) {
            const activeTab = document.querySelector(`[href="${hash}"]`);
            if (activeTab) {
                const tab = new bootstrap.Tab(activeTab);
                tab.show();
            }
        }
    }
});

function checkApiKeys() {
    fetch('/api/check_api_keys')
        .then(response => response.json())
        .then(data => {
            updateApiStatusIndicators(data);
        })
        .catch(error => {
            console.error('Error checking API keys:', error);
        });
}

function updateApiStatusIndicators(data) {
    for (const [service, status] of Object.entries(data)) {
        const statusElement = document.getElementById(`${service.toLowerCase().replace(/\s+/g, '-')}-status`);
        if (statusElement) {
            if (status.status === 'online') {
                statusElement.innerHTML = '<span class="badge bg-success">Online</span>';
            } else {
                let message = status.message || 'Error';
                statusElement.innerHTML = `<span class="badge bg-danger" data-bs-toggle="tooltip" title="${message}">Offline</span>`;
                
                // Reinitialize tooltips
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            }
        }
    }
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Show toast notification
    const toastEl = document.getElementById('copy-toast');
    if (toastEl) {
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }
}

// Function to show/hide JSON data
function toggleJsonView(buttonId, contentId) {
    const button = document.getElementById(buttonId);
    const content = document.getElementById(contentId);
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        button.innerHTML = '<i class="bi bi-chevron-up"></i> Hide Raw JSON';
    } else {
        content.style.display = 'none';
        button.innerHTML = '<i class="bi bi-chevron-down"></i> Show Raw JSON';
    }
}
