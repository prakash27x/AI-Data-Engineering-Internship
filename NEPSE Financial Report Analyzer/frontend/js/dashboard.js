// =====================================
// CONFIG
// =====================================

const API = "http://127.0.0.1:8000/dashboard";
const AI_API = "http://127.0.0.1:8000/ai";

let currentCompany = "BUNGAL";
let currentPeriod = null;
let currentDashboardData = null;
let companies = [];

let revenueChart = null;
let profitChart = null;
let dashboardRequestController = null;
let aiSummaryRequestController = null;
let activeDashboardRequestId = 0;


// =====================================
// UTILITIES
// =====================================

function formatCurrency(value) {

    if (value == null) return "-";

    return "NPR " + Number(value).toLocaleString();

}

function setGrowth(elementId, growth) {

    const element = document.getElementById(elementId);

    if (!growth || growth.direction === "none") {
        element.innerText = "-";
        return;
    }

    // Special cases
    if (growth.status) {

        if (growth.value === null) {

            element.innerText = growth.status;

        } else {

            element.innerText =
                `${growth.direction === "up" ? "▲" : "▼"} ${growth.value}% (${growth.status})`;

        }

    } else {

        element.innerText =
            `${growth.direction === "up" ? "▲" : "▼"} ${growth.value}%`;

    }

    element.className =
        growth.direction === "up"
            ? "text-green-600 font-bold"
            : "text-red-600 font-bold";
}

function setDashboardLoading(isLoading) {
    const loadingTargets = [
        "dashboard-metrics-card",
        "revenue-trend-card",
        "profit-trend-card"
    ];

    loadingTargets.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.classList.toggle("dashboard-loading", isLoading);
        }
    });

    const quarterSelect = document.getElementById("quarter-select");
    const switchCompanyBtn = document.getElementById("switch-company-btn");

    if (quarterSelect) quarterSelect.disabled = isLoading;
    if (switchCompanyBtn) switchCompanyBtn.disabled = isLoading;
}

function setAISummaryLoading(isLoading) {
    const overlay = document.getElementById("ai-loading-overlay");
    const contentWrapper = document.getElementById("ai-content-wrapper");

    if (overlay) {
        overlay.classList.toggle("hidden", !isLoading);
        overlay.classList.toggle("flex", isLoading);
    }

    if (contentWrapper) {
        contentWrapper.classList.toggle("opacity-40", isLoading);
    }
}

function setAIInsightsMessage(message) {
    const insightsListEl = document.getElementById("ai-insights-list");
    if (insightsListEl) {
        insightsListEl.innerHTML = `<li>${message}</li>`;
    }
}

async function loadDashboardSummary(symbol, period, requestId) {
    if (aiSummaryRequestController) {
        aiSummaryRequestController.abort();
    }

    aiSummaryRequestController = new AbortController();
    setAISummaryLoading(true);
    setAIInsightsMessage("Generating summary...");

    try {
        const response = await fetch(`${AI_API}/dashboard-summary`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                company_symbol: symbol,
                fiscal_year: period?.fiscal_year || null,
                quarter: period?.quarter || null
            }),
            signal: aiSummaryRequestController.signal
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Unable to generate AI summary.");
        }

        if (requestId !== activeDashboardRequestId) return;

        updateAIInsights(result.insights);
    } catch (err) {
        if (err.name === "AbortError") return;
        console.error(err);

        if (requestId === activeDashboardRequestId) {
            setAIInsightsMessage("AI summary is taking longer than expected. Please try again.");
        }
    } finally {
        if (requestId === activeDashboardRequestId) {
            setAISummaryLoading(false);
        }
    }
}


// =====================================
// LOAD DASHBOARD
// =====================================

