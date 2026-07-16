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


// =====================================
// LOAD DASHBOARD
// =====================================

async function loadDashboard(symbol = currentCompany, period = null) {

    try {

        let url = `${API}/${symbol}`;

        if (period && period.fiscal_year && period.quarter) {
            url += `?fiscal_year=${encodeURIComponent(period.fiscal_year)}`
                 + `&quarter=${encodeURIComponent(period.quarter)}`;
        }

        const response =
            await fetch(url);

        const data = await response.json();
        
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

        drawRevenueChart(data.revenue_trend);

        drawProfitChart(data.net_profit_trend);

        // Update AI Report Period
        const periodEl = document.getElementById("ai-report-period");
        if(periodEl) {
            periodEl.innerText = `FY${data.company.fiscal_year} ${data.company.quarter} Report`;
        }

        // Populate company quarter selector
        populateQuarterSelect(data.available_periods, data.current_period);

        // Update AI Insights
        updateAIInsights(data.ai_insights);

        // Trigger Auto AI Insight (show loading and then reveal)
        triggerAutoAIInsight();

    }

    catch (err) {

        console.error(err);

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

                    backgroundColor: "#47607e",

                    borderRadius: 8

                }]

            },

            options: {

                plugins: {

                    legend: {

                        display: false

                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                // Mock AI insight per bar hover
                                return "\n✨ AI: Revenue is strongly correlated with increased generation capacity this quarter.";
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

                    tension: .4

                }]

            },

            options: {

                plugins: {

                    legend: {

                        display: false

                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                // Mock AI insight per point hover
                                return "\n✨ AI: Profit margin squeezed by rising finance costs in this period.";
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

    const contentArea = document.getElementById("ai-content-area");
    if (!contentArea) return;

    // Update Score
    const scoreEl = contentArea.querySelector("p.text-3xl");
    if (scoreEl) {
        scoreEl.innerHTML = `${insights.score || 0}<span class="text-sm text-on-surface-variant font-normal">/100</span>`;
    }

    // Update Growth Score
    const growthScoreEl = contentArea.querySelector('span.w-20');
    if (growthScoreEl && insights.growth_score !== undefined) {
        const growthBar = growthScoreEl.nextElementSibling;
        const growthValEl = growthBar.nextElementSibling;
        if (growthBar) {
            const innerBar = growthBar.querySelector('div');
            if (innerBar) {
                innerBar.style.width = `${insights.growth_score}%`;
            }
        }
        if (growthValEl) {
            growthValEl.textContent = insights.growth_score;
        }
    }

    // Update other scores
    const scoreItems = contentArea.querySelectorAll('.space-y-xs > div');
    const scoreKeys = ['growth_score', 'profitability_score', 'liquidity_score', 'stability_score', 'risk_score'];
    const colors = ['bg-green-500', 'bg-yellow-500', 'bg-blue-500', 'bg-blue-400', 'bg-red-500'];

    scoreItems.forEach((item, index) => {
        if (index < scoreKeys.length && insights[scoreKeys[index]] !== undefined) {
            const barEl = item.querySelector('.h-full');
            const valEl = item.querySelector('span.w-6');
            if (barEl) {
                // Reset color classes and apply correct one
                colors.forEach(c => barEl.classList.remove(c));
                barEl.classList.add(colors[index]);
                barEl.style.width = `${insights[scoreKeys[index]]}%`;
            }
            if (valEl) {
                valEl.textContent = insights[scoreKeys[index]];
            }
        }
    });

    // Update Executive Summary
    const summaryDetails = contentArea.querySelectorAll('details')[0];
    if (summaryDetails && insights.summary && Array.isArray(insights.summary)) {
        const summaryUl = summaryDetails.querySelector('ul');
        if (summaryUl) {
            summaryUl.innerHTML = insights.summary.map(item => `<li>${item}</li>`).join('');
        }
    }

    // Update Risks
    const risksDetails = contentArea.querySelectorAll('details')[1];
    if (risksDetails && insights.risks && Array.isArray(insights.risks)) {
        const risksUl = risksDetails.querySelector('ul');
        if (risksUl) {
            risksUl.innerHTML = insights.risks.map(item => `<li>${item}</li>`).join('');
        }
    }
}

function triggerAutoAIInsight() {
    const overlay = document.getElementById("ai-loading-overlay");
    const content = document.getElementById("ai-content-area");
    
    if (!overlay || !content) return;

    // Show loading overlay
    content.classList.add("opacity-0");
    content.classList.remove("transition-opacity", "duration-500");
    overlay.classList.remove("hidden");
    overlay.classList.add("flex");

    // Mock AI processing delay
    setTimeout(() => {
        overlay.classList.add("hidden");
        overlay.classList.remove("flex");
        
        content.classList.remove("opacity-0");
        content.classList.add("transition-opacity", "duration-500");
    }, 1500);
}

function addChatMessage(text, isUser = false) {
    const chatMessages = document.getElementById("chat-messages");
    if (!chatMessages) return;
    
    const messageDiv = document.createElement("div");
    messageDiv.className = `text-xs ${isUser ? "text-right" : ""}`;
    
    const bubble = document.createElement("div");
    bubble.className = isUser 
        ? "inline-block bg-primary text-on-primary px-3 py-1.5 rounded-lg" 
        : "inline-block bg-surface-container-low border border-outline-variant px-3 py-1.5 rounded-lg";
    bubble.textContent = text;
    
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(question) {
    if (!question.trim() || !currentDashboardData) return;
    
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send-btn");
    
    addChatMessage(question, true);
    
    if (chatInput) chatInput.value = "";
    if (sendBtn) sendBtn.disabled = true;
    
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
        addChatMessage(result.answer, false);
    } catch (err) {
        console.error(err);
        addChatMessage("Sorry, I couldn't connect to the server.", false);
    } finally {
        if (sendBtn) sendBtn.disabled = false;
    }
}

function initChat() {
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("chat-send-btn");
    const exampleBtns = document.querySelectorAll(".example-question");
    
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
