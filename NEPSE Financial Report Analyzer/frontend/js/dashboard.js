// Toggle Dark/Light Theme
function toggleTheme() {
    const html = document.documentElement;
    html.classList.toggle('dark');
    localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
}

// Toggle Sidebar Navigation (Mobile)
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('hidden');
        sidebar.classList.toggle('flex');
    }
}

// Display Keyboard Shortcuts Alert
function showKeyboardShortcuts() {
    const shortcuts = `
⌨️ KEYBOARD SHORTCUTS
═══════════════════════════════════════
• U         → Go to Upload
• D         → Go to Dashboard
• C         → Go to Comparison
• /         → Search
• T         → Toggle Theme
• ?         → Show This Help

📚 TIPS
═══════════════════════════════════════
✓ Upload PDF reports to auto-extract financial data
✓ Compare multiple companies side-by-side
✓ All data is public and freely accessible
✓ No login required - share with anyone
    `;
    alert(shortcuts);
}

// Event Listeners Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Attach theme toggle buttons
    const themeButtons = document.querySelectorAll('.theme-toggle-btn');
    themeButtons.forEach(btn => btn.addEventListener('click', toggleTheme));

    // Mobile sidebar toggle button
    const sidebarToggleBtn = document.getElementById('sidebar-toggle');
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener('click', toggleSidebar);
    }

    // Keyboard shortcuts button
    const shortcutsBtn = document.getElementById('shortcuts-btn');
    if (shortcutsBtn) {
        shortcutsBtn.addEventListener('click', showKeyboardShortcuts);
    }

    // Feedback button
    const feedbackBtn = document.getElementById('feedback-btn');
    if (feedbackBtn) {
        feedbackBtn.addEventListener('click', () => {
            alert('Visit GitHub or Documentation for support.');
        });
    }

    // Switch company placeholder action
    const switchCompanyBtn = document.getElementById('switch-company-btn');
    if (switchCompanyBtn) {
        switchCompanyBtn.addEventListener('click', () => {
            alert('Company switching feature coming soon!');
        });
    }

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'u' && !e.ctrlKey) window.location.href = 'upload_file.html';
        if (e.key === 'd' && !e.ctrlKey) window.location.href = 'dashboard.html';
        if (e.key === 'c' && !e.ctrlKey) window.location.href = 'comparative_analysis.html';
        if (e.key === 't' && !e.ctrlKey) toggleTheme();
        if (e.key === '?') showKeyboardShortcuts();
    });

    // Load Saved Theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }

    // Mobile Sidebar Responsive Adjustments
    const sidebar = document.getElementById('sidebar');
    if (sidebar && window.innerWidth < 768) {
        sidebar.classList.add('hidden');
    }

    window.addEventListener('resize', () => {
        if (sidebar && window.innerWidth >= 768) {
            sidebar.classList.remove('hidden');
            sidebar.classList.add('flex');
        }
    });

    // Interactive Hover Effect for Bar Charts
    const bars = document.querySelectorAll('.chart-bar');
    bars.forEach(bar => {
        bar.addEventListener('mouseenter', () => bar.classList.add('bg-primary'));
        bar.addEventListener('mouseleave', () => bar.classList.remove('bg-primary'));
    });

    // Smooth Fade-in Animation for Cards
    const cards = document.querySelectorAll('.glass-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(10px)';
        setTimeout(() => {
            card.style.transition = 'all 0.4s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});