async function loadDashboard(symbol = currentCompany, period = null) {
    const requestId = ++activeDashboardRequestId;

    if (dashboardRequestController) {
        dashboardRequestController.abort();
    }

    dashboardRequestController = new AbortController();
    setDashboardLoading(true);
    setAISummaryLoading(true);

    try {

        let url = `${API}/${symbol}`;

        if (period && period.fiscal_year && period.quarter) {
            url += `?fiscal_year=${encodeURIComponent(period.fiscal_year)}`
                 + `&quarter=${encodeURIComponent(period.quarter)}`;
        }

        const response =
            await fetch(url, {
                signal: dashboardRequestController.signal
            });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Unable to load dashboard data.");
        }

        if (requestId !== activeDashboardRequestId) return;
        
        currentDashboardData = data;

        currentCompany = symbol;
        currentPeriod = data.current_period || null;

        document.getElementById("company-name").innerText =
            data.company.name;

        document.getElementById("company-info").innerText =
            `${data.company.symbol} | ${data.company.sector} | FY ${data.company.fiscal_year} ${data.company.quarter}`;

        document.getElementById("company-avatar").innerText =
            data.company.symbol.charAt(0);

        document.getElementById("revenue").innerText =
            formatCurrency(data.metrics.revenue);

        document.getElementById("net-profit").innerText =
            formatCurrency(data.metrics.net_profit);

        document.getElementById("assets").innerText =
            formatCurrency(data.metrics.assets);

        document.getElementById("equity").innerText =
            formatCurrency(data.metrics.equity);

        // Additional metrics
        document.getElementById("gross-profit").innerText =
            formatCurrency(data.metrics.gross_profit);

        document.getElementById("profit-before-tax").innerText =
            formatCurrency(data.metrics.profit_before_tax);

        document.getElementById("finance-costs").innerText =
            formatCurrency(data.metrics.finance_costs);

        document.getElementById("total-current-assets").innerText =
            formatCurrency(data.metrics.total_current_assets);

        document.getElementById("cash-and-cash-equivalents").innerText =
            formatCurrency(data.metrics.cash_and_cash_equivalents);

        document.getElementById("total-current-liabilities").innerText =
            formatCurrency(data.metrics.total_current_liabilities);

        document.getElementById("total-liabilities").innerText =
            formatCurrency(data.metrics.total_liabilities);

        document.getElementById("share-capital").innerText =
            formatCurrency(data.metrics.share_capital);

        document.getElementById("reserves-and-surplus").innerText =
            formatCurrency(data.metrics.reserves_and_surplus);

        setGrowth(
            "revenue-growth",
            data.metrics.revenue_growth
        );

        setGrowth(
            "profit-growth",
            data.metrics.profit_growth
        );

        setGrowth(
            "asset-growth",
            data.metrics.asset_growth
        );

        setGrowth(
            "equity-growth",
            data.metrics.equity_growth
        );

        // Additional growth metrics
        setGrowth(
            "gross-profit-growth",
            data.metrics.gross_profit_growth
        );

        setGrowth(
            "profit-before-tax-growth",
            data.metrics.profit_before_tax_growth
        );

        setGrowth(
            "finance-costs-growth",
            data.metrics.finance_costs_growth
        );

        setGrowth(
            "total-current-assets-growth",
            data.metrics.total_current_assets_growth
        );

        setGrowth(
            "cash-and-cash-equivalents-growth",
            data.metrics.cash_and_cash_equivalents_growth
        );

        setGrowth(
            "total-current-liabilities-growth",
            data.metrics.total_current_liabilities_growth
        );

        setGrowth(
            "total-liabilities-growth",
            data.metrics.total_liabilities_growth
        );

        setGrowth(
            "share-capital-growth",
            data.metrics.share_capital_growth
        );

        setGrowth(
            "reserves-and-surplus-growth",
            data.metrics.reserves_and_surplus_growth
        );

        drawRevenueChart(data.revenue_trend);

        drawProfitChart(data.net_profit_trend);

        populateTrendInsights(data.revenue_trend_insights, 'revenue');
        populateTrendInsights(data.net_profit_trend_insights, 'profit');

        // Update AI Report Period
        const periodEl = document.getElementById("ai-report-period");
        if(periodEl) {
            periodEl.innerText = `FY${data.company.fiscal_year} ${data.company.quarter} Report`;
        }

        // Populate company quarter selector
        populateQuarterSelect(data.available_periods, data.current_period);
        loadDashboardSummary(symbol, data.current_period, requestId);

    } catch (err) {
        if (err.name === "AbortError") {
            return;
        }

        console.error(err);
        setAIInsightsMessage("Unable to load AI summary right now.");
        setAISummaryLoading(false);
    } finally {
        if (requestId === activeDashboardRequestId) {
            setDashboardLoading(false);
        }
    }
}


