// Function to create a doughnut chart for threat scores
function createThreatScoreChart(canvasId, score, maxScore, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    // Calculate percentage
    const percentage = (score / maxScore) * 100;
    
    // Determine color based on score percentage
    let color;
    if (percentage < 20) {
        color = '#198754'; // Green (safe)
    } else if (percentage < 50) {
        color = '#ffc107'; // Yellow (warning)
    } else if (percentage < 80) {
        color = '#fd7e14'; // Orange (suspicious)
    } else {
        color = '#dc3545'; // Red (dangerous)
    }
    
    // Create chart
    new Chart(canvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [score, maxScore - score],
                backgroundColor: [color, '#e9ecef'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            }
        }
    });
    
    // Add text in the center
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = 'bold 24px Arial';
    ctx.fillStyle = color;
    ctx.fillText(score, centerX, centerY);
    
    ctx.font = '12px Arial';
    ctx.fillStyle = '#6c757d';
    ctx.fillText(`of ${maxScore}`, centerX, centerY + 20);
    
    if (label) {
        ctx.font = '14px Arial';
        ctx.fillStyle = '#212529';
        ctx.fillText(label, centerX, centerY - 25);
    }
}

// Function to create a bar chart for malware categories
function createCategoryChart(canvasId, categories) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !categories || categories.length === 0) return;
    
    // Sort categories by count
    categories.sort((a, b) => b.count - a.count);
    
    // Take top 10 categories
    const topCategories = categories.slice(0, 10);
    
    // Create chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: topCategories.map(cat => cat.name),
            datasets: [{
                label: 'Count',
                data: topCategories.map(cat => cat.count),
                backgroundColor: '#0d6efd',
                borderWidth: 0
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Count: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            }
        }
    });
}

// Function to create a timeline chart for report history
function createTimelineChart(canvasId, timeData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !timeData || timeData.length === 0) return;
    
    // Parse dates and sort by time
    const parsedData = timeData.map(item => ({
        date: new Date(item.date),
        count: item.count
    })).sort((a, b) => a.date - b.date);
    
    // Create chart
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: parsedData.map(item => item.date.toLocaleDateString()),
            datasets: [{
                label: 'Reports',
                data: parsedData.map(item => item.count),
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Reports: ${context.raw}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Reports'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}
