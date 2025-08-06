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
        this.initSpendingTimeline();
        this.initMonthlyComparison();
        this.initBudgetProgress();
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

    // Spending Timeline Chart
    initSpendingTimeline() {
        const ctx = document.getElementById('timelineChart');
        if (!ctx) {
            console.log('Timeline chart canvas not found');
            return;
        }

        const data = JSON.parse(ctx.dataset.chartData || '{}');
        console.log('Timeline chart data:', data);
        console.log('Timeline labels:', data.labels);
        console.log('Timeline values:', data.values);
        
        if (!data.labels || data.labels.length === 0) {
            console.log('No timeline data available');
            return;
        }
        
        this.charts.timeline = new Chart(ctx, {
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

    // Monthly Comparison Chart
    initMonthlyComparison() {
        const ctx = document.getElementById('monthlyChart');
        if (!ctx) return;

        const data = JSON.parse(ctx.dataset.chartData || '{}');
        
        this.charts.monthly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Monthly Spending',
                    data: data.values || [],
                    backgroundColor: this.colors[0],
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    borderRadius: 8,
                    borderSkipped: false
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
                }
            }
        });
    }

    // Budget Progress Chart
    initBudgetProgress() {
        const ctx = document.getElementById('budgetChart');
        if (!ctx) {
            console.log('Budget chart canvas not found');
            return;
        }

        const data = JSON.parse(ctx.dataset.chartData || '{}');
        console.log('Budget chart data:', data);
        console.log('Budget labels:', data.labels);
        console.log('Budget values:', data.values);
        
        if (!data.labels || data.labels.length === 0) {
            console.log('No budget data available');
            return;
        }
        
        this.charts.budget = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: data.colors || this.colors,
                    borderWidth: 0,
                    cutout: '70%'
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
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${percentage}%`;
                            }
                        }
                    }
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