// =====================================
// POPULATE TREND INSIGHTS
// =====================================
function populateTrendInsights(insights, prefix) {
    if (!insights) return;

    // Populate badge
    const badgeEl = document.getElementById(`${prefix}-trend-badge`);
    if (badgeEl) {
        badgeEl.textContent = insights.badge;
        // Add styling based on badge
        badgeEl.classList.remove('bg-green-100', 'text-green-800', 'bg-red-100', 'text-red-800', 'bg-yellow-100', 'text-yellow-800');
        if (insights.badge === 'Up') {
            badgeEl.classList.add('bg-green-100', 'text-green-800');
        } else if (insights.badge === 'Down') {
            badgeEl.classList.add('bg-red-100', 'text-red-800');
        } else {
            badgeEl.classList.add('bg-yellow-100', 'text-yellow-800');
        }
    }

    // Populate text
    const textEl = document.getElementById(`${prefix}-trend-text`);
    if (textEl) {
        textEl.textContent = insights.text;
    }

    // Populate stats
    const latestEl = document.getElementById(`${prefix}-trend-latest`);
    if (latestEl && insights.latest !== '-') {
        latestEl.textContent = formatCurrency(insights.latest);
    }

    const qoqEl = document.getElementById(`${prefix}-trend-qoq`);
    if (qoqEl) {
        if (insights.qoq !== '-' && insights.qoq !== null) {
            const sign = insights.qoq >= 0 ? '+' : '';
            qoqEl.textContent = `${sign}${insights.qoq.toFixed(2)}%`;
            qoqEl.classList.remove('text-green-600', 'text-red-600');
            qoqEl.classList.add(insights.qoq >= 0 ? 'text-green-600' : 'text-red-600');
        } else {
            qoqEl.textContent = '-';
        }
    }

    const bestEl = document.getElementById(`${prefix}-trend-best`);
    if (bestEl && insights.best !== '-') {
        bestEl.textContent = formatCurrency(insights.best);
    }
}

// =====================================
// REVENUE CHART
// =====================================

function drawRevenueChart(data) {

    if (revenueChart)
        revenueChart.destroy();

    revenueChart = new Chart(
        document.getElementById("revenueChart"),
        {

            type: "bar",

            data: {

                labels: data.map(x => x.quarter),

                datasets: [{

                    data: data.map(x => x.value),

                    backgroundColor: "#4f46e5",
                    hoverBackgroundColor: "#4338ca",

                    borderRadius: 8,
                    borderSkipped: false,

                }]

            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {

                    legend: {

                        display: false

                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.raw);
                            }
                        }
                    }

                }

            }

        }

    );

}


// =====================================
// PROFIT CHART
// =====================================

function drawProfitChart(data) {

    if (profitChart)
        profitChart.destroy();

    profitChart = new Chart(

        document.getElementById("profitChart"),

        {

            type: "line",

            data: {

                labels: data.map(x => x.quarter),

                datasets: [{

                    data: data.map(x => x.value),

                    fill: true,
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderColor: '#10b981',
                    tension: .4,
                    pointBackgroundColor: '#10b981',
                    pointRadius: 4,
                    pointHoverRadius: 6,

                }]

            },

            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        grid: {
                            color: 'rgba(0,0,0,0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {

                    legend: {

                        display: false

                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.raw);
                            }
                        }
                    }

                }

            }

        }

    );

}


// =====================================
// QUARTER SELECT
// =====================================

function populateQuarterSelect(periods, current) {

    const select = document.getElementById("quarter-select");

    if (!select || !periods) return;

    select.innerHTML = "";

    const latest = document.createElement("option");
    latest.value = "";
    latest.textContent = "Latest Quarter";
    select.appendChild(latest);

    periods.forEach(p => {

        const opt = document.createElement("option");
        opt.value = `${p.fiscal_year}|${p.quarter}`;
        opt.textContent = `FY ${p.fiscal_year} · ${p.quarter}`;

        if (current
            && p.fiscal_year === current.fiscal_year
            && p.quarter === current.quarter) {
            opt.selected = true;
        }

        select.appendChild(opt);

    });

}


// =====================================
// COMPANY LIST
// =====================================

async function loadCompanies() {

    const response =
        await fetch(`${API}/companies`);

    companies = await response.json();

    renderCompanies(companies);

}


function renderCompanies(list) {

    const companyList =
        document.getElementById("company-list");

    companyList.innerHTML = "";

    list.forEach(company => {

        companyList.innerHTML += `

        <div
            class="company-item p-3 border rounded cursor-pointer hover:bg-gray-100"
            data-symbol="${company.company_symbol}">

            <div class="font-bold">

                ${company.company_symbol}

            </div>

            <div class="text-sm text-gray-500">

                ${company.company_name}

            </div>

        </div>

        `;

    });

}


