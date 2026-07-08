/* ==========================================
   Theme Toggle
========================================== */
const html = document.documentElement;
const themeButton = document.querySelector("header button");
const themeIcon = themeButton
    ? themeButton.querySelector(".material-symbols-outlined")
    : null;
/**
 * Apply selected theme
 */
function applyTheme(theme) {
    if (theme === "dark") {
        html.classList.add("dark");
        if (themeIcon) {
            themeIcon.textContent = "dark_mode";
        }
    } else {
        html.classList.remove("dark");
        if (themeIcon) {
            themeIcon.textContent = "light_mode";
        }
    }
    localStorage.setItem("theme", theme);
}

/**
 * Toggle Theme
 */
function toggleTheme() {
    const isDark = html.classList.contains("dark");
    applyTheme(isDark ? "light" : "dark");
}

/**
 * Load Saved Theme
 */
document.addEventListener("DOMContentLoaded", () => {
    const savedTheme =
        localStorage.getItem("theme") ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light");
    applyTheme(savedTheme);
});


/* ==========================================
   Navbar Scroll Effect
========================================== */

const header = document.querySelector("header");
window.addEventListener("scroll", () => {
    if (!header) return;
    if (window.scrollY > 20) {
        header.classList.add(
            "shadow-lg",
            "backdrop-blur-md",
            "bg-white/95"
        );

    } else {

        header.classList.remove(
            "shadow-lg",
            "backdrop-blur-md",
            "bg-white/95"
        );

    }

});


/* ==========================================
   Smooth Scroll
========================================== */

document.querySelectorAll('a[href^="#"]').forEach(link => {

    link.addEventListener("click", function (e) {

        const target = document.querySelector(this.getAttribute("href"));

        if (!target) return;
        e.preventDefault();

        target.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    });

});


/* ==========================================
   Scroll Reveal Animation
========================================== */

const revealElements = document.querySelectorAll(
    ".feature-card, .step-card, .sector-card"
);

const observer = new IntersectionObserver(

    (entries) => {

        entries.forEach(entry => {

            if (entry.isIntersecting) {

                entry.target.classList.add("show");

            }

        });

    },

    {
        threshold: 0.15
    }

);

revealElements.forEach(element => {

    element.classList.add("hidden-card");

    observer.observe(element);

});


/* ==========================================
   Console Message
========================================== */

console.log(
    "%cNEPSE Financial Intelligence",
    "color:#051125;font-size:18px;font-weight:bold;"
);
console.log("Landing Page Loaded Successfully.");