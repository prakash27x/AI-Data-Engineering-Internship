// =====================================
// CONFIG
// =====================================

const API = "http://127.0.0.1:8000/dashboard";

let currentCompany = "BUNGAL";
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

async function loadDashboard(symbol = currentCompany) {

    try {

        const response =
            await fetch(`${API}/${symbol}`);

        const data = await response.json();

        currentCompany = symbol;

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

                    }

                }

            }

        }

    );

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

});