// =====================================
// MODAL
// =====================================

function openCompanyModal() {

    document
        .getElementById("company-modal")
        .classList
        .replace("hidden", "flex");

}


function closeCompanyModal() {

    document
        .getElementById("company-modal")
        .classList
        .replace("flex", "hidden");

}


// =====================================
// SEARCH IN MODAL
// =====================================

function searchCompanies() {

    const keyword =
        document
            .getElementById("company-search")
            .value
            .toLowerCase();

    const filtered = companies.filter(c =>

        c.company_symbol
            .toLowerCase()
            .includes(keyword)

        ||

        c.company_name
            .toLowerCase()
            .includes(keyword)

    );

    renderCompanies(filtered);

}


// =====================================
// TOP SEARCH BAR
// =====================================

function topSearch() {

    const symbol =
        document
            .getElementById("top-company-search")
            .value
            .trim()
            .toUpperCase();

    if (!symbol) return;

    loadDashboard(symbol);

}


// =====================================
// EVENTS
// =====================================

document.addEventListener("DOMContentLoaded", () => {

    const params = new URLSearchParams(window.location.search);
    const symbolFromUrl = params.get("symbol");
    if (symbolFromUrl) {
        currentCompany = symbolFromUrl.trim().toUpperCase();
    }

    loadCompanies();

    loadDashboard(currentCompany);

    document
        .getElementById("switch-company-btn")
        .addEventListener("click", openCompanyModal);

    document
        .getElementById("quarter-select")
        .addEventListener("change", e => {

            const value = e.target.value;

            if (!value) {
                loadDashboard(currentCompany, null);
                return;
            }

            const [fy, q] = value.split("|");
            loadDashboard(currentCompany, { fiscal_year: fy, quarter: q });

        });

    document
        .getElementById("close-company-modal")
        .addEventListener("click", closeCompanyModal);

    document
        .getElementById("company-search")
        .addEventListener("input", searchCompanies);

    document
        .getElementById("top-search-btn")
        .addEventListener("click", topSearch);

    document
        .getElementById("top-company-search")
        .addEventListener("keypress", e => {

            if (e.key === "Enter")
                topSearch();

        });

    document
        .getElementById("company-list")
        .addEventListener("click", e => {

            const item =
                e.target.closest(".company-item");

            if (!item) return;

            closeCompanyModal();

            loadDashboard(item.dataset.symbol);

        });

    const sidebar = document.getElementById("sidebar");
    const mainContent = document.getElementById("main-content");
    const footerContent = document.getElementById("footer-content");

    document.getElementById("sidebar-toggle")?.addEventListener("click", () => {
        if (window.innerWidth < 768) {
            sidebar?.classList.toggle("-translate-x-full");
        } else {
            sidebar?.classList.toggle("md:translate-x-0");
            sidebar?.classList.toggle("md:-translate-x-full");
            mainContent?.classList.toggle("md:ml-[260px]");
            mainContent?.classList.toggle("md:ml-0");
            footerContent?.classList.toggle("md:ml-[260px]");
            footerContent?.classList.toggle("md:ml-0");
        }
    });

    document.getElementById("sidebar-close")?.addEventListener("click", () => {
        sidebar?.classList.add("-translate-x-full");
    });
    
    initChat();

});

// =====================================
// AI INSIGHTS
// =====================================

