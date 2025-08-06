// Advanced Charts for Budget Buddy
class BudgetCharts {
    constructor() {
        this.charts = {};
        this.colors = [
            '#3bac72', '#ff6b6b', '#4ecdc4', '#45b7d1', 
            '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff'
        ];
    }

    // Initialize all charts
    initCharts() {
        this.initCategoryChart();
        this.initDailySpending();
    }

    // Category Spending Pie Chart
    initCategoryChart() {
        const ctx = document.getElementById('categoryChart');
        if (!ctx) return;

        const data = JSON.parse(ctx.dataset.chartData || '{}');
        
        this.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: this.colors,
                    borderWidth: 2,
                    borderColor: '#1a1a1a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#ffffff',
                            font: { size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateRotate: true,
                    animateScale: true
                }
            }
        });
    }



    // Daily Spending Chart
    initDailySpending() {
        const ctx = document.getElementById('dailyChart');
        if (!ctx) return;

        const data = JSON.parse(ctx.dataset.chartData || '{}');
        
        this.charts.daily = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Daily Spending',
                    data: data.values || [],
                    borderColor: '#3bac72',
                    backgroundColor: 'rgba(59, 172, 114, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#3bac72',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#ffffff' }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#ffffff' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    },
                    y: {
                        ticks: { 
                            color: '#ffffff',
                            callback: function(value) {
                                return '$' + value.toFixed(0);
                            }
                        },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }



    // Update chart data
    updateChart(chartName, newData) {
        if (this.charts[chartName]) {
            this.charts[chartName].data = newData;
            this.charts[chartName].update();
        }
    }

    // Animate chart entrance
    animateChart(chartName) {
        if (this.charts[chartName]) {
            this.charts[chartName].update('active');
        }
    }
}

// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing BudgetCharts...');
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded!');
        return;
    }
    
    console.log('Chart.js is loaded, version:', Chart.version);
    
    const budgetCharts = new BudgetCharts();
    budgetCharts.initCharts();
    
    console.log('Charts initialized:', Object.keys(budgetCharts.charts));
    
    // Add entrance animations
    setTimeout(() => {
        Object.keys(budgetCharts.charts).forEach(chartName => {
            budgetCharts.animateChart(chartName);
        });
    }, 500);
}); 