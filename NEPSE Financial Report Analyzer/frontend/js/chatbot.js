/* ==========================================
   AI Chatbot (rule-based assistant)
   Provides information about the NEPSE Insight
   platform: product name, features, workflow.
========================================== */

(function () {
    const toggle = document.getElementById("chat-toggle");
    const panel = document.getElementById("chat-panel");
    const closeBtn = document.getElementById("chat-close");
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const body = document.getElementById("chat-body");
    const suggestions = document.getElementById("chat-suggestions");
    const iconOpen = document.querySelector(".chat-icon-open");
    const iconClose = document.querySelector(".chat-icon-close");

    const PRODUCT_NAME = "NEPSE Insight (AI Financial Report Analyzer)";
    const COMPANY = "NEPSE Financial Intelligence";

    /* ---- Knowledge base (keyword -> answer) ---- */
    const KNOWLEDGE = [
        {
            keywords: ["product", "name", "what is this", "about", "tool", "platform", "app"],
            answer:
                "This product is " + PRODUCT_NAME + ", built by " + COMPANY + ". " +
                "It is an AI-powered web platform that lets you upload NEPSE-listed " +
                "company financial reports (PDF) and instantly extracts, visualizes, " +
                "and compares their financial data.",
        },
        {
            keywords: ["feature", "features", "can you do", "capability", "capabilities", "offer"],
            answer:
                "Key features:\n" +
                "• PDF Data Extraction – automatically reads financial statements and metrics.\n" +
                "• Company Comparison – compare multiple companies side by side with charts.\n" +
                "• Quarterly Trends – visualize growth across quarters.\n" +
                "• Lightning Fast – AI-powered extraction in seconds.\n" +
                "• No Login Required – free and instantly accessible.\n" +
                "• Comprehensive Metrics – assets, liabilities, income, profitability ratios, EPS and more.",
        },
        {
            keywords: ["work", "working", "workflow", "process", "how does", "steps", "pipeline"],
            answer:
                "How it works (4 steps):\n" +
                "1. Upload Report – pick a company, report type (quarterly), and upload the PDF.\n" +
                "2. Extract Data – AI extracts tables, statements, and figures using pdfplumber.\n" +
                "3. View Dashboard – explore interactive charts and financial statements.\n" +
                "4. Compare Companies – evaluate multiple companies to make informed decisions.",
        },
        {
            keywords: ["sector", "sectors", "hydropower", "bank", "banking", "company", "companies"],
            answer:
                "Currently the platform supports NEPSE-listed hydropower companies with NFRS PDF " +
                "reports (e.g. UPPER, CHCL, PHCL). Commercial bank analysis is marked 'Coming Soon'.",
        },
        {
            keywords: ["report", "quarterly", "annual", "pdf", "type", "upload"],
            answer:
                "You upload quarterly financial report PDFs from NEPSE-listed hydropower companies. " +
                "Each report is tagged with a fiscal year and quarter (Q1–Q4) and stored in MySQL.",
        },
        {
            keywords: ["tech", "technology", "stack", "built", "backend", "frontend", "database", "ai"],
            answer:
                "The stack uses Python (pdfplumber for extraction, FastAPI backend, MySQL for storage) " +
                "and a static HTML/CSS/JavaScript frontend styled with Tailwind. AI powers the " +
                "data extraction and the analysis view.",
        },
        {
            keywords: ["contact", "support", "help", "price", "free", "cost"],
            answer:
                "The platform is completely free and requires no login. For help, use the Resource " +
                "links in the footer (Documentation, User Guide, FAQ).",
        },
        {
            keywords: ["hi", "hello", "hey", "namaste", "good"],
            answer: "Hello! 👋 How can I help you learn about NEPSE Insight today?",
        },
    ];

    const FALLBACK =
        "I'm here to help you learn about " + PRODUCT_NAME + ". " +
        "Try asking: 'What is this product?', 'What are the key features?', " +
        "or 'How does it work?'";

    function findAnswer(text) {
        const q = text.toLowerCase();
        for (const item of KNOWLEDGE) {
            if (item.keywords.some((k) => q.includes(k))) {
                return item.answer;
            }
        }
        return FALLBACK;
    }

    function appendMessage(text, sender) {
        const msg = document.createElement("div");
        msg.className = "chat-msg " + sender;
        msg.textContent = text;
        body.appendChild(msg);
        body.scrollTop = body.scrollHeight;
    }

    function formatText(text) {
        const wrapper = document.createElement("div");
        text.split("\n").forEach((raw) => {
            const line = raw.trim();
            if (!line) return;
            const block = document.createElement("div");
            if (line.startsWith("•")) {
                block.style.marginLeft = "14px";
                block.textContent = "• " + line.slice(1).trim();
            } else if (/^\d+\./.test(line)) {
                block.style.marginTop = "6px";
                block.textContent = line;
            } else {
                block.textContent = line;
            }
            wrapper.appendChild(block);
        });
        return wrapper;
    }

    function botRespond(userText) {
        const answer = findAnswer(userText);
        const msg = document.createElement("div");
        msg.className = "chat-msg bot";
        msg.appendChild(formatText(answer));
        body.appendChild(msg);
        body.scrollTop = body.scrollHeight;
    }

    function handleUser(text) {
        const trimmed = text.trim();
        if (!trimmed) return;
        appendMessage(trimmed, "user");
        if (suggestions) suggestions.style.display = "none";
        setTimeout(() => botRespond(trimmed), 350);
    }

    function openChat() {
        panel.classList.remove("hidden");
        iconOpen.classList.add("hidden");
        iconClose.classList.remove("hidden");
        if (input) input.focus();
    }

    function closeChat() {
        panel.classList.add("hidden");
        iconOpen.classList.remove("hidden");
        iconClose.classList.add("hidden");
    }

    if (toggle) {
        toggle.addEventListener("click", () => {
            if (panel.classList.contains("hidden")) openChat();
            else closeChat();
        });
    }
    if (closeBtn) closeBtn.addEventListener("click", closeChat);

    if (form) {
        form.addEventListener("submit", (e) => {
            e.preventDefault();
            handleUser(input.value);
            input.value = "";
        });
    }

    if (suggestions) {
        suggestions.querySelectorAll(".chip").forEach((chip) => {
            chip.addEventListener("click", () => {
                const map = {
                    product: "What is this product?",
                    features: "What are the key features?",
                    workflow: "How does it work?",
                };
                handleUser(map[chip.dataset.q] || chip.textContent);
            });
        });
    }
})();