function updateAIInsights(insights) {
    if (!insights) return;

    // Update Score
    const scoreEl = document.getElementById("ai-score");
    if (scoreEl) {
        scoreEl.textContent = insights.score || 0;
    }

    // Update Score Label
    const scoreLabelEl = document.getElementById("ai-score-label");
    if (scoreLabelEl) {
        let label = "Poor";
        let color = "text-red-600";
        if (insights.score >= 80) {
            label = "Excellent";
            color = "text-green-600";
        } else if (insights.score >= 60) {
            label = "Good";
            color = "text-yellow-600";
        } else if (insights.score >= 40) {
            label = "Fair";
            color = "text-orange-600";
        }
        scoreLabelEl.textContent = label;
        scoreLabelEl.className = `text-[10px] uppercase font-bold ${color}`;
    }

    // Update Rating
    const ratingNumEl = document.getElementById("ai-rating-num");
    if (ratingNumEl && insights.score !== undefined) {
        const rating = Math.round((insights.score / 20) * 10) / 10;
        ratingNumEl.textContent = rating;
        let stars = "★".repeat(Math.floor(rating)) + "☆".repeat(5 - Math.floor(rating));
        document.getElementById("ai-rating").textContent = stars;
    }

    // Update All Scores
    const scoreKeys = ['growth_score', 'profitability_score', 'liquidity_score', 'stability_score', 'risk_score'];
    const barIds = ['ai-growth-bar', 'ai-profitability-bar', 'ai-liquidity-bar', 'ai-stability-bar', 'ai-risk-bar'];
    const scoreIds = ['ai-growth-score', 'ai-profitability-score', 'ai-liquidity-score', 'ai-stability-score', 'ai-risk-score'];
    const colors = ['bg-green-500', 'bg-yellow-500', 'bg-blue-500', 'bg-blue-400', 'bg-red-500'];

    scoreKeys.forEach((key, index) => {
        if (insights[key] !== undefined) {
            const barEl = document.getElementById(barIds[index]);
            const scoreEl = document.getElementById(scoreIds[index]);
            if (barEl) {
                colors.forEach(c => barEl.classList.remove(c));
                barEl.classList.add(colors[index]);
                barEl.style.width = `${insights[key]}%`;
            }
            if (scoreEl) {
                scoreEl.textContent = insights[key];
            }
        }
    });

    // Update AI Insights List (combined summary + risks)
    const insightsListEl = document.getElementById("ai-insights-list");
    if (insightsListEl) {
        let allInsights = [];
        if (insights.summary && Array.isArray(insights.summary)) {
            allInsights = allInsights.concat(insights.summary);
        }
        if (insights.risks && Array.isArray(insights.risks)) {
            allInsights = allInsights.concat(insights.risks.map(risk => `⚠️ ${risk}`));
        }
        insightsListEl.innerHTML = allInsights.map(item => `<li>${item}</li>`).join('');
    }
}

function convertMarkdownToHtml(text) {
    if (!text) return "";
    // Convert **bold**
    let html = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    // Convert *italic*
    html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
    // Convert - or * at start of line to list items
    let lines = html.split(/\r?\n/);
    let inList = false;
    let result = [];
    for (let line of lines) {
        if (line.trim().startsWith("* ") || line.trim().startsWith("- ")) {
            if (!inList) {
                result.push("<ul class=\"list-disc pl-5 my-2\">");
                inList = true;
            }
            // Remove the list marker
            let listItem = line.trim().replace(/^[\*\-]\s*/, "");
            result.push(`<li class="my-1">${listItem}</li>`);
        } else {
            if (inList) {
                result.push("</ul>");
                inList = false;
            }
            if (line.trim()) {
                result.push(`<p class="my-1">${line}</p>`);
            } else {
                result.push("<br>");
            }
        }
    }
    if (inList) {
        result.push("</ul>");
    }
    return result.join("");
}

