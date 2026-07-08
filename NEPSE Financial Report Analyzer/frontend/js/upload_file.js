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
    // Attach event listeners to Theme Toggle buttons
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

    // Global Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'u' && !e.ctrlKey) window.location.href = 'upload_file.html';
        if (e.key === 'd' && !e.ctrlKey) window.location.href = 'dashboard.html';
        if (e.key === 'c' && !e.ctrlKey) window.location.href = 'comparative_analysis.html';
        if (e.key === 't' && !e.ctrlKey) toggleTheme();
        if (e.key === '?') showKeyboardShortcuts();
    });

    // Load saved theme state
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }

    // Mobile-responsive sidebar management
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

    // Micro-interactions for Drag and Drop Zone
    const dropzone = document.getElementById('dropzone');
    const duplicateChecker = document.getElementById('duplicate-checker');

    if (dropzone) {
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('bg-secondary-container/20', 'border-secondary');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('bg-secondary-container/20', 'border-secondary');
        });

        dropzone.addEventListener('click', () => {
            alert('Opening file selector...');
            // Simulated duplicate file detection trigger
            if (duplicateChecker) {
                setTimeout(() => {
                    duplicateChecker.classList.remove('hidden');
                    duplicateChecker.classList.add('animate-pulse');
                    setTimeout(() => duplicateChecker.classList.remove('animate-pulse'), 1000);
                }, 500);
            }
        });
    }

    // Select input handling
    const selects = document.querySelectorAll('select');
    selects.forEach(select => {
        select.addEventListener('change', () => {
            if (select.value !== 'Select Company...') {
                // Potential duplicate checking logic hook
            }
        });
    });
});