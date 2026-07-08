/**
 * App Interactivity & Controls
 */

// Theme Toggle Functionality
function toggleTheme() {
  const html = document.documentElement;
  html.classList.toggle('dark');
  localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
}

// Sidebar Toggle Functionality for Mobile
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('hidden');
  sidebar.classList.toggle('flex');
}

// Display Keyboard Shortcuts
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
  // Theme Toggles
  const btnThemeTop = document.getElementById('btn-toggle-theme-top');
  const btnThemeSidebar = document.getElementById('btn-toggle-theme-sidebar');

  if (btnThemeTop) btnThemeTop.addEventListener('click', toggleTheme);
  if (btnThemeSidebar) btnThemeSidebar.addEventListener('click', toggleTheme);

  // Sidebar Toggle Button
  const btnSidebar = document.getElementById('btn-toggle-sidebar');
  if (btnSidebar) btnSidebar.addEventListener('click', toggleSidebar);

  // Help & Feedback Buttons
  const btnShortcuts = document.getElementById('btn-shortcuts');
  if (btnShortcuts) btnShortcuts.addEventListener('click', showKeyboardShortcuts);

  const btnFeedback = document.getElementById('btn-feedback');
  if (btnFeedback) {
    btnFeedback.addEventListener('click', () => {
      alert('Visit GitHub or Documentation for support.');
    });
  }

  // Load Saved Theme
  const savedTheme = localStorage.getItem('theme') || 'light';
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark');
  }

  // Mobile Sidebar Responsiveness Adjustment
  const sidebar = document.getElementById('sidebar');
  if (window.innerWidth < 768 && sidebar) {
    sidebar.classList.add('hidden');
  }

  window.addEventListener('resize', () => {
    if (window.innerWidth >= 768 && sidebar) {
      sidebar.classList.remove('hidden');
      sidebar.classList.add('flex');
    }
  });

  // Global Keyboard Shortcuts Listener
  document.addEventListener('keydown', (e) => {
    // Avoid triggering shortcuts when focused inside input fields
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
      return;
    }

    if (e.key === 'u' && !e.ctrlKey) window.location.href = 'upload_file.html';
    if (e.key === 'd' && !e.ctrlKey) window.location.href = 'dashboard.html';
    if (e.key === 'c' && !e.ctrlKey) window.location.href = 'comparative_analysis.html';
    if (e.key === 't' && !e.ctrlKey) toggleTheme();
    if (e.key === '?') showKeyboardShortcuts();
  });
});