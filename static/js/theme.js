// Theme Toggle System for Budget Buddy
class ThemeManager {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.createToggleButton();
        this.setupEventListeners();
    }

    createToggleButton() {
        // Create theme toggle button
        const toggle = document.createElement('button');
        toggle.id = 'theme-toggle';
        toggle.className = 'theme-toggle';
        toggle.innerHTML = this.currentTheme === 'dark' ? '☀️' : '🌙';
        toggle.title = `Switch to ${this.currentTheme === 'dark' ? 'light' : 'dark'} mode`;
        
        // Add to navigation
        const nav = document.querySelector('.nav-menu');
        if (nav) {
            const li = document.createElement('li');
            li.appendChild(toggle);
            nav.appendChild(li);
        }
    }

    setupEventListeners() {
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
        this.currentTheme = newTheme;
        localStorage.setItem('theme', newTheme);
        
        // Update toggle button
        const toggle = document.getElementById('theme-toggle');
        if (toggle) {
            toggle.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';
            toggle.title = `Switch to ${newTheme === 'dark' ? 'light' : 'dark'} mode`;
        }
    }

    applyTheme(theme) {
        const root = document.documentElement;
        
        // Set data-theme attribute for CSS selectors
        root.setAttribute('data-theme', theme);
        
        if (theme === 'light') {
            root.style.setProperty('--bg-primary', '#ffffff');
            root.style.setProperty('--bg-secondary', '#f8f9fa');
            root.style.setProperty('--bg-glass', 'rgba(255, 255, 255, 0.1)');
            root.style.setProperty('--text-primary', '#1a1a1a');
            root.style.setProperty('--text-secondary', '#6c757d');
            root.style.setProperty('--border-primary', 'rgba(59, 172, 114, 0.3)');
            root.style.setProperty('--border-secondary', 'rgba(0, 0, 0, 0.1)');
            root.style.setProperty('--shadow', '0 4px 6px rgba(0, 0, 0, 0.1)');
            root.style.setProperty('--shadow-hover', '0 8px 25px rgba(0, 0, 0, 0.15)');
        } else {
            root.style.setProperty('--bg-primary', '#0a0a0a');
            root.style.setProperty('--bg-secondary', '#1a1a1a');
            root.style.setProperty('--bg-glass', 'rgba(26, 26, 26, 0.8)');
            root.style.setProperty('--text-primary', '#ffffff');
            root.style.setProperty('--text-secondary', '#a0a0a0');
            root.style.setProperty('--border-primary', 'rgba(59, 172, 114, 0.5)');
            root.style.setProperty('--border-secondary', 'rgba(255, 255, 255, 0.1)');
            root.style.setProperty('--shadow', '0 4px 6px rgba(0, 0, 0, 0.3)');
            root.style.setProperty('--shadow-hover', '0 8px 25px rgba(0, 0, 0, 0.4)');
        }
        
        // Add transition class for smooth animation
        document.body.classList.add('theme-transition');
        setTimeout(() => {
            document.body.classList.remove('theme-transition');
        }, 300);
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ThemeManager();
}); 