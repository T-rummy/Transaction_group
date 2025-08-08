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
            // Apple-inspired light mode colors
            root.style.setProperty('--bg-primary', '#f5f5f7');
            root.style.setProperty('--bg-secondary', '#ffffff');
            root.style.setProperty('--bg-tertiary', '#f2f2f2');
            root.style.setProperty('--bg-card', '#ffffff');
            root.style.setProperty('--bg-glass', 'rgba(255, 255, 255, 0.8)');
            root.style.setProperty('--text-primary', '#1d1d1f');
            root.style.setProperty('--text-secondary', '#86868b');
            root.style.setProperty('--text-tertiary', '#6e6e73');
            root.style.setProperty('--border-primary', 'rgba(59, 172, 114, 0.2)');
            root.style.setProperty('--border-secondary', '#d2d2d7');
            root.style.setProperty('--shadow', '0 2px 8px rgba(0, 0, 0, 0.08)');
            root.style.setProperty('--shadow-hover', '0 4px 16px rgba(0, 0, 0, 0.12)');
            root.style.setProperty('--shadow-lg', '0 8px 24px rgba(0, 0, 0, 0.12)');
            root.style.setProperty('--shadow-xl', '0 12px 32px rgba(0, 0, 0, 0.16)');
        } else {
            // Original dark mode colors (unchanged)
            root.style.setProperty('--bg-primary', '#1A1A1A');
            root.style.setProperty('--bg-secondary', '#2D2D2D');
            root.style.setProperty('--bg-tertiary', '#3A3A3A');
            root.style.setProperty('--bg-card', '#2A2A2A');
            root.style.setProperty('--bg-glass', 'rgba(42, 42, 42, 0.8)');
            root.style.setProperty('--text-primary', '#FFFFFF');
            root.style.setProperty('--text-secondary', '#E0E0E0');
            root.style.setProperty('--text-tertiary', '#B0B0B0');
            root.style.setProperty('--border-primary', '#404040');
            root.style.setProperty('--border-secondary', '#505050');
            root.style.setProperty('--shadow', '0 4px 6px -1px rgba(0, 0, 0, 0.1)');
            root.style.setProperty('--shadow-hover', '0 8px 25px rgba(0, 0, 0, 0.4)');
            root.style.setProperty('--shadow-lg', '0 10px 15px -3px rgba(0, 0, 0, 0.1)');
            root.style.setProperty('--shadow-xl', '0 20px 25px -5px rgba(0, 0, 0, 0.1)');
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