function addChatMessage(text, isUser = false) {
    const chatMessages = document.getElementById("chat-messages");
    if (!chatMessages) return;
    
    const messageDiv = document.createElement("div");
    messageDiv.className = `flex ${isUser ? "justify-end" : "justify-start"}`;
    
    const avatarDiv = document.createElement("div");
    if (!isUser) {
        avatarDiv.className = "w-8 h-8 rounded-full bg-primary-fixed text-primary flex items-center justify-center mr-2 flex-shrink-0";
        avatarDiv.innerHTML = '<span class="material-symbols-outlined text-sm">robot_2</span>';
    }

    const bubble = document.createElement("div");
    if (isUser) {
        bubble.className = "bg-primary text-on-primary px-4 py-2 rounded-2xl rounded-br-sm max-w-[80%] text-sm shadow-sm";
    } else {
        bubble.className = "bg-surface-container-low border border-outline-variant px-4 py-2 rounded-2xl rounded-bl-sm max-w-[80%] text-sm shadow-sm text-on-surface-variant";
    }
    
    // Render Markdown for AI messages, plain text for user messages
    if (isUser) {
        bubble.textContent = text;
    } else {
        bubble.innerHTML = convertMarkdownToHtml(text);
    }

    if (!isUser) {
        messageDiv.appendChild(avatarDiv);
    }
    messageDiv.appendChild(bubble);
    if (isUser) {
        const userAvatar = document.createElement("div");
        userAvatar.className = "w-8 h-8 rounded-full bg-secondary-fixed text-secondary flex items-center justify-center ml-2 flex-shrink-0";
        userAvatar.innerHTML = '<span class="material-symbols-outlined text-sm">person</span>';
        messageDiv.appendChild(userAvatar);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll the chat messages container to the bottom
    const chatMessagesContainer = document.getElementById("chat-messages-container");
    if (chatMessagesContainer) {
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
}

function toggleChatWindow() {
    const chatWindow = document.getElementById("chat-window");
    const floatingChatBtn = document.getElementById("floating-chat-btn");
    
    if (!chatWindow || !floatingChatBtn) return;
    
    const isHidden = chatWindow.classList.contains("hidden");
    
    if (isHidden) {
        chatWindow.classList.remove("hidden");
        floatingChatBtn.classList.add("is-open");
    } else {
        chatWindow.classList.add("hidden");
        floatingChatBtn.classList.remove("is-open");
    }
}

function closeChatWindow() {
    const chatWindow = document.getElementById("chat-window");
    const floatingChatBtn = document.getElementById("floating-chat-btn");
    
    if (!chatWindow || !floatingChatBtn) return;
    
    chatWindow.classList.add("hidden");
    floatingChatBtn.classList.remove("is-open");
}

async function sendMessage(question) {
    if (!question.trim() || !currentDashboardData) return;
    
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send-btn");
    
    addChatMessage(question, true);
    
    if (chatInput) chatInput.value = "";
    if (sendBtn) sendBtn.disabled = true;

    // Add typing indicator
    const chatMessages = document.getElementById("chat-messages");
    const typingDiv = document.createElement("div");
    typingDiv.id = "typing-indicator";
    typingDiv.className = "flex justify-start";
    const typingAvatar = document.createElement("div");
    typingAvatar.className = "w-8 h-8 rounded-full bg-primary-fixed text-primary flex items-center justify-center mr-2 flex-shrink-0";
    typingAvatar.innerHTML = '<span class="material-symbols-outlined text-sm">robot_2</span>';
    const typingBubble = document.createElement("div");
    typingBubble.className = "bg-surface-container-low border border-outline-variant px-4 py-2 rounded-2xl rounded-bl-sm flex gap-1";
    typingBubble.innerHTML = `
        <span class="w-2 h-2 bg-on-surface-variant rounded-full animate-bounce" style="animation-delay: 0ms"></span>
        <span class="w-2 h-2 bg-on-surface-variant rounded-full animate-bounce" style="animation-delay: 150ms"></span>
        <span class="w-2 h-2 bg-on-surface-variant rounded-full animate-bounce" style="animation-delay: 300ms"></span>
    `;
    typingDiv.appendChild(typingAvatar);
    typingDiv.appendChild(typingBubble);
    chatMessages.appendChild(typingDiv);
    
    // Scroll the chat messages container to the bottom
    const chatMessagesContainer = document.getElementById("chat-messages-container");
    if (chatMessagesContainer) {
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }
    
    try {
        const response = await fetch(`${AI_API}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question,
                company_symbol: currentCompany,
                fiscal_year: currentDashboardData.current_period?.fiscal_year,
                quarter: currentDashboardData.current_period?.quarter
            })
        });
        
        const result = await response.json();
        // Remove typing indicator
        if (typingDiv.parentNode) {
            typingDiv.parentNode.removeChild(typingDiv);
        }
        addChatMessage(result.answer, false);
    } catch (err) {
        console.error(err);
        // Remove typing indicator
        if (typingDiv.parentNode) {
            typingDiv.parentNode.removeChild(typingDiv);
        }
        addChatMessage("Sorry, I couldn't connect to the server.", false);
    } finally {
        if (sendBtn) sendBtn.disabled = false;
    }
}

function initChat() {
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send-btn");
    const exampleBtns = document.querySelectorAll(".example-question");
    const floatingChatBtn = document.getElementById("floating-chat-btn");
    const closeChatBtn = document.getElementById("close-chat-btn");
    
    if (floatingChatBtn) {
        floatingChatBtn.addEventListener("click", toggleChatWindow);
    }
    
    if (closeChatBtn) {
        closeChatBtn.addEventListener("click", closeChatWindow);
    }
    
    if (sendBtn) {
        sendBtn.addEventListener("click", () => {
            if (chatInput) {
                sendMessage(chatInput.value);
            }
        });
    }
    
    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                sendMessage(chatInput.value);
            }
        });
    }
    
    exampleBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const question = btn.getAttribute("data-question");
            if (question) {
                sendMessage(question);
            }
        });
    });
}
